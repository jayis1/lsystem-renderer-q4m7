"""
PDF rendering backend for the L-System Renderer.

Produces vector PDF output using reportlab (optional dependency).
Falls back gracefully if reportlab is not installed.
"""

from __future__ import annotations

import logging
from typing import List, Optional, Tuple

from ..core.types import Segment
from ..utils.colors import hex_to_rgb

logger = logging.getLogger(__name__)

# Try importing reportlab
try:
    from reportlab.pdfgen import canvas as pdfcanvas
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    logger.debug("reportlab not available; PDF rendering disabled")


class PDFRenderer:
    """Renders segments to a PDF file.

    Requires the reportlab library. Falls back gracefully if unavailable.
    Produces vector-quality PDF output with auto-scaling and centering.
    """

    def __init__(
        self,
        width: int = 800,
        height: int = 800,
        background: str = "#ffffff",
        margin: float = 20.0,
        title: str = "L-System Renderer",
    ):
        self.width = width
        self.height = height
        self.background = background
        self.margin = margin
        self.title = title

    @staticmethod
    def is_available() -> bool:
        """Check if reportlab is available for PDF rendering."""
        return HAS_REPORTLAB

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
        """Render segments to a PDF file.

        Args:
            segments: List of Segment objects to render.
            output_path: Path to write the PDF file.

        Returns:
            Path to the output file.

        Raises:
            ImportError: If reportlab is not installed.
        """
        if not HAS_REPORTLAB:
            raise ImportError(
                "PDF rendering requires reportlab. "
                "Install it with: pip install reportlab"
            )

        c = pdfcanvas.Canvas(output_path, pagesize=(self.width, self.height))
        c.setTitle(self.title)

        # Draw background
        bg_rgb = hex_to_rgb(self.background)
        c.setFillColorRGB(bg_rgb[0] / 255, bg_rgb[1] / 255, bg_rgb[2] / 255)
        c.rect(0, 0, self.width, self.height, fill=True, stroke=False)

        if not segments:
            c.save()
            return output_path

        min_x, min_y, max_x, max_y = self._compute_bounds(segments)
        data_w = max_x - min_x or 1.0
        data_h = max_y - min_y or 1.0

        avail_w = self.width - 2 * self.margin
        avail_h = self.height - 2 * self.margin
        scale = min(avail_w / data_w, avail_h / data_h)

        offset_x = self.margin + (avail_w - data_w * scale) / 2
        offset_y = self.margin + (avail_h - data_h * scale) / 2

        for seg in segments:
            sx1 = (seg.x1 - min_x) * scale + offset_x
            sy1 = self.height - ((seg.y1 - min_y) * scale + offset_y)
            sx2 = (seg.x2 - min_x) * scale + offset_x
            sy2 = self.height - ((seg.y2 - min_y) * scale + offset_y)

            color_rgb = hex_to_rgb(seg.color)
            c.setStrokeColorRGB(color_rgb[0] / 255, color_rgb[1] / 255, color_rgb[2] / 255)
            c.setLineWidth(max(0.5, seg.width * scale / 10))
            c.line(sx1, sy1, sx2, sy2)

        c.save()
        logger.info("Rendered %d segments to PDF: %s", len(segments), output_path)
        return output_path