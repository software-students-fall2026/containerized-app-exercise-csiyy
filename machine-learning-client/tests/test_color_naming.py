"""Tests for automatic color naming."""

import pytest

from color_naming import get_color_name, name_colors


def test_exact_color():
    """Verify naming an exact reference color."""
    assert get_color_name("#FF0000") == "Red"
    assert get_color_name("#000000") == "Black"


def test_approximate_color():
    """Verify naming colors close to reference values."""
    assert get_color_name("#520C2F") == "Burgundy"
    assert get_color_name("#06BCDE") == "Cyan"


def test_name_colors():
    """Verify names are added without changing existing data."""
    colors = [
        {"hex": "#FF0000", "percentage": 70.0},
        {"hex": "#0000FF", "percentage": 30.0},
    ]

    results = name_colors(colors)

    assert results[0]["name"] == "Red"
    assert results[1]["name"] == "Blue"
    assert results[0]["percentage"] == 70.0
    assert "name" not in colors[0]


def test_invalid_hex():
    """Verify malformed HEX values are rejected."""
    with pytest.raises(ValueError):
        get_color_name("not-a-color")
