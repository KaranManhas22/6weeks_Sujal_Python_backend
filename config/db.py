import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/realestate")

client = MongoClient(MONGO_URI)
# Get database defined in URI, or fallback to 'realestate'
try:
    db = client.get_default_database()
    if db is None:
        db = client["realestate"]
except Exception:
    db = client["realestate"]

def get_db():
    return db
