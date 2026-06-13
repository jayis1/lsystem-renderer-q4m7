"""
ASCII rendering backend for the L-System Renderer.

Produces terminal-friendly character-based output with directional characters.
"""

from __future__ import annotations

import logging
from typing import List, Optional

from ..core.types import Segment

logger = logging.getLogger(__name__)


class ASCIIRenderer:
    """Renders segments to ASCII art using a character grid.

    Supports directional characters (|, -, /, \\) for better-looking output.
    """

    CHAR_MAP = {
        (0, 1): "|",
        (0, -1): "|",
        (1, 0): "-",
        (-1, 0): "-",
        (1, 1): "\\",
        (-1, -1): "\\",
        (1, -1): "/",
        (-1, 1): "/",
    }

    def __init__(self, width: int = 80, height: int = 40):
        self.width = width
        self.height = height

    def render(self, segments: List[Segment], output_path: Optional[str] = None) -> str:
        """Render segments to ASCII art string.

        Args:
            segments: List of Segment objects to render.
            output_path: Optional path to write output to file.

        Returns:
            ASCII art string.
        """
        if not segments:
            return ""

        # Compute bounds
        xs = []
        ys = []
        for seg in segments:
            xs.extend([seg.x1, seg.x2])
            ys.extend([seg.y1, seg.y2])

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        data_w = max_x - min_x or 1.0
        data_h = max_y - min_y or 1.0

        # Create grid
        grid = [[" " for _ in range(self.width)] for _ in range(self.height)]

        scale_x = (self.width - 1) / data_w if data_w > 0 else 1
        scale_y = (self.height - 1) / data_h if data_h > 0 else 1
        scale = min(scale_x, scale_y)

        for seg in segments:
            x1 = int((seg.x1 - min_x) * scale)
            y1 = int((seg.y1 - min_y) * scale)
            x2 = int((seg.x2 - min_x) * scale)
            y2 = int((seg.y2 - min_y) * scale)

            # Bresenham-like rasterization
            dx = x2 - x1
            dy = y2 - y1
            steps = max(abs(dx), abs(dy), 1)

            # Determine direction character
            if steps > 0:
                ndx = dx / steps
                ndy = dy / steps
                # Snap to nearest direction
                key = (
                    round(ndx) if abs(ndx) > 0.3 else 0,
                    round(ndy) if abs(ndy) > 0.3 else 0,
                )
                char = self.CHAR_MAP.get(key, "*")
            else:
                char = "*"

            for i in range(steps + 1):
                t = i / steps
                px = int(x1 + dx * t)
                py = int(y1 + dy * t)
                if 0 <= px < self.width and 0 <= py < self.height:
                    grid[py][px] = char

        # Flip grid vertically (y increases upward in math, downward in text)
        lines = ["".join(row) for row in reversed(grid)]
        result = "\n".join(lines)

        if output_path:
            with open(output_path, "w") as f:
                f.write(result)
            logger.info("ASCII art written to %s", output_path)

        return result