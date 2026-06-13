#!/usr/bin/env python3
"""
Example: Render all presets as a tiled gallery SVG.

This demonstrates the grid renderer for creating comparison
galleries of L-system fractals.
"""

from lsystem_renderer.renderers.grid import GridRenderer
from lsystem_renderer.core.presets import PRESETS
import copy

# Create a gallery of all presets
grid = GridRenderer(
    cell_width=250,
    cell_height=250,
    columns=4,
    padding=10,
    title="L-System Gallery",
    background="#f5f5f5",
)

# Select a subset of interesting presets
subset = {
    "koch_snowflake": copy.deepcopy(PRESETS["koch_snowflake"]),
    "dragon_curve": copy.deepcopy(PRESETS["dragon_curve"]),
    "hilbert_curve": copy.deepcopy(PRESETS["hilbert_curve"]),
    "sierpinski_triangle": copy.deepcopy(PRESETS["sierpinski_triangle"]),
    "plant_simple": copy.deepcopy(PRESETS["plant_simple"]),
    "barnsley_fern": copy.deepcopy(PRESETS["barnsley_fern"]),
    "fibonacci_word": copy.deepcopy(PRESETS["fibonacci_word"]),
    "moore_curve": copy.deepcopy(PRESETS["moore_curve"]),
}

output = grid.render_grid(subset, "gallery_example.svg", iterations=3, seed=42)
print(f"Gallery saved to: {output}")

# Or render ALL presets as a grid
output_all = grid.render_all_presets_grid("all_presets_gallery.svg", iterations=2, seed=42)
print(f"All-presets gallery saved to: {output_all}")