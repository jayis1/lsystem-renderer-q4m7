#!/usr/bin/env python3
"""
Example: PDF and SVG Optimized Output.

Demonstrates rendering to PDF format and creating
optimized SVG files with reduced file size.
"""

from lsystem_renderer import LSystemRenderer

renderer = LSystemRenderer()

# ── PDF Rendering ──────────────────────────────────────────────
# Render to PDF (requires: pip install reportlab)
result = renderer.render(
    "dragon_curve",
    iterations=10,
    backend="pdf",
    output="dragon_curve.pdf",
    width=1000,
    height=1000,
)
print(f"PDF saved to: {result}")

# ── Optimized SVG ──────────────────────────────────────────────
# Render with SVG optimization (float truncation, path merging)
result = renderer.render_optimized(
    "hilbert_curve",
    iterations=5,
    output="hilbert_optimized.svg",
    width=800,
    height=800,
)
print(f"Optimized SVG saved to: {result}")

# ── Compare file sizes ─────────────────────────────────────────
import os

# Standard SVG
renderer.render("hilbert_curve", iterations=5, output="hilbert_standard.svg")
standard_size = os.path.getsize("hilbert_standard.svg")
optimized_size = os.path.getsize("hilbert_optimized.svg")

print(f"\nStandard SVG:  {standard_size:,} bytes")
print(f"Optimized SVG: {optimized_size:,} bytes")
print(f"Reduction:     {(1 - optimized_size/standard_size)*100:.1f}%")