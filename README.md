# 🌿 L-System Renderer

[![CI](https://github.com/jayis1/lsystem-renderer-q4m7/actions/workflows/ci.yml/badge.svg)](https://github.com/jayis1/lsystem-renderer-q4m7/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-176%20passing-brightgreen)](https://github.com/jayis1/lsystem-renderer-q4m7)

A **formal grammar-based generative art engine** implementing Lindenmayer Systems (L-systems) with multiple rendering backends, advanced coloring, animation support, and a comprehensive Python + CLI interface.

```
   │  ╱╲  ╱╲     ╱╲       L-System Renderer v3.0
   │ ╱  ╲╱  ╲   ╱  ╲      Fractals • Plants • Curves
   │╱        ╲ ╱    ╲      SVG • PNG • PDF • ASCII
   ──────────────╱──────    
   ╲            ╱          20 built-in presets
    ╲    ╱╲    ╱           Deterministic, stochastic,
     ╲  ╱  ╲  ╱            context-sensitive, parametric
      ╲╱    ╲╱             
```

## ✨ Features

- **20 built-in presets** — Koch, Sierpiński, Dragon, Hilbert, Lévy C, Gosper, Penrose, Peano, Fibonacci Word, Minkowski Sausage, Moore Curve, and more
- **4 rendering backends** — SVG, PNG, **PDF** (new!), ASCII
- **Gallery renderer** — Tile multiple presets into a single SVG comparison grid
- **SVG optimization** — Reduce file size with float truncation, path merging, and whitespace removal
- **Advanced coloring** — Single, depth-based, position gradient, rainbow/segment-index
- **Animation** — Progressive SVG draw animations and step-by-step growth
- **Stochastic L-systems** — Probabilistic rule selection with seed control
- **Context-sensitive rules** — Left/right context matching for complex grammars
- **Parametric conditions** — Conditional rules via safe expression evaluation
- **Perturbation** — Organic randomness in angles and step sizes
- **JSON import/export** — Save and load L-system definitions
- **Configuration files** — JSON, TOML, and YAML config support
- **Comprehensive CLI** — One-command rendering, animation, galleries, and more

## 📦 Installation

```bash
# Basic install (SVG + ASCII backends)
pip install -e .

# With PNG support
pip install -e ".[png]"

# With PDF support
pip install -e ".[pdf]"

# With all optional dependencies
pip install -e ".[all]"

# Development dependencies (includes all optional deps + pytest)
pip install -e ".[dev]"
```

## 🚀 Quick Start

### Python API

```python
from lsystem_renderer import LSystemRenderer

renderer = LSystemRenderer()

# Render a preset to SVG
renderer.render("dragon_curve", iterations=10, output="dragon.svg")

# Render to PDF
renderer.render("hilbert_curve", iterations=5, backend="pdf", output="hilbert.pdf")

# Render with animation
renderer.render("plant_simple", iterations=5, animate=True, output="plant.svg")

# Create an optimized SVG (smaller file)
renderer.render_optimized("koch_snowflake", iterations=4, output="koch_opt.svg")

# Generate a gallery of all presets
renderer.render_gallery_grid("gallery.svg", iterations=2, columns=4)
```

### CLI

```bash
# Render a preset
lsystem-renderer --preset dragon_curve --iterations 10 -o dragon.svg

# Render to PDF
lsystem-renderer --preset hilbert_curve --backend pdf -o hilbert.pdf

# List available presets
lsystem-renderer --list-presets

# Show detailed preset info
lsystem-renderer --preset koch_curve --info

# Render with animation
lsystem-renderer --preset plant_simple --animate -o plant.svg

# Render an optimized SVG
lsystem-renderer --preset dragon_curve --optimize -o dragon.svg

# Generate a preset gallery
lsystem-renderer --gallery --gallery-cols 4 -o gallery.svg

# Custom L-system from command line
lsystem-renderer --axiom "F" --rules "F=F+F--F+F" --angle 60 -i 4 -o koch.svg

# Load definition from JSON
lsystem-renderer --load definition.json -o output.svg

# Render all presets
lsystem-renderer --render-all -d ./output/
```

## 🎨 Presets

| Preset | Type | Description |
|--------|------|-------------|
| `koch_curve` | Fractal | Classic Koch curve |
| `koch_snowflake` | Fractal | Koch snowflake (triangle base) |
| `koch_antisnowflake` | Fractal | Koch with inward cusps *(new)* |
| `sierpinski_triangle` | Fractal | Sierpiński triangle |
| `sierpinski_arrowhead` | Fractal | Sierpiński arrowhead curve |
| `dragon_curve` | Fractal | Dragon curve |
| `hilbert_curve` | Space-filling | Hilbert space-filling curve |
| `levy_c_curve` | Fractal | Lévy C curve |
| `gosper_curve` | Fractal | Gosper/flowsnake curve |
| `peano_curve` | Space-filling | Peano space-filling curve |
| `quadratic_koch` | Fractal | Quadratic Koch island |
| `fibonacci_word` | Fractal | Fibonacci word fractal *(new)* |
| `minkowski_sausage` | Space-filling | Minkowski sausage curve *(new)* |
| `moore_curve` | Space-filling | Moore curve (closed Hilbert) *(new)* |
| `cesaro_fractal` | Fractal | Cesàro fractal (80° variant) *(new)* |
| `cantor_dust` | Fractal | Cantor dust |
| `penrose_tiles` | Tiling | Penrose tile pattern |
| `plant_simple` | Plant | Simple branching plant |
| `plant_stochastic` | Plant | Stochastic plant variant |
| `plant_alternate` | Plant | Alternate branching plant *(new)* |
| `tree_bushy` | Plant | Bushy tree |
| `tree_willow` | Plant | Willow tree (with perturbation) |
| `fractal_tree` | Plant | Detailed fractal tree |
| `barnsley_fern` | Plant | Barnsley fern approximation |

## 🏗 Architecture

```
LSystemDefinition → LSystemEngine → TurtleInterpreter → ColorPostProcessor → Renderer
```

Each stage is independent and composable:

- **`LSystemDefinition`** — Defines the grammar (axiom, rules, angle, colors)
- **`LSystemEngine`** — Applies production rules iteratively
- **`TurtleInterpreter`** — Converts strings to line segments
- **`ColorPostProcessor`** — Assigns colors by mode (depth, position, rainbow)
- **`Renderer`** — Outputs to SVG, PNG, PDF, or ASCII

See [docs/architecture.md](docs/architecture.md) for full details.

## 📖 Advanced Usage

### Custom L-System Definitions

```python
from lsystem_renderer import LSystemDefinition, LSystemRule, LSystemRenderer

# Create a custom L-system
definition = LSystemDefinition(
    name="My Fractal",
    axiom="F",
    rules=[
        LSystemRule("F", "F+F--F+F"),  # Classic Koch rule
    ],
    angle=60.0,
    step_size=5.0,
    iterations=4,
    color_mode="segment_index",  # Rainbow coloring
)

renderer = LSystemRenderer()
renderer.render(definition, output="my_fractal.svg")
```

### Stochastic L-Systems

```python
definition = LSystemDefinition(
    name="Random Plant",
    axiom="F",
    rules=[
        LSystemRule("F", "F[+F]F[-F]F", probability=0.5),
        LSystemRule("F", "F[+F]F", probability=0.25),
        LSystemRule("F", "F[-F]F", probability=0.25),
    ],
    angle=25.7,
    step_size=4.0,
    iterations=5,
)
renderer = LSystemRenderer(seed=42)  # Reproducible randomness
```

### Gallery Rendering

```python
from lsystem_renderer.renderers.grid import GridRenderer
from lsystem_renderer.core.presets import PRESETS
import copy

grid = GridRenderer(cell_width=250, cell_height=250, columns=4)
subset = {k: copy.deepcopy(v) for k, v in PRESETS.items() if "plant" in k}
grid.render_grid(subset, "plants_gallery.svg", iterations=3)
```

### SVG Optimization

```python
from lsystem_renderer.utils.svg_optimizer import optimize_svg, merge_svg_paths, stats_svg

# Read an SVG file
with open("output.svg") as f:
    svg = f.read()

# Get statistics
stats = stats_svg(svg)
print(f"Size: {stats['bytes']} bytes, Paths: {stats['paths']}")

# Optimize: truncate floats, remove comments, collapse whitespace
optimized = optimize_svg(svg, precision=2)

# Merge paths with identical styles
merged = merge_svg_paths(optimized)

with open("output_optimized.svg", "w") as f:
    f.write(merged)
```

### PDF Rendering

```python
from lsystem_renderer import LSystemRenderer

renderer = LSystemRenderer()
renderer.render("dragon_curve", iterations=10, backend="pdf", output="dragon.pdf")
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=lsystem_renderer --cov-report=term-missing

# Run only v3 feature tests
python -m pytest tests/test_v3_features.py -v
```

All **176 tests** pass (including 50 new tests for v3.0 features).

## 📁 Project Structure

```
lsystem_renderer/
├── __init__.py              # Package exports
├── cli.py                   # CLI entry point
├── core/
│   ├── types.py             # Data types (LSystemDefinition, Rule, Segment, etc.)
│   ├── engine.py            # String rewriting engine
│   ├── interpreter.py       # Turtle graphics interpreter
│   ├── renderer.py          # Main rendering coordinator
│   ├── color_postprocessor.py # Color mode processing
│   ├── presets.py           # 20 built-in presets
│   └── config.py            # Configuration management
├── renderers/
│   ├── svg.py               # SVG renderer
│   ├── png.py               # PNG renderer (optional: Pillow)
│   ├── pdf.py               # PDF renderer (optional: reportlab) ★ new
│   ├── ascii.py             # ASCII renderer
│   └── grid.py              # Gallery grid renderer ★ new
└── utils/
    ├── colors.py             # Color utilities
    └── svg_optimizer.py      # SVG optimization ★ new
examples/
├── basic_usage.py            # Getting started
├── custom_definitions.py    # Custom L-systems
├── animation.py             # SVG animation
├── gallery_rendering.py     # Gallery/grid rendering ★ new
├── pdf_and_optimized.py     # PDF and optimization ★ new
├── new_presets.py           # v3 preset showcase ★ new
└── svg_optimization.py      # SVG optimization demo ★ new
docs/
├── architecture.md           # Architecture documentation ★ new
└── changelog.md              # Version history ★ new
tests/
├── test_lsystem.py           # Core test suite (126 tests)
└── test_v3_features.py       # v3 feature tests (50 tests) ★ new
```

## 🗺 Roadmap

- [ ] **EPS/PostScript backend** — Vector output for print workflows
- [ ] **Interactive viewer** — Real-time parameter adjustment with web UI
- [ ] **L-system composition** — Chain/blend multiple L-systems
- [ ] **Animation export** — GIF/APNG from growth animation
- [ ] **3D L-systems** — Turtle interpreter with 3D rotations
- [ ] **Subdivision curves** — Smooth interpolation of L-system paths
- [ ] **Performance mode** — C-extension acceleration for high-iteration counts

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. Contributions are welcome — bug reports, feature requests, new presets, and code improvements all help!

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

**v3.0.0** — PDF rendering, gallery renderer, SVG optimizer, 6 new presets, CLI enhancements