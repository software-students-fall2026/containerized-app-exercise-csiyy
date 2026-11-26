"""Detect dominant colors in images using K-means clustering."""

from io import BytesIO

from PIL import Image
import numpy as np
from sklearn.cluster import KMeans


def detect_colors(image_path, n_colors=5):
    """Return dominant HEX colors and their pixel percentages."""

    # Load the image and convert it to RGB
    if isinstance(image_path, (bytes, bytearray)):
        image = Image.open(BytesIO(image_path)).convert("RGB")
    else:
        image = Image.open(image_path).convert("RGB")

    # Resize the image for faster processing
    image.thumbnail((200, 200))

    # Convert the image into an array of RGB pixels
    pixels = np.array(image).reshape(-1, 3)

    # Handle images with fewer than five distinct colors
    n_colors = min(n_colors, len(np.unique(pixels, axis=0)))

    # Perform K-Means clustering
    model = KMeans(n_clusters=n_colors, random_state=42, n_init=10)

    model.fit(pixels)

    # Retrieve representative colors
    colors = model.cluster_centers_

    # Count pixels in each cluster
    counts = np.bincount(model.labels_, minlength=n_colors)

    results = []

    for color, count in zip(colors, counts):

        if count == 0:
            continue

        r, g, b = np.rint(color).astype(int)

        hex_code = f"#{r:02X}{g:02X}{b:02X}"

        percentage = count / len(pixels) * 100

        results.append({"hex": hex_code, "percentage": round(percentage, 2)})

    # Sort from most to least dominant
    results.sort(key=lambda color: color["percentage"], reverse=True)

    return results
