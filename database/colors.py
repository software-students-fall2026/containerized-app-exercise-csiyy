"""Store and read dominant-color analysis results in MongoDB.

Each document in the ``colors`` collection holds the output of the
machine learning client's ``detect_colors()`` for one photo:

    {
        "image_id": ObjectId,   # _id of the photo in the photos collection
        "colors": [{"hex": "#FF0000", "percentage": 70.0}, ...],
        "date": datetime
    }
"""

from datetime import datetime

from bson import ObjectId

from database import colors_collection


def _valid_color(color):
    """Return True if a color entry has a valid hex code and percentage."""
    if not isinstance(color, dict):
        return False
    hex_code = color.get("hex")
    percentage = color.get("percentage")
    if not isinstance(hex_code, str) or len(hex_code) != 7 or hex_code[0] != "#":
        return False
    try:
        int(hex_code[1:], 16)
    except ValueError:
        return False
    if isinstance(percentage, bool) or not isinstance(percentage, (int, float)):
        return False
    return 0 <= percentage <= 100


def save_colors(image_id, colors):
    """Save the detected colors for a photo.

    Returns the new document's id as a string, or None if the image id
    or the color list is invalid.
    """
    if not ObjectId.is_valid(image_id):
        return None
    if not isinstance(colors, list) or not colors:
        return None
    if not all(_valid_color(color) for color in colors):
        return None

    document = {
        "image_id": ObjectId(image_id),
        "colors": [
            {"hex": color["hex"].upper(), "percentage": float(color["percentage"])}
            for color in colors
        ],
        "date": datetime.now(),
    }
    result = colors_collection.insert_one(document)
    return str(result.inserted_id)


def get_colors(image_id):
    """Return the most recent color result for a photo, or None."""
    if not ObjectId.is_valid(image_id):
        return None
    return colors_collection.find_one(
        {"image_id": ObjectId(image_id)}, sort=[("date", -1)]
    )


def get_recent_colors(limit=10):
    """Return up to ``limit`` of the newest color results, newest first."""
    if not isinstance(limit, int) or limit < 1:
        return []
    return list(colors_collection.find().sort("date", -1).limit(limit))


def delete_colors(image_id):
    """Delete every color result for a photo.

    Returns True if anything was deleted, False otherwise.
    """
    if not ObjectId.is_valid(image_id):
        return False
    result = colors_collection.delete_many({"image_id": ObjectId(image_id)})
    return result.deleted_count > 0
