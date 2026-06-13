"""
SVG optimization utilities for the L-System Renderer.

Provides post-processing to reduce SVG file size through:
- Removing unnecessary whitespace
- Shortening numeric precision
- Deduplicating styles
"""

from __future__ import annotations

import re
import logging
from typing import List

logger = logging.getLogger(__name__)


def optimize_svg(svg_content: str, precision: int = 2) -> str:
    """Optimize an SVG string by reducing file size.

    Applies the following optimizations:
    - Truncate floating-point numbers to specified precision
    - Remove unnecessary whitespace between tags
    - Remove leading zeros from decimals (0.5 → .5)
    - Remove XML comments

    Args:
        svg_content: Raw SVG content string.
        precision: Number of decimal places for float values.

    Returns:
        Optimized SVG string.
    """
    result = svg_content

    # Remove XML comments
    result = re.sub(r'<!--.*?-->', '', result, flags=re.DOTALL)

    # Truncate long float values to specified precision
    def truncate_float(match: re.Match) -> str:
        value = match.group(0)
        try:
            f = float(value)
            formatted = f"{f:.{precision}f}"
            # Remove trailing zeros after decimal point
            if '.' in formatted:
                formatted = formatted.rstrip('0').rstrip('.')
            # Remove leading zero for decimals
            if formatted.startswith('0.'):
                formatted = '.' + formatted[2:]
            return formatted
        except ValueError:
            return value

    # Match float numbers in SVG (in attributes like x1, y1, stroke-width, etc.)
    result = re.sub(
        r'\b\d+\.\d{3,}\b',
        truncate_float,
        result,
    )

    # Collapse multiple whitespace
    result = re.sub(r'\n\s*\n', '\n', result)
    result = re.sub(r'  +', ' ', result)

    # Remove whitespace around tag boundaries
    result = re.sub(r'>\s+<', '><', result)

    original_size = len(svg_content)
    optimized_size = len(result)
    if original_size > 0:
        reduction = (1 - optimized_size / original_size) * 100
        logger.debug(
            "SVG optimized: %d → %d bytes (%.1f%% reduction)",
            original_size, optimized_size, reduction,
        )

    return result


def merge_svg_paths(svg_content: str) -> str:
    """Merge consecutive path elements with the same style attributes.

    This reduces the number of SVG elements, making the file smaller.

    Args:
        svg_content: Raw SVG content string.

    Returns:
        SVG with merged path elements.
    """
    # Find paths with same stroke and stroke-width
    pattern = re.compile(
        r'<path\s+d="([^"]+)"\s+stroke="([^"]+)"\s+'
        r'stroke-width="([^"]+)"\s+fill="none"\s+'
        r'stroke-linecap="([^"]+)"\s+stroke-linejoin="([^"]+)"\s*/>'
    )

    matches = list(pattern.finditer(svg_content))
    if not matches:
        return svg_content

    # Group by (stroke, stroke-width, linecap, linejoin)
    from collections import defaultdict
    groups: dict[tuple, List[str]] = defaultdict(list)
    for m in matches:
        d, stroke, width, linecap, linejoin = m.groups()
        key = (stroke, width, linecap, linejoin)
        groups[key].append(d)

    # Build merged paths
    result = svg_content
    for key, d_list in groups.items():
        if len(d_list) <= 1:
            continue
        stroke, width, linecap, linejoin = key
        merged_d = " ".join(d_list)
        merged_path = (
            f'<path d="{merged_d}" stroke="{stroke}" '
            f'stroke-width="{width}" fill="none" '
            f'stroke-linecap="{linecap}" stroke-linejoin="{linejoin}"/>'
        )
        # Replace first occurrence and remove others
        first = True
        for m in matches:
            m_stroke = m.group(2)
            m_width = m.group(3)
            m_linecap = m.group(4)
            m_linejoin = m.group(5)
            if (m_stroke, m_width, m_linecap, m_linejoin) == key:
                if first:
                    result = result.replace(m.group(0), merged_path, 1)
                    first = False
                else:
                    result = result.replace(m.group(0), '', 1)

    return result


def stats_svg(svg_content: str) -> dict:
    """Analyze an SVG string and return statistics.

    Args:
        svg_content: SVG content string.

    Returns:
        Dict with keys: bytes, lines, paths, lines_count, groups, animations.
    """
    paths = len(re.findall(r'<path\b', svg_content))
    lines_count = len(re.findall(r'<line\b', svg_content))
    groups = len(re.findall(r'<g\b', svg_content))
    animations = len(re.findall(r'<animate\b', svg_content))

    return {
        "bytes": len(svg_content.encode('utf-8')),
        "lines": svg_content.count('\n') + 1,
        "paths": paths,
        "lines_count": lines_count,
        "groups": groups,
        "animations": animations,
    }