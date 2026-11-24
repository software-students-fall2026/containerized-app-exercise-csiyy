"""Test setup: replace the real MongoDB connection with an in-memory mock.

database.py connects to MongoDB as soon as it is imported, so a fake
``database`` module is registered before colors.py is imported.
"""

import sys
import types
from pathlib import Path

import mongomock
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_fake_db = mongomock.MongoClient()["test"]
_fake_module = types.ModuleType("database")
_fake_module.photos_collection = _fake_db["photos"]
_fake_module.colors_collection = _fake_db["colors"]
sys.modules["database"] = _fake_module


@pytest.fixture(autouse=True)
def clean_collections():
    """Empty the mock collections before every test."""
    _fake_db["colors"].delete_many({})
    _fake_db["photos"].delete_many({})
    yield
