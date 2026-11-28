import os
import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

def get_jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET must be set in the environment")
    return secret

def generate_token(user_id: str) -> str:
    payload = {
        "userId": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(days=30)
    }
    return jwt.encode(payload, get_jwt_secret(), algorithm="HS256")
