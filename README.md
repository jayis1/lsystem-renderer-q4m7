# 🌿 L-System Renderer

[![CI](https://github.com/jayis1/lsystem-renderer-q4m7/actions/workflows/ci.yml/badge.svg)](https://github.com/jayis1/lsystem-renderer-q4m7/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-126%20passing-brightgreen)](https://github.com/jayis1/lsystem-renderer-q4m7)

A **Lindenmayer System (L-System) renderer** — a formal grammar-based generative art engine that produces fractals, plant-like structures, and complex geometric patterns through string rewriting and turtle graphics interpretation.

```
     /\    /\    /\
    /  \  /  \  /  \
   /    \/    \/    \
  /                  \
  \    /\    /\    /\ /
   \  /  \  /  \  /  X
    \/    \/    \/
     Koch Snowflake — 4 iterations
```

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Deterministic L-systems** | Standard one-symbol → one-replacement rules |
| **Stochastic L-systems** | Rules with probability weights for organic variation |
| **Context-sensitive L-systems** | Rules that consider neighboring symbols (ignoring brackets) |
| **Parametric L-systems** | Rules with Python-evaluated conditions |
| **SVG rendering** | High-quality vector output with auto-scaling, centering, and grouped paths |
| **PNG rendering** | Raster output via Pillow (optional) |
| **ASCII rendering** | Terminal-friendly character-based output with directional chars |
| **SVG animation** | Progressive draw animation with opacity transitions |
| **Growth animation** | Render each iteration step as a separate SVG |
| **4 color modes** | Depth, position gradient, rainbow (segment_index), single |
| **Perturbation/noise** | Random angle and step-size perturbation for organic variation |
| **JSON import/export** | Save and load L-system definitions as JSON files |
| **YAML/TOML config** | Configuration file support (YAML, TOML, JSON) |
| **Batch rendering** | Render all presets at once with `--render-all` |
| **String statistics** | Analyze L-system strings: length, symbol counts, branch depth |
| **18 built-in presets** | Classic fractals, plants, curves, and space-filling curves |
| **Installable package** | pip-installable with `lsystem-renderer` CLI entry point |
| **Comprehensive tests** | 126 tests with full coverage |
| **Type hints** | Full type annotations throughout |
| **Input validation** | Dataclass-level validation for all definitions and rules |
| **Logging** | Structured logging with configurable verbosity |

## 📑 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Built-in Presets](#-built-in-presets)
- [Turtle Command Reference](#-turtle-command-reference)
- [Usage](#-usage)
  - [Command Line](#command-line)
  - [Python API](#python-api)
- [Configuration Files](#-configuration-files)
- [Architecture](#-architecture)
- [Development](#-development)
- [Known Issues (Resolved)](#-known-issues-resolved)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [Changelog](#-changelog)
- [License](#-license)

## 📦 Installation

### From PyPI (once published)

```bash
pip install lsystem-renderer-q4m7
```

### From Source

```bash
git clone https://github.com/jayis1/lsystem-renderer-q4m7.git
cd lsystem-renderer-q4m7
pip install -e .
```

### With Optional Dependencies

```bash
# PNG rendering support (requires Pillow)
pip install -e ".[png]"

# YAML configuration support (requires PyYAML)
pip install -e ".[yaml]"

# Everything
pip install -e ".[all]"

# Development dependencies (pytest, coverage, etc.)
pip install -e ".[dev]"
```

### Requirements

- **Python 3.8+** (no external dependencies for core functionality)
- **Pillow** (optional, for PNG rendering)
- **PyYAML** (optional, for YAML config files)
- **tomli** (optional, for TOML config on Python < 3.11)

## 🚀 Quick Start

### Command Line

```bash
# Render Koch snowflake to SVG
lsystem-renderer --preset koch_snowflake -i 4 -o koch.svg

# Render dragon curve with rainbow colors
lsystem-renderer --preset dragon_curve -i 12 --color-mode segment_index -o dragon.svg

# Render organic tree with perturbation
lsystem-renderer --preset tree_willow -i 5 --perturbation 3.0 -o willow.svg

# Render all presets to a gallery directory
lsystem-renderer --render-all -d ./gallery

# Render to PNG
lsystem-renderer --preset hilbert_curve -i 5 --backend png -o hilbert.png

# List all 18 presets
lsystem-renderer --list-presets
```

### Python API

```python
from lsystem_renderer import LSystemRenderer

renderer = LSystemRenderer(seed=42)

# Render a preset
renderer.render("koch_snowflake", iterations=4, output="koch.svg")

# Render with custom colors and animation
renderer.render("plant_simple", iterations=5, output="plant.svg",
                animate=True, animation_duration=5.0)

# Render all presets
results = renderer.render_all_presets(output_dir="./gallery")
```

## 🌸 Built-in Presets

| Preset Name | Description | Color Mode |
|------------|-------------|------------|
| `koch_curve` | Classic Koch curve fractal | depth |
| `koch_snowflake` | Koch snowflake (three Koch curves) | depth |
| `sierpinski_triangle` | Sierpiński triangle | depth |
| `sierpinski_arrowhead` | Sierpiński arrowhead curve | rainbow |
| `dragon_curve` | Dragon curve (Heighway dragon) | rainbow |
| `hilbert_curve` | Hilbert space-filling curve | rainbow |
| `levy_c_curve` | Lévy C curve | rainbow |
| `gosper_curve` | Gosper/flowsnake curve | rainbow |
| `peano_curve` | Peano space-filling curve | rainbow |
| `quadratic_koch` | Quadratic Koch Island | rainbow |
| `plant_simple` | Simple branching plant | depth |
| `plant_stochastic` | Stochastic plant (varies each run) | depth |
| `tree_bushy` | Bushy fractal tree | depth |
| `tree_willow` | Willow tree with perturbation | depth |
| `fractal_tree` | Fractal tree (branching) | depth |
| `barnsley_fern` | Barnsley fern (approximation) | depth |
| `cantor_dust` | Cantor dust fractal | single |
| `penrose_tiles` | Penrose tiling pattern | depth |

## 🐢 Turtle Command Reference

| Symbol | Action |
|--------|--------|
| `F`, `G` | Move forward and draw a line |
| `f` | Move forward without drawing |
| `+` | Turn left by the angle increment |
| `-` | Turn right by the angle increment |
| `[` | Push turtle state (start branch) |
| `]` | Pop turtle state (end branch) |
| `\|` | Reverse direction (turn 180°) |
| `#` | Increase line width |
| `!` | Decrease line width |
| `<` | Halve step size |
| `>` | Double step size |
| `(` | Decrease step size by factor (0.7) |
| `)` | Increase step size by factor |
| `@` | Shrink step size by 0.8 |

## 📖 Usage

### Command Line

```bash
# Render a Koch snowflake to SVG
lsystem-renderer --preset koch_snowflake -i 4 -o koch.svg

# Render a stochastic plant with seed for reproducibility
lsystem-renderer --preset plant_stochastic -i 5 --seed 42 -o plant.svg

# Render dragon curve as ASCII art
lsystem-renderer --preset dragon_curve -i 10 --backend ascii -o dragon.txt

# Render with rainbow color mode
lsystem-renderer --preset hilbert_curve -i 5 --color-mode segment_index -o hilbert.svg

# Render with gradient (bottom=red, top=blue)
lsystem-renderer --preset plant_simple -i 5 --color-mode position --gradient "#ff0000,#0000ff" -o gradient.svg

# Add organic perturbation (angle noise ±3°)
lsystem-renderer --preset tree_bushy -i 4 --perturbation 3.0 -o organic.svg

# Render all presets at once
lsystem-renderer --render-all -d ./output

# Animate growth steps (step_0.svg, step_1.svg, ...)
lsystem-renderer --preset koch_snowflake --animate-steps -d ./growth

# Generate animated SVG (progressive draw)
lsystem-renderer --preset plant_simple -i 5 --animate -o growing.svg

# Print string statistics
lsystem-renderer --preset dragon_curve -i 12 --stats

# List all presets
lsystem-renderer --list-presets

# Custom L-system (Sierpinski arrowhead)
lsystem-renderer --axiom "A" --rule "A->B-A-B" --rule "B->A+B+A" --angle 60 -i 7 -o custom.svg

# Load from JSON definition
lsystem-renderer --load my_definition.json -o output.svg

# Save definition to JSON (no rendering)
lsystem-renderer --preset koch_snowflake --save koch.json

# Use a configuration file
lsystem-renderer --config config.json

# Render to PNG (requires Pillow)
lsystem-renderer --preset dragon_curve -i 10 --backend png -o dragon.png

# Enable verbose logging
lsystem-renderer -v --preset koch_curve -i 3 -o koch.svg
```

### Python API

```python
from lsystem_renderer import (
    LSystemRenderer, LSystemDefinition, LSystemRule,
    LSystemEngine, SVGRenderer, ASCIIRenderer, PNGRenderer,
    ColorPostProcessor, LSystemConfig,
    hex_to_rgb, lerp_color, hsl_to_rgb, rgb_to_hsl,
    complementary_color, blend_colors,
    rainbow_color, PRESETS,
)

renderer = LSystemRenderer(seed=42)

# ── Presets ────────────────────────────────────────────────
renderer.render("koch_snowflake", iterations=4, output="koch.svg")
renderer.render("dragon_curve", iterations=12, backend="ascii", output="dragon.txt")
renderer.render("hilbert_curve", iterations=5, backend="png", output="hilbert.png")

# ── Custom Definitions ─────────────────────────────────────
custom = LSystemDefinition(
    name="My Fractal",
    axiom="F",
    rules=[LSystemRule("F", "F+F-F-F+F")],
    angle=90.0,
    step_size=5.0,
    iterations=4,
    colors={0: "#ff6600", 1: "#ff3300"},
)
renderer.render(custom, output="custom.svg")

# ── Rainbow Color Mode ─────────────────────────────────────
rainbow_def = LSystemDefinition(
    name="Rainbow Dragon",
    axiom="F",
    rules=[LSystemRule("F", "F+G"), LSystemRule("G", "F-G")],
    angle=90.0,
    step_size=5.0,
    iterations=12,
    color_mode="segment_index",
)
renderer.render(rainbow_def, output="rainbow_dragon.svg")

# ── Gradient Coloring ──────────────────────────────────────
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
renderer.render(gradient_def, output="gradient_plant.svg")

# ── Organic Perturbation ───────────────────────────────────
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
renderer.render(organic_def, output="organic.svg")

# ── Animation ───────────────────────────────────────────────
# Progressive draw animation
renderer.render("plant_simple", iterations=5, output="growing.svg",
                animate=True, animation_duration=5.0)

# Growth step sequence
steps = renderer.animate_growth("koch_snowflake", output_dir="./growth", iterations=4)
print(f"Generated {len(steps)} step files")

# ── Save/Load Definitions ──────────────────────────────────
custom.to_json("my_fractal.json")
loaded = LSystemDefinition.from_json("my_fractal.json")

# ── Configuration Files ─────────────────────────────────────
config = LSystemConfig(
    preset="koch_snowflake",
    iterations=4,
    backend="svg",
    seed=42,
)
config.to_json("config.json")
result = renderer.render_from_config(config)

# ── String Analysis ────────────────────────────────────────
engine = LSystemEngine(custom)
lstring = engine.iterate(4)
stats = LSystemEngine.analyze(lstring)
print(f"Length: {stats['length']:,}, Drawing symbols: {stats['draw_symbols']:,}")
print(f"Max branch depth: {stats['branch_depth']}")

# ── Color Utilities ─────────────────────────────────────────
# Hex/RGB conversion
r, g, b = hex_to_rgb("#ff6600")
hex_str = rgb_to_hex(255, 102, 0)

# Linear interpolation
mid_color = lerp_color("#000000", "#ffffff", 0.5)  # "#808080"

# HSL conversion
r, g, b = hsl_to_rgb(120, 0.85, 0.55)
h, s, l = rgb_to_hsl(255, 0, 0)

# Complementary color
comp = complementary_color("#ff0000")  # "#00ffff"

# Multi-color blending
blended = blend_colors(["#ff0000", "#00ff00", "#0000ff"], 0.5)

# ── Batch Rendering ─────────────────────────────────────────
results = renderer.render_all_presets(output_dir="./gallery")
for name, path in results.items():
    print(f"{name}: {path}")
```

## ⚙️ Configuration Files

The renderer supports configuration via JSON, YAML, or TOML files:

```json
{
  "preset": "koch_snowflake",
  "iterations": 4,
  "seed": 42,
  "backend": "svg",
  "render": {
    "width": 1000,
    "height": 1000,
    "background": "#1a1a2e",
    "margin": 20.0,
    "animate": false,
    "animation_duration": 5.0
  },
  "output": {
    "output_dir": "./output",
    "overwrite": true
  }
}
```

Load with: `lsystem-renderer --config config.json`

Or in Python:
```python
from lsystem_renderer import LSystemConfig

config = LSystemConfig.from_file("config.json")
# Or: config = LSystemConfig.from_yaml("config.yaml")
result = renderer.render_from_config(config)
```

## 🏗 Architecture

```
lsystem_renderer/
├── __init__.py              — Package exports and version
├── cli.py                   — Full-featured argparse CLI
├── core/
│   ├── __init__.py
│   ├── types.py             — Data types: Segment, TurtleState, LSystemRule, LSystemDefinition
│   ├── engine.py            — Core string rewriting engine (iterate, iterate_steps, analyze)
│   ├── interpreter.py       — Turtle graphics interpreter (string → segments)
│   ├── color_postprocessor.py — Color mode application (depth, gradient, rainbow, single)
│   ├── renderer.py          — High-level LSystemRenderer API
│   ├── presets.py           — 18 built-in L-system definitions
│   └── config.py            — Configuration management (JSON/YAML/TOML)
├── renderers/
│   ├── __init__.py
│   ├── svg.py               — SVG renderer (grouped paths, animation)
│   ├── ascii.py             — ASCII art renderer (directional characters)
│   └── png.py               — PNG renderer (via Pillow, optional)
└── utils/
    ├── __init__.py
    └── colors.py             — Color utilities (hex/RGB, lerp, HSL, rainbow, complementary, blend)

tests/
└── test_lsystem.py           — 126 comprehensive tests

examples/
├── basic_usage.py            — Getting started examples
├── custom_definitions.py     — Custom L-system definitions
└── animation.py              — Animation and growth examples
```

### Pipeline

```
Definition → Engine.iterate() → L-string → TurtleInterpreter.interpret() → Segments
    → ColorPostProcessor.apply() → Colored Segments → Renderer.render() → Output File
```

## 🛠 Development

```bash
# Clone and set up
git clone https://github.com/jayis1/lsystem-renderer-q4m7.git
cd lsystem-renderer-q4m7
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=lsystem_renderer --cov-report=html

# Run specific tests
pytest tests/test_lsystem.py::TestLSystemEngine -v

# Run the CLI
lsystem-renderer --list-presets

# Or directly
python3 -m lsystem_renderer.cli --list-presets
```

## 🔧 Known Issues (Resolved)

The following bugs were identified and have been fixed:

1. **`lerp_color` rounding error** — Used `int()` (truncation) instead of `round()` for color interpolation, causing `lerp_color("#000000", "#ffffff", 0.5)` to return `#7f7f7f` instead of `#808080`. Fixed by switching to `round()`.

2. **SVG title XSS/malformed XML** — SVG `<title>` and `<desc>` elements contained unescaped XML special characters (`<`, `>`, `&`), which could produce malformed SVG or allow XSS in browser contexts. Fixed by adding `_escape_xml()` helper.

3. **SVG path grouping lost width variation** — When grouping segments by color for compact SVG output, all segments in a group were rendered with the first segment's `stroke-width`. Fixed by grouping by `(color, rounded_width)` tuple.

4. **`iterate_steps` missing validation** — The `iterate_steps()` method did not validate negative iterations. Fixed by adding the same `ValueError` check.

5. **CLI `--render-all` required preset** — The `--render-all` flag required `--preset` to be specified. Fixed by moving the handler before definition resolution.

6. **ASCII output path for extensionless filenames** — Incorrect path handling for filenames without extensions. Fixed by checking basename before replacing extensions.

7. **Duplicate iteration validation** — Removed duplicated `if n < 0` check in `iterate_steps()`.

## 🗺 Roadmap

- [ ] **3D L-systems** — Extend turtle interpreter to support 3D rendering
- [ ] **PDF export** — Add PDF rendering backend
- [ ] **Interactive viewer** — Web-based interactive L-system explorer
- [ ] **Parametric L-systems (full)** — Full parametric L-system support with symbol parameters
- [ ] **Open L-systems** — Environment-sensitive L-systems
- [ ] **Tiled L-systems** — Tiling and wallpaper patterns
- [ ] **Performance optimization** — C-accelerated string rewriting for large iterations
- [ ] **Animation to GIF/MP4** — Convert growth steps to animated formats
- [ ] **WebAssembly build** — Run in browser via Pyodide
- [ ] **More presets** — Add Fibonacci word, Minkowski sausage, Moore curve, etc.

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project, including:

- Development setup
- Running tests
- Adding new presets
- Adding new renderers
- Code style guidelines
- Pull request process

## 📋 Changelog

### v2.0.0 — Comprehensive Improvement

**Architecture**
- Restructured monolithic `lsystem.py` into a proper Python package (`lsystem_renderer/`)
- Split into 9 focused modules: types, engine, interpreter, color postprocessor, renderer, presets, config, SVG renderer, ASCII renderer, PNG renderer, colors utils
- Full type hints and input validation throughout
- Added `__post_init__` validation to all dataclasses

**New Features**
- **PNG rendering backend** — Render to PNG images via Pillow (optional dependency)
- **Configuration files** — Load/save rendering configuration from JSON, YAML, or TOML
- **4 new presets** — Sierpiński Arrowhead, Peano Curve, Quadratic Koch Island, Willow Tree
- **`@` turtle symbol** — Shrink step size by 0.8 factor
- **`Segment` helper methods** — `length()`, `midpoint()`, `direction_deg()`
- **`LSystemRule.parse()`** — Parse rules from strings like `"F->F+F"`
- **Color utilities** — `rgb_to_hsl()`, `complementary_color()`, `blend_colors()`
- **`ColorMode` enum** — Type-safe color mode selection with `from_string()` / `to_string()`
- **`RenderConfig` / `OutputConfig`** — Structured configuration dataclasses
- **Branch depth analysis** — `LSystemEngine.analyze()` now reports `branch_depth`
- **Verbose logging** — CLI `-v` flag for debug output
- **`lsystem-renderer` CLI entry point** — Installable console script

**Infrastructure**
- `pyproject.toml` — Modern Python packaging with optional dependencies
- `.github/workflows/ci.yml` — CI pipeline testing Python 3.8–3.12
- `.gitignore` — Proper ignore patterns
- `LICENSE` — MIT license
- `CONTRIBUTING.md` — Contributor guidelines
- `examples/` — 3 usage example scripts
- Installable via pip with `[png]`, `[yaml]`, `[toml]`, `[dev]`, `[all]` extras

**Testing**
- Expanded from 71 to 126 tests
- Added tests for: `Segment` methods, `ColorMode` enum, `LSystemRule.parse()`, `LSystemRule` validation, `LSystemDefinition` validation, `PNGRenderer`, `LSystemConfig`, CLI commands, new presets, `rgb_to_hsl`, `complementary_color`, `blend_colors`, config JSON round-trip

### v1.0.0 — Initial Release

- Deterministic, stochastic, context-sensitive, parametric L-systems
- SVG and ASCII rendering
- Turtle graphics interpreter with 12+ command symbols
- 14 built-in presets
- JSON import/export
- SVG animation, growth animation
- Color modes: depth, position gradient, rainbow, single
- Perturbation/noise
- 7 bug fixes

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.