"""Run a color detection experiment on a sample image."""

from color_detection import detect_colors

results = detect_colors("test_images/sample.jpg")

for index, color in enumerate(results, start=1):
    print(f"#{index}: {color['hex']} - " f"{color['percentage']}%")
