import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/realestate")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
# Get database defined in URI, or fallback to 'realestate'
try:
    db = client.get_default_database()
    if db is None:
        db = client["realestate"]
except Exception:
    db = client["realestate"]

def get_db():
    return db


def ensure_indexes():
    db.users.create_index("email", unique=True)
    db.properties.create_index([("approvalStatus", 1), ("createdAt", -1)])
    db.properties.create_index("seller")
    db.inquiries.create_index([("seller", 1), ("createdAt", -1)])
