"""Manage photo storage and retrieval in MongoDB."""

from datetime import datetime

from bson import ObjectId
from bson.binary import Binary

from database import photos_collection


def get_photo(image_id):
    """Retrieve a photo by its ID."""
    if not ObjectId.is_valid(image_id):
        return None
    photo = photos_collection.find_one({"_id": ObjectId(image_id)})
    return photo


def save_photo(image):
    """Save a photo to MongoDB."""
    image_data = image.read()
    photo = {
        "filename": image.filename,
        "image": Binary(image_data),
        "file_type": image.mimetype,
        "date": datetime.now(),
    }
    x = photos_collection.insert_one(photo)
    return str(x.inserted_id)


def delete_photo(image_id):
    """Delete a photo from MongoDB by its ID."""
    if not ObjectId.is_valid(image_id):
        return None
    result = photos_collection.delete_one({"_id": ObjectId(image_id)})
    return result.deleted_count > 0
