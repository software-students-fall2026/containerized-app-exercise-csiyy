"""Analyze stored photos and save dominant colors to MongoDB."""

import argparse
import json
import os
from datetime import datetime, timezone

from bson import ObjectId
from pymongo import MongoClient

from color_detection import detect_colors
from color_naming import name_colors


def process_image(image_id, photos_collection, colors_collection):
    """Retrieve a photo, detect its colors, and save the results."""

    if not ObjectId.is_valid(image_id):
        raise ValueError("Invalid image ID")

    photo = photos_collection.find_one({"_id": ObjectId(image_id)})

    if photo is None:
        raise ValueError("Photo not found")

    image_data = photo.get("image")

    if not image_data:
        raise ValueError("Photo contains no image data")

    detected_colors = detect_colors(bytes(image_data))

    document = {
        "image_id": ObjectId(image_id),
        "colors": detected_colors,
        "date": datetime.now(timezone.utc),
    }

    colors_collection.insert_one(document)

    return {
        "image_id": image_id,
        "colors": name_colors(detected_colors),
    }


def get_named_results(image_id, colors_collection):
    """Retrieve saved color results and add human-readable names."""

    if not ObjectId.is_valid(image_id):
        raise ValueError("Invalid image ID")

    document = colors_collection.find_one(
        {"image_id": ObjectId(image_id)},
        sort=[("date", -1)],
    )

    if document is None:
        return None

    return {
        "image_id": image_id,
        "colors": name_colors(document["colors"]),
    }


def main():
    """Process a photo using the configured MongoDB connection."""

    parser = argparse.ArgumentParser(description="Analyze a photo stored in MongoDB.")
    parser.add_argument("image_id", help="MongoDB photo ID")
    args = parser.parse_args()

    mongo_uri = os.getenv("MONGO_URI")

    if not mongo_uri:
        parser.error("MONGO_URI environment variable is required")

    database_name = os.getenv("MONGO_DB", "sonder")

    with MongoClient(mongo_uri, serverSelectionTimeoutMS=5000) as client:
        database = client[database_name]

        result = process_image(
            args.image_id,
            database["photos"],
            database["colors"],
        )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
