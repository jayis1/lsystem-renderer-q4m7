#!/usr/bin/env python3
"""
Example: Animation and Growth Visualization.

This example shows how to create animated SVGs and growth step sequences.
"""

from lsystem_renderer import LSystemRenderer

renderer = LSystemRenderer(seed=42)

# 1. Animated SVG (progressive draw)
print("=== Animated SVG ===")
renderer.render(
    "plant_simple",
    iterations=5,
    output="animated_plant.svg",
    animate=True,
    animation_duration=5.0,
)
print("  → animated_plant.svg (opens in browser to see animation)")

# 2. Growth step sequence
print("=== Growth Steps ===")
steps = renderer.animate_growth(
    "koch_snowflake",
    output_dir="./growth_steps",
    iterations=5,
)
print(f"  Generated {len(steps)} step files in ./growth_steps/")
for i, path in enumerate(steps):
    print(f"    step_{i}.svg")

# 3. Growth animation for fractal tree
print("=== Fractal Tree Growth ===")
steps = renderer.animate_growth(
    "fractal_tree",
    output_dir="./tree_growth",
    iterations=6,
)
print(f"  Generated {len(steps)} step files in ./tree_growth/")

print("\nDone! Open the SVG files in a browser to view animations.")