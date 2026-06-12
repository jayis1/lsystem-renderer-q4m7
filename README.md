# L-System Renderer — `lsystem-renderer-q4m7`

A **Lindenmayer System (L-System) renderer** — a formal grammar-based generative art engine that produces fractals, plant-like structures, and complex geometric patterns through string rewriting and turtle graphics interpretation.

## How It Works

L-systems work through **parallel string rewriting**: starting from an initial string (axiom), production rules are simultaneously applied to each symbol across multiple iterations. The resulting string is then interpreted as turtle graphics commands to produce 2D line art.

### Supported Features

| Feature | Description |
|---------|-------------|
| **Deterministic L-systems** | Standard one-symbol → one-replacement rules |
| **Stochastic L-systems** | Rules with probability weights for organic variation |
| **Context-sensitive L-systems** | Rules that consider neighboring symbols |
| **Parametric L-systems** | Rules with Python-evaluated conditions |
| **SVG rendering** | High-quality vector output with auto-scaling and centering |
| **ASCII rendering** | Terminal-friendly character-based output |
| **Depth-based coloring** | Branches colored by recursion depth for plant-like visuals |
| **10 built-in presets** | Classic fractals and plant models ready to render |

### Turtle Command Reference

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
| `(` | Decrease step size by factor |
| `)` | Increase step size by factor |

## Built-in Presets

| Preset Name | Description |
|------------|-------------|
| `koch_curve` | Classic Koch curve fractal |
| `koch_snowflake` | Koch snowflake (three Koch curves) |
| `sierpinski_triangle` | Sierpiński triangle |
| `dragon_curve` | Dragon curve (Heighway dragon) |
| `hilbert_curve` | Hilbert space-filling curve |
| `plant_simple` | Simple branching plant |
| `plant_stochastic` | Stochastic plant (varies each run) |
| `tree_bushy` | Bushy fractal tree |
| `penrose_tiles` | Penrose tiling pattern |
| `levy_c_curve` | Lévy C curve |
| `gosper_curve` | Gosper/flowsnake curve |

## Usage

### Command Line

```bash
# Render a Koch snowflake to SVG
python3 lsystem.py --preset koch_snowflake -i 4 -o koch.svg

# Render a stochastic plant with seed for reproducibility
python3 lsystem.py --preset plant_stochastic -i 5 --seed 42 -o plant.svg

# Render dragon curve as ASCII art
python3 lsystem.py --preset dragon_curve -i 10 --backend ascii -o dragon.txt

# List all presets
python3 lsystem.py --list-presets

# Custom L-system (Sierpinski arrowhead)
python3 lsystem.py --axiom "A" --rule "A->B-A-B" --rule "B->A+B+A" --angle 60 -i 7 -o custom.svg
```

### Python API

```python
from lsystem import LSystemRenderer, LSystemDefinition, LSystemRule

renderer = LSystemRenderer(seed=42)

# Use a preset
renderer.render("koch_snowflake", iterations=4, output="koch.svg")

# Define a custom L-system
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
```

## Architecture

```
lsystem.py
├── LSystemDefinition   — Data class holding axiom, rules, angle, etc.
├── LSystemRule          — Single production rule with optional probability/context
├── LSystemEngine        — Core string rewriting (iterate method)
├── TurtleInterpreter    — Converts L-system string → Segments
├── SVGRenderer          — Segments → SVG file with auto-scaling
├── ASCIIRenderer        — Segments → ASCII art text
├── LSystemRenderer      — High-level API tying everything together
└── PRESETS dict         — 11 built-in L-system definitions
```

## Requirements

- Python 3.7+ (no external dependencies — uses only stdlib)

## License

MIT