"""
Color utility functions for the L-System Renderer.

Provides hex/RGB conversion, linear interpolation, HSL conversion,
and rainbow color generation.
"""

from __future__ import annotations

from typing import Tuple


def _escape_xml(text: str) -> str:
    """Escape XML special characters in a string."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;"))


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert a hex color string to an (R, G, B) tuple.

    Handles both '#RRGGBB' and 'RRGGBB' formats.
    Returns (0, 0, 0) for unparseable input.
    """
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return (0, 0, 0)
    try:
        return (
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16),
        )
    except ValueError:
        return (0, 0, 0)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert an (R, G, B) tuple to a hex color string.

    Values are clamped to [0, 255].
    """
    return f"#{max(0, min(255, r)):02x}{max(0, min(255, g)):02x}{max(0, min(255, b)):02x}"


def lerp_color(color1: str, color2: str, t: float) -> str:
    """Linearly interpolate between two hex colors.

    Args:
        color1: Start color in '#RRGGBB' format.
        color2: End color in '#RRGGBB' format.
        t: Interpolation factor (0.0 = color1, 1.0 = color2).

    Returns:
        Interpolated color in '#RRGGBB' format.
    """
    t = max(0.0, min(1.0, t))
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)
    r = round(r1 + (r2 - r1) * t)
    g = round(g1 + (g2 - g1) * t)
    b = round(b1 + (b2 - b1) * t)
    return rgb_to_hex(r, g, b)


def hsl_to_rgb(h: float, s: float, l: float) -> Tuple[int, int, int]:
    """Convert HSL (h in [0,360], s,l in [0,1]) to RGB (0-255 each)."""
    h = h % 360
    s = max(0.0, min(1.0, s))
    l = max(0.0, min(1.0, l))
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return (round((r + m) * 255), round((g + m) * 255), round((b + m) * 255))


def rgb_to_hsl(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Convert RGB (0-255 each) to HSL (h in [0,360], s,l in [0,1])."""
    r_n, g_n, b_n = r / 255, g / 255, b / 255
    cmax = max(r_n, g_n, b_n)
    cmin = min(r_n, g_n, b_n)
    delta = cmax - cmin

    # Lightness
    l = (cmax + cmin) / 2

    if delta == 0:
        h = 0.0
        s = 0.0
    else:
        # Saturation
        s = delta / (1 - abs(2 * l - 1)) if (1 - abs(2 * l - 1)) != 0 else 0.0

        # Hue
        if cmax == r_n:
            h = 60 * (((g_n - b_n) / delta) % 6)
        elif cmax == g_n:
            h = 60 * (((b_n - r_n) / delta) + 2)
        else:
            h = 60 * (((r_n - g_n) / delta) + 4)

    return (h % 360, s, l)


def rainbow_color(index: int, total: int) -> str:
    """Generate a rainbow color for a segment index."""
    if total <= 0:
        return "#ffffff"
    hue = (index / total) * 360
    r, g, b = hsl_to_rgb(hue, 0.85, 0.55)
    return rgb_to_hex(r, g, b)


def complementary_color(hex_color: str) -> str:
    """Return the complementary color of a hex color."""
    r, g, b = hex_to_rgb(hex_color)
    return rgb_to_hex(255 - r, 255 - g, 255 - b)


def blend_colors(colors: list[str], t: float) -> str:
    """Blend multiple colors at position t (0.0 to 1.0) along the list."""
    if not colors:
        return "#000000"
    if len(colors) == 1:
        return colors[0]
    t = max(0.0, min(1.0, t))
    segment = t * (len(colors) - 1)
    idx = int(segment)
    frac = segment - idx
    if idx >= len(colors) - 1:
        return colors[-1]
    return lerp_color(colors[idx], colors[idx + 1], frac)