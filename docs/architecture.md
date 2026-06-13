# Architecture

## Overview

The L-System Renderer follows a clean pipeline architecture:

```
LSystemDefinition → LSystemEngine → TurtleInterpreter → ColorPostProcessor → Renderer
```

Each stage is independent and composable, allowing you to use any combination.

## Core Modules

### `core/types.py`
Data types used throughout the system:
- **`LSystemDefinition`** — Full definition of an L-system (axiom, rules, angle, colors, etc.)
- **`LSystemRule`** — A single production rule with optional probability, context, and conditions
- **`Segment`** — A line segment (x1, y1, x2, y2, color, width, depth)
- **`TurtleState`** — Current state of the virtual turtle
- **`RenderBackend`** / **`ColorMode`** — Enums for output format and coloring strategy

### `core/engine.py`
The string rewriting engine:
- **`LSystemEngine`** — Takes a definition and applies production rules iteratively
- Supports deterministic, stochastic (probabilistic), and context-sensitive rules
- Parametric conditions via safe eval

### `core/interpreter.py`
Turtle graphics interpreter:
- **`TurtleInterpreter`** — Converts a string into a list of `Segment` objects
- Supports: forward/draw (`F`, `G`), turn (`+`, `-`), push/pop (`[`, `]`), reverse (`|`), shrink (`@`), no-draw (`f`, `g`)
- Branch-dependent line width thinning
- Perturbation support for organic variation

### `core/color_postprocessor.py`
Post-processing color assignment:
- **`ColorPostProcessor`** — Applies color modes (single, depth, position, segment_index/rainbow)
- Gradient interpolation between two colors

### `core/renderer.py`
Main rendering coordinator:
- **`LSystemRenderer`** — High-level API that orchestrates the full pipeline
- Convenience methods: `render()`, `render_all_presets()`, `render_gallery_grid()`, `render_optimized()`, `animate_growth()`

### `core/presets.py`
Built-in L-system definitions (20 presets):
- Classic fractals: Koch, Sierpiński, Dragon, Hilbert, Lévy C, Gosper, Penrose, Peano, Quadratic Koch
- New in v3: Fibonacci Word, Minkowski Sausage, Moore Curve, Koch Antisnowflake, Cesàro Fractal
- Plant models: Simple Plant, Stochastic Plant, Bushy Tree, Willow Tree, Fractal Tree, Barnsley Fern, Alternate Branching Plant
- Special: Cantor Dust, Sierpiński Arrowhead

### `core/config.py`
Configuration management via `LSystemConfig` dataclass with JSON/TOML/YAML support.

## Rendering Backends

### `renderers/svg.py`
**`SVGRenderer`** — Produces scalable vector graphics with:
- Auto-scaling and centering
- Path grouping by (color, width) for smaller files
- Animated SVG output (progressive draw)
- Title and description elements

### `renderers/png.py`
**`PNGRenderer`** — Raster output via Pillow (optional dependency).

### `renderers/pdf.py` *(New in v3.0)*
**`PDFRenderer`** — Vector PDF output via reportlab (optional dependency).

### `renderers/ascii.py`
**`ASCIIRenderer`** — Terminal-friendly text output.

### `renderers/grid.py` *(New in v3.0)*
**`GridRenderer`** — Renders multiple L-systems as a tiled grid in a single SVG, ideal for galleries and comparison views.

## Utility Modules

### `utils/colors.py`
Color manipulation utilities: hex↔RGB, HSL↔RGB, lerp, rainbow, XML escaping.

### `utils/svg_optimizer.py` *(New in v3.0)*
SVG optimization tools:
- **`optimize_svg()`** — Truncate floats, remove comments, collapse whitespace, strip leading zeros
- **`merge_svg_paths()`** — Merge consecutive `<path>` elements with identical styles
- **`stats_svg()`** — Analyze SVG content and return element counts and byte sizes

## CLI

The `lsystem-renderer` command provides:
- `--preset` / `--axiom` / `--rules` — Define an L-system
- `--backend` — Choose svg, png, pdf, ascii, terminal
- `--iterations` — Control recursion depth
- `--width` / `--height` — Canvas dimensions
- `--animate` — Produce animated SVG
- `--render-all` — Batch render all presets
- `--gallery` *(New)* — Generate a tiled gallery SVG
- `--optimize` *(New)* — Apply SVG optimization
- `--info` *(New)* — Print detailed preset information
- `--stats` — Show string statistics
- `--list-presets` — List available presets