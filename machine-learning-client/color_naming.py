"""Assign human-readable names to detected HEX colors."""

COLOR_NAMES = {
    "Black": "#000000",
    "White": "#FFFFFF",
    "Off-white": "#F0ECEE",
    "Gray": "#808080",
    "Red": "#FF0000",
    "Dark Red": "#8B0000",
    "Burgundy": "#650D31",
    "Orange": "#FFA500",
    "Yellow": "#FFFF00",
    "Green": "#008000",
    "Lime": "#00FF00",
    "Olive": "#808000",
    "Blue": "#0000FF",
    "Deep Blue": "#20568B",
    "Sky Blue": "#87CEEB",
    "Cyan": "#00BCD4",
    "Purple": "#800080",
    "Magenta": "#D9277C",
    "Pink": "#FFC0CB",
    "Brown": "#8B4513",
    "Beige": "#F5F5DC",
}


def hex_to_rgb(hex_code):
    """Convert a six-digit HEX color to an RGB tuple."""
    if not isinstance(hex_code, str):
        raise ValueError("Invalid HEX color")

    if len(hex_code) != 7 or not hex_code.startswith("#"):
        raise ValueError("Invalid HEX color")

    try:
        return tuple(int(hex_code[i : i + 2], 16) for i in (1, 3, 5))
    except ValueError as error:
        raise ValueError("Invalid HEX color") from error


def get_color_name(hex_code):
    """Find the nearest color name using RGB distance."""
    target = hex_to_rgb(hex_code)

    closest_name = None
    smallest_distance = float("inf")

    for name, reference_hex in COLOR_NAMES.items():
        reference = hex_to_rgb(reference_hex)

        distance = sum((target[i] - reference[i]) ** 2 for i in range(3))

        if distance < smallest_distance:
            smallest_distance = distance
            closest_name = name

    return closest_name


def name_colors(colors):
    """Add a color name to each detected color result."""
    results = []

    for color in colors:
        results.append(
            {
                **color,
                "name": get_color_name(color["hex"]),
            }
        )

    return results
