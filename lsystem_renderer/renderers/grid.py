"""
Grid/tiled batch renderer for the L-System Renderer.

Renders multiple presets or iterations as a grid of images
in a single SVG, useful for galleries and comparison views.
"""

from __future__ import annotations

import logging
import math
import os
from typing import Dict, List, Optional, Tuple

from ..core.types import LSystemDefinition, Segment
from ..core.engine import LSystemEngine
from ..core.interpreter import TurtleInterpreter
from ..core.color_postprocessor import ColorPostProcessor
from ..core.presets import PRESETS
from ..renderers.svg import SVGRenderer
from ..utils.colors import _escape_xml

logger = logging.getLogger(__name__)


class GridRenderer:
    """Renders multiple L-systems as a tiled grid in a single SVG.

    Useful for creating comparison galleries and preset showcase images.
    """

    def __init__(
        self,
        cell_width: int = 300,
        cell_height: int = 300,
        columns: int = 4,
        padding: int = 10,
        title: str = "L-System Gallery",
        background: str = "#ffffff",
    ):
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.columns = columns
        self.padding = padding
        self.title = title
        self.background = background

    def render_grid(
        self,
        definitions: Dict[str, LSystemDefinition],
        output_path: str,
        iterations: int = 2,
        seed: Optional[int] = None,
    ) -> str:
        """Render multiple L-systems as a grid in a single SVG.

        Args:
            definitions: Dict mapping names to LSystemDefinition instances.
            output_path: Path to write the output SVG.
            iterations: Number of iterations for each L-system.
            seed: Random seed for stochastic L-systems.

        Returns:
            Path to the output file.
        """
        import random
        rng = random.Random(seed)

        names = list(definitions.keys())
        count = len(names)
        cols = min(self.columns, count)
        rows = math.ceil(count / cols)

        total_width = cols * (self.cell_width + self.padding) + self.padding
        total_height = rows * (self.cell_height + 30 + self.padding) + self.padding + 40

        lines: List[str] = []
        lines.append('<?xml version="1.0" encoding="UTF-8"?>')
        lines.append(
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{total_width}" height="{total_height}" '
            f'viewBox="0 0 {total_width} {total_height}">'
        )
        lines.append(f"<title>{_escape_xml(self.title)}</title>")
        lines.append(
            f'<rect width="{total_width}" height="{total_height}" '
            f'fill="{self.background}"/>'
        )

        # Title
        lines.append(
            f'<text x="{total_width // 2}" y="30" '
            f'text-anchor="middle" font-size="18" font-family="sans-serif" '
            f'fill="#333">{_escape_xml(self.title)}</text>'
        )

        for idx, name in enumerate(names):
            col = idx % cols
            row = idx // cols
            definition = definitions[name]

            x_offset = col * (self.cell_width + self.padding) + self.padding
            y_offset = row * (self.cell_height + 30 + self.padding) + 50

            # Render L-system
            try:
                engine = LSystemEngine(definition, seed=rng.randint(0, 2**31))
                lstring = engine.iterate(iterations)
                interpreter = TurtleInterpreter(
                    angle=definition.angle,
                    step_size=definition.step_size,
                    line_width=definition.line_width,
                    colors=definition.colors,
                    perturbation=definition.perturbation,
                    step_perturbation=definition.step_perturbation,
                    seed=rng.randint(0, 2**31),
                )
                segments = interpreter.interpret(lstring)
                segments = ColorPostProcessor.apply(
                    segments,
                    color_mode=definition.color_mode,
                    colors=definition.colors,
                    gradient=definition.gradient,
                )
            except Exception as e:
                logger.warning("Failed to render '%s' for grid: %s", name, e)
                segments = []

            # Draw cell background
            lines.append(
                f'<rect x="{x_offset}" y="{y_offset}" '
                f'width="{self.cell_width}" height="{self.cell_height}" '
                f'fill="#fafafa" stroke="#ddd" stroke-width="1" rx="4"/>'
            )

            # Label
            label_y = y_offset + self.cell_height + 15
            lines.append(
                f'<text x="{x_offset + self.cell_width // 2}" y="{label_y}" '
                f'text-anchor="middle" font-size="11" font-family="sans-serif" '
                f'fill="#555">{_escape_xml(definition.name)}</text>'
            )

            # Render segments within cell
            if segments:
                min_x, min_y, max_x, max_y = self._compute_bounds(segments)
                data_w = max_x - min_x or 1.0
                data_h = max_y - min_y or 1.0
                cell_margin = 5.0
                avail_w = self.cell_width - 2 * cell_margin
                avail_h = self.cell_height - 2 * cell_margin
                scale = min(avail_w / data_w, avail_h / data_h)
                off_x = x_offset + cell_margin + (avail_w - data_w * scale) / 2
                off_y = y_offset + cell_margin + (avail_h - data_h * scale) / 2

                # Clip to cell
                lines.append(
                    f'<clipPath id="cell-{idx}"><rect x="{x_offset}" y="{y_offset}" '
                    f'width="{self.cell_width}" height="{self.cell_height}"/></clipPath>'
                )
                lines.append(f'<g clip-path="url(#cell-{idx})">')

                for seg in segments:
                    sx1 = (seg.x1 - min_x) * scale + off_x
                    sy1 = total_height - ((seg.y1 - min_y) * scale + (y_offset + cell_margin - y_offset) - y_offset)
                    # Recalculate: flip Y within cell
                    sy1 = y_offset + cell_margin + (avail_h - (seg.y1 - min_y) * scale)
                    sx2 = (seg.x2 - min_x) * scale + off_x
                    sy2 = y_offset + cell_margin + (avail_h - (seg.y2 - min_y) * scale)

                    lines.append(
                        f'<line x1="{sx1:.2f}" y1="{sy1:.2f}" '
                        f'x2="{sx2:.2f}" y2="{sy2:.2f}" '
                        f'stroke="{seg.color}" stroke-width="{max(0.5, seg.width * scale / 20):.2f}" '
                        f'stroke-linecap="round"/>'
                    )
                lines.append('</g>')

        lines.append("</svg>")

        with open(output_path, "w") as f:
            f.write("\n".join(lines))

        logger.info("Rendered grid of %d L-systems to %s", count, output_path)
        return output_path

    @staticmethod
    def _compute_bounds(segments: List[Segment]) -> Tuple[float, float, float, float]:
        if not segments:
            return (0, 0, 100, 100)
        xs = []
        ys = []
        for seg in segments:
            xs.extend([seg.x1, seg.x2])
            ys.extend([seg.y1, seg.y2])
        return min(xs), min(ys), max(xs), max(ys)

    def render_all_presets_grid(
        self,
        output_path: str,
        iterations: int = 2,
        seed: Optional[int] = None,
    ) -> str:
        """Render all built-in presets as a grid.

        Args:
            output_path: Path to write the output SVG.
            iterations: Number of iterations per preset.
            seed: Random seed for stochastic L-systems.

        Returns:
            Path to the output file.
        """
        import copy
        definitions = {name: copy.deepcopy(defn) for name, defn in PRESETS.items()}
        return self.render_grid(definitions, output_path, iterations=iterations, seed=seed)