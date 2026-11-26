"""Unit tests for MongoDB image processing."""

import json
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from bson import ObjectId
from PIL import Image

from process_image import get_named_results, main, process_image


def create_image_bytes():
    """Create a red PNG image for testing."""
    image = Image.new("RGB", (50, 50), (255, 0, 0))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_process_image_success():
    """Verify image analysis and database storage."""
    image_id = str(ObjectId())

    photos_collection = MagicMock()
    colors_collection = MagicMock()

    photos_collection.find_one.return_value = {
        "_id": ObjectId(image_id),
        "image": create_image_bytes(),
    }

    result = process_image(
        image_id,
        photos_collection,
        colors_collection,
    )

    assert result["image_id"] == image_id
    assert result["colors"][0]["hex"] == "#FF0000"
    assert result["colors"][0]["percentage"] == 100.0
    assert result["colors"][0]["name"] == "Red"

    photos_collection.find_one.assert_called_once_with({"_id": ObjectId(image_id)})

    colors_collection.insert_one.assert_called_once()

    saved_document = colors_collection.insert_one.call_args.args[0]

    assert saved_document["image_id"] == ObjectId(image_id)
    assert saved_document["colors"] == [{"hex": "#FF0000", "percentage": 100.0}]
    assert "date" in saved_document


def test_invalid_image_id():
    """Reject invalid MongoDB image IDs."""
    photos_collection = MagicMock()
    colors_collection = MagicMock()

    with pytest.raises(ValueError, match="Invalid image ID"):
        process_image(
            "invalid-id",
            photos_collection,
            colors_collection,
        )

    photos_collection.find_one.assert_not_called()
    colors_collection.insert_one.assert_not_called()


def test_missing_photo():
    """Handle photos that do not exist in MongoDB."""
    image_id = str(ObjectId())

    photos_collection = MagicMock()
    colors_collection = MagicMock()

    photos_collection.find_one.return_value = None

    with pytest.raises(ValueError, match="Photo not found"):
        process_image(
            image_id,
            photos_collection,
            colors_collection,
        )

    colors_collection.insert_one.assert_not_called()


def test_empty_image():
    """Reject MongoDB records with empty image data."""
    image_id = str(ObjectId())

    photos_collection = MagicMock()
    colors_collection = MagicMock()

    photos_collection.find_one.return_value = {"image": b""}

    with pytest.raises(ValueError, match="no image data"):
        process_image(
            image_id,
            photos_collection,
            colors_collection,
        )

    colors_collection.insert_one.assert_not_called()


def test_main_success(monkeypatch, capsys):
    """Verify the command-line entry point processes a photo."""
    image_id = str(ObjectId())

    monkeypatch.setenv("MONGO_URI", "mongodb://localhost:27017")
    monkeypatch.setenv("MONGO_DB", "sonder")
    monkeypatch.setattr("sys.argv", ["process_image.py", image_id])

    with patch("process_image.MongoClient") as mock_client:
        database = MagicMock()
        database["photos"].find_one.return_value = {"image": create_image_bytes()}

        connection = mock_client.return_value.__enter__.return_value
        connection.__getitem__.return_value = database

        main()

        database["colors"].insert_one.assert_called_once()

    output = json.loads(capsys.readouterr().out)

    assert output["image_id"] == image_id
    assert output["colors"][0]["name"] == "Red"


def test_main_missing_uri(monkeypatch):
    """Verify MongoDB configuration is required."""
    monkeypatch.delenv("MONGO_URI", raising=False)
    monkeypatch.setattr("sys.argv", ["process_image.py", str(ObjectId())])

    with pytest.raises(SystemExit):
        main()


def test_get_named_results_success():
    """Retrieve saved colors and add names."""
    image_id = str(ObjectId())
    colors_collection = MagicMock()

    colors_collection.find_one.return_value = {
        "image_id": ObjectId(image_id),
        "colors": [
            {"hex": "#FF0000", "percentage": 70.0},
            {"hex": "#0000FF", "percentage": 30.0},
        ],
    }

    result = get_named_results(image_id, colors_collection)

    assert result["image_id"] == image_id
    assert result["colors"][0]["name"] == "Red"
    assert result["colors"][1]["name"] == "Blue"
    assert result["colors"][0]["percentage"] == 70.0

    colors_collection.find_one.assert_called_once_with(
        {"image_id": ObjectId(image_id)},
        sort=[("date", -1)],
    )


def test_get_named_results_missing():
    """Return None if no color analysis exists."""
    image_id = str(ObjectId())
    colors_collection = MagicMock()
    colors_collection.find_one.return_value = None

    result = get_named_results(image_id, colors_collection)

    assert result is None


def test_get_named_results_invalid_id():
    """Reject malformed image IDs."""
    colors_collection = MagicMock()

    with pytest.raises(ValueError, match="Invalid image ID"):
        get_named_results("invalid-id", colors_collection)

    colors_collection.find_one.assert_not_called()
