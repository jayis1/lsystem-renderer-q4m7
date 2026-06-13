"""
Color post-processor for L-system segments.

Applies various color modes to segments after turtle interpretation.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

from .types import Segment
from ..utils.colors import lerp_color, rainbow_color

logger = logging.getLogger(__name__)


class ColorPostProcessor:
    """Applies color modes to segments after interpretation."""

    @staticmethod
    def apply(
        segments: List[Segment],
        color_mode: str = "depth",
        colors: Optional[Dict[int, str]] = None,
        gradient: Optional[Tuple[str, str]] = None,
    ) -> List[Segment]:
        """Apply the specified color mode to all segments.

        Args:
            segments: List of Segment objects to color.
            color_mode: One of 'depth', 'position', 'segment_index', 'single'.
            colors: Optional depth-to-color mapping.
            gradient: Optional (start_color, end_color) for gradient modes.

        Returns:
            The same list with colors applied.
        """
        if not segments:
            return segments

        colors = colors or {}

        if color_mode == "single":
            base_color = colors.get(0, "#2d5016")
            for seg in segments:
                seg.color = base_color

        elif color_mode == "depth":
            for seg in segments:
                seg.color = colors.get(seg.depth, seg.color)

        elif color_mode == "position":
            if gradient:
                # Color based on normalized Y position (bottom=start, top=end)
                ys = []
                for seg in segments:
                    ys.extend([seg.y1, seg.y2])
                if ys:
                    min_y = min(ys)
                    max_y = max(ys)
                    y_range = max_y - min_y if max_y != min_y else 1.0
                    for seg in segments:
                        mid_y = (seg.y1 + seg.y2) / 2
                        t = (mid_y - min_y) / y_range
                        seg.color = lerp_color(gradient[0], gradient[1], t)
            else:
                # Default: use depth colors
                for seg in segments:
                    seg.color = colors.get(seg.depth, seg.color)

        elif color_mode == "segment_index":
            total = len(segments)
            for seg in segments:
                seg.color = rainbow_color(seg.segment_index, total)

        else:
            logger.warning("Unknown color mode '%s', leaving colors unchanged", color_mode)

        return segments