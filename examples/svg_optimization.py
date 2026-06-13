#!/usr/bin/env python3
"""
Example: SVG Optimization Utilities.

Demonstrates the SVG optimizer and statistics module.
"""

from lsystem_renderer.utils.svg_optimizer import optimize_svg, merge_svg_paths, stats_svg

# Sample SVG content
svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800">
<!-- This is a comment that should be removed -->
<path d="M10.12345678,20.98765432 L30.11111111,40.22222222" stroke="#000" stroke-width="1" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M50.33333333,60.44444444 L70.55555555,80.66666666" stroke="#000" stroke-width="1" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M90.77777777,100.88888888 L110.99999999,120.11111111" stroke="#ff0000" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>


</svg>"""

print("Original SVG:")
print(svg_content)
print()

# ── Get Statistics ──────────────────────────────────────────────
stats = stats_svg(svg_content)
print(f"SVG Statistics:")
for key, value in stats.items():
    print(f"  {key}: {value}")
print()

# ── Optimize SVG ────────────────────────────────────────────────
optimized = optimize_svg(svg_content, precision=2)
print("Optimized SVG:")
print(optimized)
print()

# ── Merge Paths ─────────────────────────────────────────────────
merged = merge_svg_paths(optimized)
print("Merged SVG:")
print(merged)
print()

# ── Compare Sizes ───────────────────────────────────────────────
orig_size = len(svg_content.encode("utf-8"))
opt_size = len(optimized.encode("utf-8"))
merged_size = len(merged.encode("utf-8"))
print(f"Original:   {orig_size:,} bytes")
print(f"Optimized:  {opt_size:,} bytes ({(1-opt_size/orig_size)*100:.1f}% reduction)")
print(f"Merged:     {merged_size:,} bytes ({(1-merged_size/orig_size)*100:.1f}% reduction)")