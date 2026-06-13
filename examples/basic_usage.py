#!/usr/bin/env python3
"""
Example: Basic usage of the L-System Renderer.

This example shows how to render various L-system presets to SVG files.
"""

from lsystem_renderer import LSystemRenderer, LSystemDefinition, LSystemRule

# Create a renderer with a fixed seed for reproducibility
renderer = LSystemRenderer(seed=42)

# 1. Render a preset to SVG
print("Rendering Koch snowflake...")
renderer.render("koch_snowflake", iterations=4, output="example_koch.svg")
print("  → example_koch.svg")

# 2. Render a stochastic plant
print("Rendering stochastic plant...")
renderer.render("plant_stochastic", iterations=5, output="example_plant.svg")
print("  → example_plant.svg")

# 3. Render with rainbow coloring
print("Rendering dragon curve with rainbow colors...")
defn = renderer.get_preset("dragon_curve")
defn.color_mode = "segment_index"
renderer.render(defn, iterations=12, output="example_dragon_rainbow.svg")
print("  → example_dragon_rainbow.svg")

# 4. Render with gradient coloring
print("Rendering gradient plant...")
gradient_def = LSystemDefinition(
    name="Gradient Plant",
    axiom="F",
    rules=[LSystemRule("F", "F[+F]F[-F]F")],
    angle=25.7,
    step_size=4.0,
    iterations=5,
    color_mode="position",
    gradient=("#1a5c1a", "#adff2f"),
)
renderer.render(gradient_def, output="example_gradient_plant.svg")
print("  → example_gradient_plant.svg")

# 5. Render with organic perturbation
print("Rendering organic tree...")
organic_def = LSystemDefinition(
    name="Organic Tree",
    axiom="F",
    rules=[LSystemRule("F", "FF+[+F-F-F]-[-F+F+F]")],
    angle=22.5,
    step_size=4.0,
    iterations=4,
    perturbation=3.0,      # ±3° angle noise
    step_perturbation=0.1,  # ±10% step noise
)
renderer.render(organic_def, output="example_organic.svg")
print("  → example_organic.svg")

# 6. Render to ASCII
print("Rendering Koch curve to ASCII...")
renderer.render("koch_curve", iterations=3, backend="ascii", output="example_koch.txt")
print("  → example_koch.txt")

# 7. Render all presets
print("Rendering all presets...")
results = renderer.render_all_presets(output_dir="./example_gallery", iterations=2)
for name, path in results.items():
    print(f"  {name}: {path}")

print("\nDone! Check the output files.")