# Changelog

## v3.0.0 — 2026-06-13

### New Features

- **PDF Rendering Backend** — Vector-quality PDF output via reportlab (optional dependency)
- **Gallery/Grid Renderer** — `GridRenderer` creates tiled SVG galleries of multiple presets
- **SVG Optimizer** — `optimize_svg()` and `merge_svg_paths()` reduce SVG file size
- **6 New Presets:**
  - Fibonacci Word Fractal
  - Minkowski Sausage
  - Moore Curve
  - Koch Antisnowflake
  - Cesàro Fractal
  - Alternate Branching Plant
- **CLI Additions:**
  - `--backend pdf` — Render to PDF
  - `--info` — Print detailed preset information
  - `--optimize` — Apply SVG optimization on output
  - `--gallery` — Render all presets as a tiled grid
  - `--gallery-cols` / `--gallery-cell-size` — Gallery layout options
- **`LSystemRenderer.render_optimized()`** — One-call optimized SVG output
- **`LSystemRenderer.render_gallery_grid()`** — One-call gallery generation

### Improvements

- Version bumped from 2.0.0 to 3.0.0
- `pyproject.toml` now includes optional `pdf` and `all` dependency groups
- Package `__init__.py` exports all new classes and functions
- Comprehensive test suite: 176 tests (+50 new), 58 subtests
- New example scripts: `gallery_rendering.py`, `pdf_and_optimized.py`, `new_presets.py`, `svg_optimization.py`
- Architecture documentation in `docs/architecture.md`

### Bug Fixes

(No new bugs introduced — all 176 tests pass)

## v2.0.0 — 2026-06-12

### Features
- SVG animation (progressive draw)
- Growth animation (step-by-step iteration rendering)
- Color modes: depth, position gradient, rainbow (segment_index), single
- Color utilities: lerp_color, hsl_to_rgb, rainbow_color
- Perturbation/noise for organic variation
- JSON import/export of definitions
- Batch rendering (--render-all)
- String statistics (--stats)
- 3 new presets (fractal_tree, barnsley_fern, cantor_dust)
- Bracket-aware context-sensitive matching
- Iteration safety guard
- Safe eval for parametric conditions
- 14 total presets

### Bug Fixes
- lerp_color rounding — int() → round()
- SVG title XSS — added _escape_xml()
- SVG path grouping — group by (color, width) not just color
- iterate_steps missing negative validation
- CLI --render-all requiring preset
- ASCII output path for extensionless filenames
- Duplicate iteration validation

## v1.0.0 — Initial Release

- Core L-system engine with deterministic, stochastic, and context-sensitive rules
- SVG and ASCII rendering backends
- Turtle graphics interpreter with 12+ command symbols
- 11 built-in presets
- CLI with argparse interface