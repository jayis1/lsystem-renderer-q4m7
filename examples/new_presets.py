#!/usr/bin/env python3
"""
Example: New Presets in v3.0

Demonstrates the six new presets added in version 3.0:
- Fibonacci Word Fractal
- Minkowski Sausage
- Moore Curve
- Koch Antisnowflake
- Cesàro Fractal
- Alternate Branching Plant
"""

from lsystem_renderer import LSystemRenderer

renderer = LSystemRenderer()

# ── Fibonacci Word Fractal ─────────────────────────────────────
# Based on the Fibonacci word sequence, produces a beautiful
# self-similar fractal pattern
result = renderer.render(
    "fibonacci_word",
    iterations=14,
    backend="svg",
    output="fibonacci_word.svg",
    width=800,
    height=800,
)
print(f"Fibonacci Word Fractal: {result}")

# ── Minkowski Sausage ───────────────────────────────────────────
# A classic space-filling variant curve
result = renderer.render(
    "minkowski_sausage",
    iterations=3,
    backend="svg",
    output="minkowski_sausage.svg",
    width=800,
    height=800,
)
print(f"Minkowski Sausage: {result}")

# ── Moore Curve ────────────────────────────────────────────────
# A space-filling curve similar to the Hilbert curve but
# forms a continuous loop
result = renderer.render(
    "moore_curve",
    iterations=4,
    backend="svg",
    output="moore_curve.svg",
    width=800,
    height=800,
)
print(f"Moore Curve: {result}")

# ── Koch Antisnowflake ──────────────────────────────────────────
# Like the Koch snowflake but with inward-pointing cusps
result = renderer.render(
    "koch_antisnowflake",
    iterations=4,
    backend="svg",
    output="koch_antisnowflake.svg",
)
print(f"Koch Antisnowflake: {result}")

# ── Cesàro Fractal ──────────────────────────────────────────────
# A generalization of the Koch curve with a non-standard angle
result = renderer.render(
    "cesaro_fractal",
    iterations=5,
    backend="svg",
    output="cesaro_fractal.svg",
)
print(f"Cesàro Fractal: {result}")

# ── Alternate Branching Plant ───────────────────────────────────
# A plant variant with different branching pattern
result = renderer.render(
    "plant_alternate",
    iterations=5,
    backend="svg",
    output="plant_alternate.svg",
)
print(f"Alternate Plant: {result}")