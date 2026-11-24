"""Unit tests for the colors database functions."""

from datetime import datetime, timedelta

from bson import ObjectId

import colors

SAMPLE = [
    {"hex": "#FF0000", "percentage": 70.0},
    {"hex": "#0000ff", "percentage": 30},
]


def test_save_colors_returns_id_and_stores_document():
    """A valid save returns an id and stores normalized colors."""
    image_id = str(ObjectId())
    color_id = colors.save_colors(image_id, SAMPLE)

    assert ObjectId.is_valid(color_id)
    doc = colors.colors_collection.find_one({"_id": ObjectId(color_id)})
    assert doc["image_id"] == ObjectId(image_id)
    assert doc["colors"][1] == {"hex": "#0000FF", "percentage": 30.0}
    assert isinstance(doc["date"], datetime)


def test_save_colors_rejects_invalid_image_id():
    """An invalid image id is rejected."""
    assert colors.save_colors("not-an-id", SAMPLE) is None


def test_save_colors_rejects_empty_or_non_list():
    """Empty lists and non-lists are rejected."""
    image_id = str(ObjectId())
    assert colors.save_colors(image_id, []) is None
    assert colors.save_colors(image_id, "red") is None


def test_save_colors_rejects_bad_entries():
    """Malformed color entries are rejected and nothing is stored."""
    image_id = str(ObjectId())
    bad_entries = [
        ["#FF0000"],
        [{"hex": "FF0000", "percentage": 50}],
        [{"hex": "#GG0000", "percentage": 50}],
        [{"hex": "#FF0000", "percentage": "50"}],
        [{"hex": "#FF0000", "percentage": True}],
        [{"hex": "#FF0000", "percentage": 150}],
        [{"percentage": 50}],
    ]
    for entry in bad_entries:
        assert colors.save_colors(image_id, entry) is None
    assert colors.colors_collection.count_documents({}) == 0


def test_get_colors_returns_latest():
    """get_colors returns the newest result for a photo."""
    image_id = str(ObjectId())
    old = datetime.now() - timedelta(hours=1)
    colors.colors_collection.insert_one(
        {"image_id": ObjectId(image_id), "colors": [], "date": old}
    )
    colors.save_colors(image_id, SAMPLE)

    doc = colors.get_colors(image_id)
    assert doc["colors"][0]["hex"] == "#FF0000"


def test_get_colors_missing_or_invalid():
    """Unknown or invalid ids return None."""
    assert colors.get_colors(str(ObjectId())) is None
    assert colors.get_colors("bad") is None


def test_get_recent_colors_order_and_limit():
    """Results come back newest first and respect the limit."""
    base = datetime.now()
    for i in range(5):
        colors.colors_collection.insert_one(
            {
                "image_id": ObjectId(),
                "colors": SAMPLE,
                "date": base + timedelta(minutes=i),
            }
        )

    recent = colors.get_recent_colors(limit=3)
    assert len(recent) == 3
    assert recent[0]["date"] > recent[1]["date"] > recent[2]["date"]


def test_get_recent_colors_invalid_limit():
    """A non-positive or non-integer limit returns an empty list."""
    assert not colors.get_recent_colors(limit=0)
    assert not colors.get_recent_colors(limit="5")


def test_delete_colors():
    """Deleting removes every result for that photo only."""
    image_id = str(ObjectId())
    other_id = str(ObjectId())
    colors.save_colors(image_id, SAMPLE)
    colors.save_colors(image_id, SAMPLE)
    colors.save_colors(other_id, SAMPLE)

    assert colors.delete_colors(image_id) is True
    assert colors.get_colors(image_id) is None
    assert colors.get_colors(other_id) is not None


def test_delete_colors_missing_or_invalid():
    """Deleting nothing, or using a bad id, returns False."""
    assert colors.delete_colors(str(ObjectId())) is False
    assert colors.delete_colors("bad") is False
