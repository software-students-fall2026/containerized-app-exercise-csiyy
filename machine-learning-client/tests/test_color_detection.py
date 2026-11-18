
import pytest
from PIL import Image
from color_detection import detect_colors


def test_single_color(tmp_path):
    image = Image.new("RGB", (100, 100), (255, 0, 0))
    path = tmp_path / "red.png"
    image.save(path)

    results = detect_colors(path)

    assert len(results) == 1
    assert results[0]["hex"] == "#FF0000"
    assert results[0]["percentage"] == 100.0


def test_two_colors(tmp_path):
    image = Image.new("RGB", (100, 100), (255, 0, 0))
    image.paste((0, 0, 255), (70, 0, 100, 100))

    path = tmp_path / "two_colors.png"
    image.save(path)

    results = detect_colors(path)

    assert len(results) == 2
    assert results[0]["hex"] == "#FF0000"
    assert results[0]["percentage"] == pytest.approx(70)
    assert results[1]["hex"] == "#0000FF"
    assert results[1]["percentage"] == pytest.approx(30)


def test_five_colors(tmp_path):
    image = Image.new("RGB", (100, 100))

    colors = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 0),
        (255, 255, 255)
    ]

    for i, color in enumerate(colors):
        image.paste(color, (i * 20, 0, (i + 1) * 20, 100))

    path = tmp_path / "five_colors.png"
    image.save(path)

    results = detect_colors(path)

    assert len(results) == 5

    for color in results:
        assert color["percentage"] == pytest.approx(20)


def test_invalid_image_path():
    with pytest.raises(FileNotFoundError):
        detect_colors("nonexistent.png")
