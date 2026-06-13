"""
PNG rendering backend for the L-System Renderer.

Produces raster PNG output using the Pillow library.
Falls back to SVG conversion if Pillow is not available.
"""

from __future__ import annotations

import logging
import math
from typing import List, Optional, Tuple

from ..core.types import Segment
from ..utils.colors import hex_to_rgb

logger = logging.getLogger(__name__)

# Try importing PIL/Pillow
try:
    from PIL import Image, ImageDraw
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    logger.debug("Pillow not available; PNG rendering disabled")


class PNGRenderer:
    """Renders segments to a PNG image file.

    Requires the Pillow (PIL) library. Falls back gracefully if unavailable.
    """

    def __init__(
        self,
        width: int = 800,
        height: int = 800,
        background: str = "#ffffff",
        margin: float = 20.0,
        anti_alias: bool = True,
    ):
        self.width = width
        self.height = height
        self.background = background
        self.margin = margin
        self.anti_alias = anti_alias

    @staticmethod
    def is_available() -> bool:
        """Check if Pillow is available for PNG rendering."""
        return HAS_PIL

    def _compute_bounds(self, segments: List[Segment]) -> Tuple[float, float, float, float]:
        """Compute the bounding box of all segments."""
        if not segments:
            return (0, 0, 100, 100)
        xs = []
        ys = []
        for seg in segments:
            xs.extend([seg.x1, seg.x2])
            ys.extend([seg.y1, seg.y2])
        return min(xs), min(ys), max(xs), max(ys)

    def render(
        self,
        segments: List[Segment],
        output_path: str,
    ) -> str:
        """Render segments to a PNG file.

        Args:
            segments: List of Segment objects to render.
            output_path: Path to write the PNG file.

        Returns:
            Path to the output file.

        Raises:
            ImportError: If Pillow is not installed.
        """
        if not HAS_PIL:
            raise ImportError(
                "PNG rendering requires Pillow. "
                "Install it with: pip install Pillow"
            )

        if not segments:
            # Create empty image
            img = Image.new("RGB", (self.width, self.height), hex_to_rgb(self.background))
            img.save(output_path)
            return output_path

        min_x, min_y, max_x, max_y = self._compute_bounds(segments)
        data_w = max_x - min_x or 1.0
        data_h = max_y - min_y or 1.0

        # Scale to fit
        avail_w = self.width - 2 * self.margin
        avail_h = self.height - 2 * self.margin
        scale = min(avail_w / data_w, avail_h / data_h)

        offset_x = self.margin + (avail_w - data_w * scale) / 2
        offset_y = self.margin + (avail_h - data_h * scale) / 2

        # Create image
        img = Image.new("RGB", (self.width, self.height), hex_to_rgb(self.background))
        draw = ImageDraw.Draw(img)

        for seg in segments:
            sx1 = (seg.x1 - min_x) * scale + offset_x
            sy1 = self.height - ((seg.y1 - min_y) * scale + offset_y)
            sx2 = (seg.x2 - min_x) * scale + offset_x
            sy2 = self.height - ((seg.y2 - min_y) * scale + offset_y)

            color = hex_to_rgb(seg.color)
            line_width = max(1, int(seg.width * scale / 10))

            draw.line(
                [(sx1, sy1), (sx2, sy2)],
                fill=color,
                width=line_width,
            )

        img.save(output_path)
        logger.info("Rendered %d segments to PNG: %s", len(segments), output_path)
        return output_path