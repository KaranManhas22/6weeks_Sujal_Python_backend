from datetime import datetime, timezone

from bson import ObjectId
from fastapi import HTTPException

from config.db import get_db
from controllers.property_controller import serialize_doc
from models.inquiry_model import InquiryCreate

db = get_db()


def create_inquiry_controller(property_id: str, inquiry: InquiryCreate):
    if not ObjectId.is_valid(property_id):
        raise HTTPException(status_code=404, detail="Property not found")
    property_doc = db.properties.find_one({"_id": ObjectId(property_id), "approvalStatus": "Approved"})
    if not property_doc:
        raise HTTPException(status_code=404, detail="Property not found")
    inquiry_doc = {
        "property": property_doc["_id"],
        "propertyTitle": property_doc.get("title", "Property"),
        "seller": property_doc["seller"],
        "name": inquiry.name.strip(),
        "email": str(inquiry.email),
        "message": inquiry.message.strip(),
        "createdAt": datetime.now(timezone.utc),
    }
    if not inquiry_doc["name"] or not inquiry_doc["message"]:
        raise HTTPException(status_code=400, detail="Name and message are required")
    db.inquiries.insert_one(inquiry_doc)
    return {"message": "Inquiry sent"}


def get_my_inquiries_controller(current_user: dict):
    if current_user.get("role") not in ("Seller", "Admin"):
        raise HTTPException(status_code=403, detail="Seller access required")
    cursor = db.inquiries.find({"seller": ObjectId(current_user["_id"])}).sort("createdAt", -1)
    return [serialize_doc(doc) for doc in cursor]
