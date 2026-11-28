from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Literal
import bcrypt

def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(10)
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

class UserRegister(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=8)
    role: Literal["Buyer", "Seller"] = "Buyer"

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, password: str) -> str:
        if len(password.encode("utf-8")) > 72:
            raise ValueError("password must be at most 72 bytes")
        return password

class UserLogin(BaseModel):
    email: EmailStr
    password: str
