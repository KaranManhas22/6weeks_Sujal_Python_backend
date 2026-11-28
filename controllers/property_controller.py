import math
import re
from fastapi import HTTPException
from bson import ObjectId
from config.db import get_db
from models.property_model import PropertyCreate
from datetime import datetime, timezone

db = get_db()

def serialize_doc(doc):
    if isinstance(doc, ObjectId):
        return str(doc)
    if isinstance(doc, list):
        return [serialize_doc(value) for value in doc]
    if isinstance(doc, dict):
        return {key: serialize_doc(value) for key, value in doc.items()}
    return doc

def get_properties_controller(keyword: str = None, page_number: int = 1):
    page_size = 12
    page = page_number
    
    query = {"approvalStatus": "Approved"}
    if keyword:
        query["title"] = {"$regex": re.escape(keyword), "$options": "i"}
        
    count = db.properties.count_documents(query)
    
    cursor = (db.properties.find(query)
              .sort([("createdAt", -1), ("_id", -1)])
              .skip(page_size * (page - 1))
              .limit(page_size))
    properties = [serialize_doc(doc) for doc in cursor]
    
    pages = math.ceil(count / page_size) if count > 0 else 1
    
    return {
        "properties": properties,
        "page": page,
        "pages": pages
    }

def get_property_by_id_controller(property_id: str):
    try:
        oid = ObjectId(property_id)
    except Exception:
        raise HTTPException(
            status_code=404,
            detail="Property not found"
        )
        
    property_doc = db.properties.find_one({"_id": oid})
    if not property_doc or property_doc.get("approvalStatus") != "Approved":
        raise HTTPException(
            status_code=404,
            detail="Property not found"
        )
        
    # Populate seller fields: name, email, avatar, phone
    seller_id = property_doc.get("seller")
    if seller_id:
        if isinstance(seller_id, ObjectId) or ObjectId.is_valid(seller_id):
            seller_oid = ObjectId(seller_id)
            seller_doc = db.users.find_one({"_id": seller_oid}, {"name": 1, "email": 1, "avatar": 1, "phone": 1})
            if seller_doc:
                property_doc["seller"] = serialize_doc(seller_doc)
            
    return serialize_doc(property_doc)

def get_my_properties_controller(current_user: dict):
    if current_user.get("role") not in ("Seller", "Admin"):
        raise HTTPException(status_code=403, detail="Seller access required")
    cursor = db.properties.find({"seller": ObjectId(current_user["_id"])}).sort("createdAt", -1)
    return [serialize_doc(doc) for doc in cursor]

def get_pending_properties_controller(current_user: dict):
    if current_user.get("role") != "Admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    cursor = db.properties.find({"approvalStatus": "Pending"}).sort("createdAt", -1)
    return [serialize_doc(doc) for doc in cursor]

def approve_property_controller(property_id: str, current_user: dict):
    if current_user.get("role") != "Admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    if not ObjectId.is_valid(property_id):
        raise HTTPException(status_code=404, detail="Property not found")
    result = db.properties.update_one(
        {"_id": ObjectId(property_id), "approvalStatus": "Pending"},
        {"$set": {"approvalStatus": "Approved", "updatedAt": datetime.now(timezone.utc)}},
    )
    if not result.matched_count:
        raise HTTPException(status_code=404, detail="Pending property not found")
    return {"message": "Property approved"}

def create_property_controller(property_data: PropertyCreate, current_user: dict):
    if current_user.get("role") not in ["Seller", "Admin"]:
        raise HTTPException(
            status_code=401,
            detail="Not authorized to create properties"
        )
        
    now = datetime.now(timezone.utc)
    
    property_dict = property_data.model_dump()
    property_dict["seller"] = ObjectId(current_user["_id"])
    property_dict["approvalStatus"] = "Approved" if current_user.get("role") == "Admin" else "Pending"
    property_dict["createdAt"] = now
    property_dict["updatedAt"] = now
    
    result = db.properties.insert_one(property_dict)
    property_dict["_id"] = result.inserted_id
    return serialize_doc(property_dict)
