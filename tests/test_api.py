import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from bson import ObjectId
from fastapi.testclient import TestClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError

import controllers.auth_controller as auth_controller
import controllers.property_controller as property_controller
import controllers.inquiry_controller as inquiry_controller
import middleware.auth_middleware as auth_middleware
from main import app
from utils.generate_token import generate_token


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.db = SimpleNamespace(users=MagicMock(), properties=MagicMock(), inquiries=MagicMock())
        for module in (auth_controller, property_controller, inquiry_controller, auth_middleware):
            patcher = patch.object(module, "db", self.db)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.client = TestClient(app)
        self.user_id = ObjectId()
        self.headers = {"Authorization": f"Bearer {generate_token(str(self.user_id))}"}

    def test_register_login_and_profile(self):
        self.db.users.find_one.return_value = None
        self.db.users.insert_one.return_value = SimpleNamespace(inserted_id=self.user_id)
        response = self.client.post("/api/auth/register", json={
            "name": "Sam", "email": "SAM@example.com", "password": "securepass", "role": "Seller"
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["email"], "sam@example.com")
        self.assertEqual(self.db.users.insert_one.call_args.args[0]["role"], "Seller")

        from models.user_model import hash_password
        self.db.users.find_one.return_value = {
            "_id": self.user_id, "name": "Sam", "email": "sam@example.com",
            "password": hash_password("securepass"), "role": "Seller"
        }
        response = self.client.post("/api/auth/login", json={
            "email": "SAM@example.com", "password": "securepass"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json())

        response = self.client.get("/api/auth/profile", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("password", response.json())

    def test_rejects_admin_registration_and_duplicate_email(self):
        data = {"name": "Sam", "email": "sam@example.com", "password": "securepass", "role": "Admin"}
        self.assertEqual(self.client.post("/api/auth/register", json=data).status_code, 400)

        data["role"] = "Buyer"
        self.db.users.find_one.return_value = None
        self.db.users.insert_one.side_effect = DuplicateKeyError("duplicate")
        response = self.client.post("/api/auth/register", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "User already exists")

    def test_invalid_token_and_missing_user(self):
        response = self.client.get("/api/auth/profile", headers={"Authorization": "Bearer invalid"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["message"], "Not authorized, token failed")

        self.db.users.find_one.return_value = None
        response = self.client.get("/api/auth/profile", headers=self.headers)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["message"], "User not found")

    def test_property_listing_and_creation(self):
        self.db.properties.count_documents.return_value = 1
        cursor = self.db.properties.find.return_value
        cursor.sort.return_value = cursor
        cursor.skip.return_value = cursor
        cursor.limit.return_value = [{
            "_id": ObjectId(), "title": "A [home]", "seller": self.user_id,
            "savedBy": [ObjectId()]
        }]
        response = self.client.get("/api/properties", params={"keyword": "[home]"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["pages"], 1)
        self.assertIsInstance(response.json()["properties"][0]["savedBy"][0], str)
        self.assertEqual(self.db.properties.count_documents.call_args.args[0]["title"]["$regex"], r"\[home\]")

        self.db.users.find_one.return_value = {
            "_id": self.user_id, "name": "Sam", "role": "Seller"
        }
        self.db.properties.insert_one.return_value = SimpleNamespace(inserted_id=ObjectId())
        response = self.client.post("/api/properties", headers=self.headers, json={
            "title": "A home", "description": "A nice home", "price": 100,
            "address": "1 Main St", "location": {"city": "Austin", "state": "TX"},
            "propertyType": "House", "bedrooms": 2, "bathrooms": 1, "area": 800
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["approvalStatus"], "Pending")
        self.assertIsInstance(response.json()["seller"], str)

    def test_validation_and_database_unavailable(self):
        self.assertEqual(self.client.get("/api/properties?pageNumber=0").status_code, 400)
        self.assertEqual(self.client.get("/api/properties/invalid").status_code, 404)
        self.db.properties.count_documents.side_effect = ConnectionFailure("offline")
        response = self.client.get("/api/properties")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"message": "Database unavailable"})

    def test_seller_listings_and_inquiries(self):
        self.db.users.find_one.return_value = {"_id": self.user_id, "role": "Seller"}
        property_id = ObjectId()
        self.db.properties.find.return_value.sort.return_value = [{
            "_id": property_id, "seller": self.user_id, "approvalStatus": "Pending"
        }]
        response = self.client.get("/api/properties/mine", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["approvalStatus"], "Pending")
        self.db.properties.find.assert_called_with({"seller": self.user_id})

        self.db.inquiries.find.return_value.sort.return_value = [{
            "_id": ObjectId(), "seller": self.user_id, "message": "Interested"
        }]
        response = self.client.get("/api/properties/mine/inquiries", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["message"], "Interested")

    def test_inquiry_requires_approved_property_and_admin_approval(self):
        property_id = ObjectId()
        path = f"/api/properties/{property_id}"
        self.db.properties.find_one.return_value = {
            "_id": property_id, "seller": self.user_id, "approvalStatus": "Approved"
        }
        response = self.client.post(f"{path}/inquiries", json={
            "name": "Buyer", "email": "buyer@example.com", "message": "Interested"
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.db.inquiries.insert_one.call_args.args[0]["seller"], self.user_id)

        self.db.properties.find_one.return_value = None
        self.assertEqual(self.client.post(f"{path}/inquiries", json={
            "name": "Buyer", "email": "buyer@example.com", "message": "Interested"
        }).status_code, 404)
        self.assertEqual(self.client.get(path).status_code, 404)

        self.db.users.find_one.return_value = {"_id": self.user_id, "role": "Seller"}
        self.assertEqual(self.client.patch(f"{path}/approve", headers=self.headers).status_code, 403)
        self.db.users.find_one.return_value = {"_id": self.user_id, "role": "Admin"}
        self.db.properties.update_one.return_value.matched_count = 1
        self.assertEqual(self.client.patch(f"{path}/approve", headers=self.headers).status_code, 200)
        self.assertEqual(self.db.properties.update_one.call_args.args[0]["approvalStatus"], "Pending")


if __name__ == "__main__":
    unittest.main()
