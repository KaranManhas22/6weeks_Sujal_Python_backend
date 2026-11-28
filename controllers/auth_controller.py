from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError
from config.db import get_db
from models.user_model import UserRegister, UserLogin, hash_password, verify_password
from utils.generate_token import generate_token

db = get_db()

def register_user_controller(user_data: UserRegister):
    email = user_data.email.lower()
    
    # Check if user already exists
    user_exists = db.users.find_one({"email": email})
    if user_exists:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )
    
    # Hash password and save user
    hashed_pwd = hash_password(user_data.password)
    user_doc = {
        "name": user_data.name,
        "email": email,
        "password": hashed_pwd,
        "role": user_data.role if user_data.role else "Buyer",
        "avatar": "",
        "phone": "",
        "savedProperties": []
    }
    
    try:
        result = db.users.insert_one(user_doc)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="User already exists") from None
    user_id = str(result.inserted_id)
    
    return {
        "_id": user_id,
        "name": user_doc["name"],
        "email": user_doc["email"],
        "role": user_doc["role"],
        "token": generate_token(user_id)
    }

def login_user_controller(login_data: UserLogin):
    email = login_data.email.lower()
    
    user = db.users.find_one({"email": email})
    if user and verify_password(login_data.password, user.get("password", "")):
        user_id = str(user["_id"])
        return {
            "_id": user_id,
            "name": user["name"],
            "email": user["email"],
            "role": user.get("role", "Buyer"),
            "token": generate_token(user_id)
        }
    raise HTTPException(status_code=401, detail="Invalid email or password")

def get_user_profile_controller(current_user: dict):
    return {
        "_id": current_user["_id"],
        "name": current_user.get("name", ""),
        "email": current_user.get("email", ""),
        "role": current_user.get("role", "Buyer"),
        "avatar": current_user.get("avatar", ""),
        "phone": current_user.get("phone", "")
    }
