"""Configure the MongoDB connection and collections."""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI is missing from .env")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
client.admin.command("ping")

db = client[os.getenv("MONGO_DB", "sonder")]

photos_collection = db["photos"]
colors_collection = db["colors"]
