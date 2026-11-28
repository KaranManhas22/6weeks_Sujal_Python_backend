import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bson import ObjectId
from config.db import get_db
from utils.generate_token import get_jwt_secret

db = get_db()
security = HTTPBearer(auto_error=False)

def protect(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Not authorized, no token"
        )
    
    token = credentials.credentials
    try:
        decoded = jwt.decode(token, get_jwt_secret(), algorithms=["HS256"])
        user_id = decoded.get("userId")
        if not user_id or not ObjectId.is_valid(user_id):
            raise HTTPException(
                status_code=401,
                detail="Not authorized, token failed"
            )
        
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Not authorized, token failed"
        ) from None

    user = db.users.find_one({"_id": ObjectId(user_id)}, {"password": 0})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    user["_id"] = str(user["_id"])
    return user

def admin(current_user: dict = Depends(protect)):
    if current_user.get("role") != "Admin":
        raise HTTPException(
            status_code=401,
            detail="Not authorized as an admin"
        )
    return current_user
