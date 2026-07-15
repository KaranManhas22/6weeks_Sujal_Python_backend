import math
from fastapi import HTTPException, status
from bson import ObjectId
from config.db import get_db
from models.property_model import PropertyCreate
from datetime import datetime

db = get_db()

def serialize_doc(doc):
    if not doc:
        return doc
    doc["_id"] = str(doc["_id"])
    if "seller" in doc:
        if isinstance(doc["seller"], ObjectId):
            doc["seller"] = str(doc["seller"])
        elif isinstance(doc["seller"], dict) and "_id" in doc["seller"]:
            doc["seller"]["_id"] = str(doc["seller"]["_id"])
    return doc

def get_properties_controller(keyword: str = None, page_number: int = 1):
    page_size = 12
    page = page_number if page_number > 0 else 1
    
    query = {"approvalStatus": "Approved"}
    if keyword:
        query["title"] = {"$regex": keyword, "$options": "i"}
        
    count = db.properties.count_documents(query)
    
    cursor = db.properties.find(query).skip(page_size * (page - 1)).limit(page_size)
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
    if not property_doc:
        raise HTTPException(
            status_code=404,
            detail="Property not found"
        )
        
    # Populate seller fields: name, email, avatar, phone
    seller_id = property_doc.get("seller")
    if seller_id:
        try:
            seller_oid = ObjectId(seller_id) if isinstance(seller_id, str) else seller_id
            seller_doc = db.users.find_one({"_id": seller_oid}, {"name": 1, "email": 1, "avatar": 1, "phone": 1})
            if seller_doc:
                property_doc["seller"] = serialize_doc(seller_doc)
        except Exception:
            pass
            
    return serialize_doc(property_doc)

def create_property_controller(property_data: PropertyCreate, current_user: dict):
    if current_user.get("role") not in ["Seller", "Admin"]:
        raise HTTPException(
            status_code=401,
            detail="Not authorized to create properties"
        )
        
    now = datetime.utcnow()
    
    property_dict = property_data.dict()
    property_dict["seller"] = ObjectId(current_user["_id"])
    property_dict["approvalStatus"] = "Approved" if current_user.get("role") == "Admin" else "Pending"
    property_dict["createdAt"] = now
    property_dict["updatedAt"] = now
    
    result = db.properties.insert_one(property_dict)
    property_dict["_id"] = str(result.inserted_id)
    property_dict["seller"] = str(property_dict["seller"])
    
    return property_dict
