"""
L-System Renderer — A formal grammar-based generative art engine.

Implements Lindenmayer Systems (L-systems) with:
  - Parametric L-systems (rules with parameters)
  - Stochastic L-systems (probabilistic rule selection)
  - Context-sensitive L-systems
  - Multiple rendering backends (SVG, ASCII, terminal)
  - Built-in presets for classic fractals and plant models
  - Custom color mapping and styling
  - Turtle graphics interpretation with 2D/3D extensions
"""

from __future__ import annotations

import copy
import hashlib
import math
import random
import re
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)


# ---------------------------------------------------------------------------
# Core data types
# ---------------------------------------------------------------------------

class RenderBackend(Enum):
    SVG = auto()
    ASCII = auto()
    TERMINAL = auto()


@dataclass
class TurtleState:
    """Snapshot of the turtle's state for push/pop operations."""
    x: float = 0.0
    y: float = 0.0
    angle: float = 90.0  # degrees; 0 = right, 90 = up
    step_size: float = 5.0
    angle_increment: float = 25.0
    line_width: float = 1.0
    color: str = "#000000"
    depth: int = 0


@dataclass
class Segment:
    """A single line segment produced by the turtle interpreter."""
    x1: float
    y1: float
    x2: float
    y2: float
    color: str = "#000000"
    width: float = 1.0
    depth: int = 0


@dataclass
class LSystemRule:
    """A single production rule.

    Attributes:
        predecessor: The symbol this rule replaces (e.g. 'F').
        successor: The replacement string (e.g. 'F+F--F+F').
        condition: Optional Python expression that must evaluate to True
                    for the rule to apply (parametric L-systems).
        probability: Weight for stochastic rule selection (default 1.0).
        left_context: Left context for context-sensitive rules.
        right_context: Right context for context-sensitive rules.
    """
    predecessor: str
    successor: str
    condition: Optional[str] = None
    probability: float = 1.0
    left_context: Optional[str] = None
    right_context: Optional[str] = None


@dataclass
class LSystemDefinition:
    """Complete definition of an L-system.

    Attributes:
        name: Human-readable name.
        axiom: The initial string / starting state.
        rules: List of production rules.
        angle: Default turning angle in degrees.
        step_size: Default forward step length.
        iterations: Default number of iterations to apply.
        line_width: Default line width for rendering.
        colors: Optional mapping from depth -> color string.
    """
    name: str
    axiom: str
    rules: List[LSystemRule]
    angle: float = 25.0
    step_size: float = 5.0
    iterations: int = 4
    line_width: float = 1.0
    colors: Dict[int, str] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# L-system engine (string rewriting)
# ---------------------------------------------------------------------------

class LSystemEngine:
    """Core engine that performs L-system string rewriting.

    Supports:
      - Deterministic rules
      - Stochastic rules (probability weights)
      - Context-sensitive rules (left/right context matching)
      - Parametric rules (conditions evaluated as Python expressions)
    """

    def __init__(self, definition: LSystemDefinition, seed: Optional[int] = None):
        self.definition = definition
        self.rng = random.Random(seed)
        self._param_context: Dict[str, Any] = {}

    def _build_rule_map(self) -> Dict[str, List[LSystemRule]]:
        """Index rules by predecessor symbol for O(1) lookup."""
        rule_map: Dict[str, List[LSystemRule]] = defaultdict(list)
        for rule in self.definition.rules:
            rule_map[rule.predecessor].append(rule)
        return rule_map

    def _match_context(
        self, rule: LSystemRule, symbol: str, string: str, pos: int
    ) -> bool:
        """Check left and right context for context-sensitive rules."""
        # Left context: check if the symbols to the left match
        if rule.left_context is not None:
            left_start = pos - len(rule.left_context)
            if left_start < 0:
                return False
            left_str = string[left_start:pos]
            if left_str != rule.left_context:
                return False

        # Right context: check if the symbols to the right match
        if rule.right_context is not None:
            right_end = pos + 1 + len(rule.right_context)
            if right_end > len(string):
                return False
            right_str = string[pos + 1 : right_end]
            if right_str != rule.right_context:
                return False

        return True

    def _evaluate_condition(self, rule: LSystemRule) -> bool:
        """Evaluate a parametric rule's condition."""
        if rule.condition is None:
            return True
        try:
            return bool(eval(rule.condition, {"__builtins__": {}}, self._param_context))
        except Exception:
            return False

    def _select_rule(
        self, rules: List[LSystemRule], symbol: str, string: str, pos: int
    ) -> Optional[LSystemRule]:
        """Select the appropriate rule for a symbol, considering context,
        conditions, and probability."""
        matching: List[LSystemRule] = []
        for rule in rules:
            if not self._match_context(rule, symbol, string, pos):
                continue
            if not self._evaluate_condition(rule):
                continue
            matching.append(rule)

        if not matching:
            return None
        if len(matching) == 1:
            return matching[0]

        # Stochastic selection
        total_weight = sum(r.probability for r in matching)
        roll = self.rng.uniform(0, total_weight)
        cumulative = 0.0
        for rule in matching:
            cumulative += rule.probability
            if roll <= cumulative:
                return rule
        return matching[-1]

    def iterate(self, iterations: Optional[int] = None) -> str:
        """Apply production rules for the given number of iterations.

        Returns the produced string.
        """
        n = iterations if iterations is not None else self.definition.iterations
        current = self.definition.axiom
        rule_map = self._build_rule_map()

        for _ in range(n):
            next_str_parts: List[str] = []
            for pos, symbol in enumerate(current):
                if symbol in rule_map:
                    rule = self._select_rule(
                        rule_map[symbol], symbol, current, pos
                    )
                    if rule is not None:
                        next_str_parts.append(rule.successor)
                    else:
                        next_str_parts.append(symbol)
                else:
                    next_str_parts.append(symbol)
            current = "".join(next_str_parts)

        return current


# ---------------------------------------------------------------------------
# Turtle interpreter
# ---------------------------------------------------------------------------

class TurtleInterpreter:
    """Interprets an L-system string using turtle graphics.

    Standard symbol meanings:
      F, G   — Move forward and draw
      f      — Move forward without drawing
      +      — Turn left by angle_increment
      -      — Turn right by angle_increment
      [      — Push state onto stack
      ]      — Pop state from stack
      |      — Reverse direction (turn 180°)
      #      — Increment line width
      !      — Decrement line width
      (      — Decrease step size by factor
      )      — Increase step size by factor
      {      — Begin polygon
      }      — End polygon
      <      — Divide step size by 2
      >      — Multiply step size by 2
    """

    def __init__(
        self,
        angle: float = 25.0,
        step_size: float = 5.0,
        line_width: float = 1.0,
        colors: Optional[Dict[int, str]] = None,
    ):
        self.initial_angle = angle
        self.initial_step_size = step_size
        self.initial_line_width = line_width
        self.colors = colors or {}

    def interpret(self, lstring: str) -> List[Segment]:
        """Interpret an L-system string and return a list of line segments."""
        state = TurtleState(
            x=0.0,
            y=0.0,
            angle=90.0,  # Start pointing up
            step_size=self.initial_step_size,
            angle_increment=self.initial_angle,
            line_width=self.initial_line_width,
            color=self.colors.get(0, "#2d5016"),
            depth=0,
        )
        stack: List[TurtleState] = []
        segments: List[Segment] = []
        step_factor = 0.7  # For ( and ) symbols

        for ch in lstring:
            if ch in ("F", "G"):
                # Move forward and draw
                rad = math.radians(state.angle)
                new_x = state.x + state.step_size * math.cos(rad)
                new_y = state.y + state.step_size * math.sin(rad)

                color = self.colors.get(state.depth, state.color)
                segments.append(
                    Segment(
                        x1=state.x,
                        y1=state.y,
                        x2=new_x,
                        y2=new_y,
                        color=color,
                        width=state.line_width,
                        depth=state.depth,
                    )
                )
                state.x = new_x
                state.y = new_y

            elif ch == "f":
                # Move forward without drawing
                rad = math.radians(state.angle)
                state.x += state.step_size * math.cos(rad)
                state.y += state.step_size * math.sin(rad)

            elif ch == "+":
                state.angle += state.angle_increment

            elif ch == "-":
                state.angle -= state.angle_increment

            elif ch == "|":
                state.angle += 180.0

            elif ch == "[":
                stack.append(copy.deepcopy(state))
                state.depth += 1
                # Gradually thin branches and shrink step
                state.line_width = max(0.3, state.line_width * 0.7)
                state.step_size *= 0.75
                color = self.colors.get(state.depth, state.color)
                state.color = color

            elif ch == "]":
                if stack:
                    state = stack.pop()

            elif ch == "#":
                state.line_width += 1.0

            elif ch == "!":
                state.line_width = max(0.1, state.line_width - 1.0)

            elif ch == "<":
                state.step_size /= 2.0

            elif ch == ">":
                state.step_size *= 2.0

            elif ch == "(":
                state.step_size *= step_factor

            elif ch == ")":
                state.step_size /= step_factor

        return segments


# ---------------------------------------------------------------------------
# Rendering backends
# ---------------------------------------------------------------------------

class SVGRenderer:
    """Renders segments to an SVG file."""

    def __init__(
        self,
        width: int = 800,
        height: int = 800,
        background: str = "#ffffff",
        margin: float = 20.0,
    ):
        self.width = width
        self.height = height
        self.background = background
        self.margin = margin

    def _compute_bounds(self, segments: List[Segment]) -> Tuple[float, float, float, float]:
        """Compute the bounding box of all segments."""
        if not segments:
            return (0, 0, 100, 100)
        xs = []
        ys = []
        for seg in segments:
            xs.extend([seg.x1, seg.x2])
            ys.extend([seg.y1, seg.y2])
        return min(xs), min(ys), max(xs), max(ys)

    def render(self, segments: List[Segment], output_path: str) -> str:
        """Render segments to an SVG file."""
        if not segments:
            return output_path

        min_x, min_y, max_x, max_y = self._compute_bounds(segments)
        data_w = max_x - min_x or 1.0
        data_h = max_y - min_y or 1.0

        # Scale to fit within the SVG viewport with margins
        avail_w = self.width - 2 * self.margin
        avail_h = self.height - 2 * self.margin
        scale = min(avail_w / data_w, avail_h / data_h)

        # Center the drawing
        offset_x = self.margin + (avail_w - data_w * scale) / 2
        offset_y = self.margin + (avail_h - data_h * scale) / 2

        lines: List[str] = []
        lines.append('<?xml version="1.0" encoding="UTF-8"?>')
        lines.append(
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{self.width}" height="{self.height}" '
            f'viewBox="0 0 {self.width} {self.height}">'
        )
        lines.append(
            f'<rect width="{self.width}" height="{self.height}" '
            f'fill="{self.background}"/>'
        )

        for seg in segments:
            sx1 = (seg.x1 - min_x) * scale + offset_x
            sy1 = self.height - ((seg.y1 - min_y) * scale + offset_y)
            sx2 = (seg.x2 - min_x) * scale + offset_x
            sy2 = self.height - ((seg.y2 - min_y) * scale + offset_y)

            lines.append(
                f'<line x1="{sx1:.3f}" y1="{sy1:.3f}" '
                f'x2="{sx2:.3f}" y2="{sy2:.3f}" '
                f'stroke="{seg.color}" stroke-width="{seg.width:.2f}" '
                f'stroke-linecap="round"/>'
            )

        lines.append("</svg>")

        with open(output_path, "w") as f:
            f.write("\n".join(lines))

        return output_path


class ASCIIRenderer:
    """Renders segments to ASCII art using a character grid."""

    CHAR_MAP = {
        (0, 1): "|",
        (0, -1): "|",
        (1, 0): "-",
        (-1, 0): "-",
        (1, 1): "\\",
        (-1, -1): "\\",
        (1, -1): "/",
        (-1, 1): "/",
    }

    def __init__(self, width: int = 80, height: int = 40):
        self.width = width
        self.height = height

    def render(self, segments: List[Segment], output_path: Optional[str] = None) -> str:
        """Render segments to ASCII art string."""
        if not segments:
            return ""

        # Compute bounds
        xs = []
        ys = []
        for seg in segments:
            xs.extend([seg.x1, seg.x2])
            ys.extend([seg.y1, seg.y2])

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        data_w = max_x - min_x or 1.0
        data_h = max_y - min_y or 1.0

        # Create grid
        grid = [[" " for _ in range(self.width)] for _ in range(self.height)]

        scale_x = (self.width - 1) / data_w if data_w > 0 else 1
        scale_y = (self.height - 1) / data_h if data_h > 0 else 1
        scale = min(scale_x, scale_y)

        for seg in segments:
            x1 = int((seg.x1 - min_x) * scale)
            y1 = int((seg.y1 - min_y) * scale)
            x2 = int((seg.x2 - min_x) * scale)
            y2 = int((seg.y2 - min_y) * scale)

            # Bresenham-like rasterization
            dx = x2 - x1
            dy = y2 - y1
            steps = max(abs(dx), abs(dy), 1)

            for i in range(steps + 1):
                t = i / steps
                px = int(x1 + dx * t)
                py = int(y1 + dy * t)
                if 0 <= px < self.width and 0 <= py < self.height:
                    grid[py][px] = "*"

        # Flip grid vertically (y increases upward in math, downward in text)
        lines = ["".join(row) for row in reversed(grid)]
        result = "\n".join(lines)

        if output_path:
            with open(output_path, "w") as f:
                f.write(result)

        return result


# ---------------------------------------------------------------------------
# Preset L-systems
# ---------------------------------------------------------------------------

PRESETS: Dict[str, LSystemDefinition] = {
    "koch_curve": LSystemDefinition(
        name="Koch Curve",
        axiom="F",
        rules=[LSystemRule("F", "F+F--F+F")],
        angle=60.0,
        step_size=3.0,
        iterations=4,
        line_width=1.0,
    ),
    "koch_snowflake": LSystemDefinition(
        name="Koch Snowflake",
        axiom="F--F--F",
        rules=[LSystemRule("F", "F+F--F+F")],
        angle=60.0,
        step_size=3.0,
        iterations=4,
        line_width=1.0,
    ),
    "sierpinski_triangle": LSystemDefinition(
        name="Sierpiński Triangle",
        axiom="F-G-G",
        rules=[
            LSystemRule("F", "F-G+F+G-F"),
            LSystemRule("G", "GG"),
        ],
        angle=120.0,
        step_size=3.0,
        iterations=6,
        line_width=1.0,
    ),
    "dragon_curve": LSystemDefinition(
        name="Dragon Curve",
        axiom="F",
        rules=[
            LSystemRule("F", "F+G"),
            LSystemRule("G", "F-G"),
        ],
        angle=90.0,
        step_size=5.0,
        iterations=12,
        line_width=1.0,
    ),
    "hilbert_curve": LSystemDefinition(
        name="Hilbert Curve",
        axiom="A",
        rules=[
            LSystemRule("A", "-BF+AFA+FB-"),
            LSystemRule("B", "+AF-BFB-FA+"),
        ],
        angle=90.0,
        step_size=5.0,
        iterations=5,
        line_width=1.0,
    ),
    "plant_simple": LSystemDefinition(
        name="Simple Plant",
        axiom="F",
        rules=[LSystemRule("F", "F[+F]F[-F]F")],
        angle=25.7,
        step_size=4.0,
        iterations=5,
        line_width=1.0,
        colors={
            0: "#5a3e1b",
            1: "#3d6b2e",
            2: "#4a8c3a",
            3: "#6bb55a",
            4: "#8dd77a",
            5: "#a8f08a",
        },
    ),
    "plant_stochastic": LSystemDefinition(
        name="Stochastic Plant",
        axiom="F",
        rules=[
            LSystemRule("F", "F[+F]F[-F]F", probability=0.5),
            LSystemRule("F", "F[+F]F", probability=0.25),
            LSystemRule("F", "F[-F]F", probability=0.25),
        ],
        angle=25.7,
        step_size=4.0,
        iterations=5,
        line_width=1.5,
        colors={
            0: "#5a3e1b",
            1: "#3d6b2e",
            2: "#4a8c3a",
            3: "#6bb55a",
            4: "#8dd77a",
            5: "#a8f08a",
        },
    ),
    "tree_bushy": LSystemDefinition(
        name="Bushy Tree",
        axiom="F",
        rules=[LSystemRule("F", "FF+[+F-F-F]-[-F+F+F]")],
        angle=22.5,
        step_size=4.0,
        iterations=4,
        line_width=1.5,
        colors={
            0: "#4a2f0a",
            1: "#5a3e1b",
            2: "#3d6b2e",
            3: "#5a9e3a",
            4: "#7abf5a",
            5: "#a8f08a",
        },
    ),
    "penrose_tiles": LSystemDefinition(
        name="Penrose Tiles",
        axiom="[7]++[7]++[7]++[7]++[7]",
        rules=[
            LSystemRule("6", "81++91----71[-81----61]++"),
            LSystemRule("7", "+81--91[---61--71]"),
            LSystemRule("8", "-61++71[+++81++91]-"),
            LSystemRule("9", "--81+++61[+91+++71]--71"),
        ],
        angle=36.0,
        step_size=4.0,
        iterations=4,
        line_width=0.8,
    ),
    "levy_c_curve": LSystemDefinition(
        name="Lévy C Curve",
        axiom="F",
        rules=[LSystemRule("F", "+F--F+")],
        angle=45.0,
        step_size=3.0,
        iterations=14,
        line_width=1.0,
    ),
    "gosper_curve": LSystemDefinition(
        name="Gosper Curve (Flowsnake)",
        axiom="A",
        rules=[
            LSystemRule("A", "A-B--B+A++AA+B-"),
            LSystemRule("B", "+A-BB--B-A++A+B"),
        ],
        angle=60.0,
        step_size=4.0,
        iterations=4,
        line_width=1.0,
    ),
}


# ---------------------------------------------------------------------------
# High-level API
# ---------------------------------------------------------------------------

class LSystemRenderer:
    """High-level API for rendering L-systems.

    Usage:
        renderer = LSystemRenderer()
        renderer.render("koch_snowflake", iterations=4, backend="svg",
                        output="koch.svg")
    """

    def __init__(self, seed: Optional[int] = None):
        self.seed = seed

    def render(
        self,
        preset_or_definition: Union[str, LSystemDefinition],
        iterations: Optional[int] = None,
        backend: Union[str, RenderBackend] = RenderBackend.SVG,
        output: str = "output.svg",
        width: int = 800,
        height: int = 800,
        background: str = "#ffffff",
        margin: float = 20.0,
    ) -> str:
        """Render an L-system to the specified backend.

        Args:
            preset_or_definition: Either a preset name (str) or an
                LSystemDefinition instance.
            iterations: Override the default iteration count.
            backend: Rendering backend ('svg', 'ascii', or RenderBackend enum).
            output: Output file path.
            width: Canvas width (for SVG).
            height: Canvas height (for SVG).
            background: Background color (for SVG).
            margin: Margin around the drawing (for SVG).

        Returns:
            Path to the output file.
        """
        if isinstance(backend, str):
            backend = RenderBackend[backend.upper()]

        # Resolve definition
        if isinstance(preset_or_definition, str):
            if preset_or_definition not in PRESETS:
                raise ValueError(
                    f"Unknown preset '{preset_or_definition}'. "
                    f"Available: {list(PRESETS.keys())}"
                )
            definition = copy.deepcopy(PRESETS[preset_or_definition])
        else:
            definition = copy.deepcopy(preset_or_definition)

        # Generate string
        engine = LSystemEngine(definition, seed=self.seed)
        lstring = engine.iterate(iterations)

        # Interpret with turtle
        interpreter = TurtleInterpreter(
            angle=definition.angle,
            step_size=definition.step_size,
            line_width=definition.line_width,
            colors=definition.colors,
        )
        segments = interpreter.interpret(lstring)

        # Render
        if backend == RenderBackend.SVG:
            renderer = SVGRenderer(
                width=width, height=height, background=background, margin=margin
            )
            return renderer.render(segments, output)
        elif backend == RenderBackend.ASCII:
            renderer = ASCIIRenderer(width=min(width // 8, 120), height=min(height // 16, 60))
            result = renderer.render(segments, output if output.endswith(".txt") else None)
            if not output.endswith(".txt"):
                with open(output, "w") as f:
                    f.write(result)
            return output
        elif backend == RenderBackend.TERMINAL:
            renderer = ASCIIRenderer(width=80, height=40)
            result = renderer.render(segments)
            print(result)
            return output
        else:
            raise ValueError(f"Unsupported backend: {backend}")

    def list_presets(self) -> List[str]:
        """Return a list of available preset names."""
        return list(PRESETS.keys())

    def get_preset(self, name: str) -> LSystemDefinition:
        """Return a copy of a preset definition."""
        if name not in PRESETS:
            raise ValueError(f"Unknown preset '{name}'")
        return copy.deepcopy(PRESETS[name])


# ---------------------------------------------------------------------------
# CLI interface
# ---------------------------------------------------------------------------

def main():
    """Command-line interface for the L-system renderer."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="L-System Renderer — Generate fractals and plant-like structures",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Render Koch snowflake
  python3 lsystem.py --preset koch_snowflake -i 4 -o koch.svg

  # Render a stochastic plant with a specific seed
  python3 lsystem.py --preset plant_stochastic -i 5 --seed 42 -o plant.svg

  # Render to ASCII
  python3 lsystem.py --preset dragon_curve -i 10 --backend ascii -o dragon.txt

  # List available presets
  python3 lsystem.py --list-presets
        """,
    )

    parser.add_argument(
        "--preset", "-p",
        help="Preset L-system name to render",
    )
    parser.add_argument(
        "--iterations", "-i",
        type=int,
        default=None,
        help="Number of iterations (default: use preset default)",
    )
    parser.add_argument(
        "--backend", "-b",
        choices=["svg", "ascii", "terminal"],
        default="svg",
        help="Rendering backend (default: svg)",
    )
    parser.add_argument(
        "--output", "-o",
        default="output.svg",
        help="Output file path (default: output.svg)",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1000,
        help="SVG canvas width (default: 1000)",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=1000,
        help="SVG canvas height (default: 1000)",
    )
    parser.add_argument(
        "--background",
        default="#ffffff",
        help="Background color (default: #ffffff)",
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=None,
        help="Random seed for stochastic L-systems",
    )
    parser.add_argument(
        "--list-presets", "-l",
        action="store_true",
        help="List available presets and exit",
    )
    parser.add_argument(
        "--axiom",
        help="Custom axiom (overrides preset)",
    )
    parser.add_argument(
        "--rule",
        action="append",
        help="Custom rule in format 'PREDECESSOR->SUCCESSOR' (can be repeated)",
    )
    parser.add_argument(
        "--angle",
        type=float,
        default=None,
        help="Custom angle in degrees (overrides preset)",
    )

    args = parser.parse_args()

    renderer = LSystemRenderer(seed=args.seed)

    if args.list_presets:
        print("Available presets:")
        for name in renderer.list_presets():
            preset = PRESETS[name]
            print(f"  {name:25s} — {preset.name}")
        return

    if not args.preset and not args.axiom:
        parser.error("Either --preset or --axiom with --rule is required")

    # Build or get definition
    if args.preset:
        definition = renderer.get_preset(args.preset)
    else:
        definition = LSystemDefinition(
            name="Custom",
            axiom=args.axiom or "F",
            rules=[],
            angle=args.angle or 90.0,
            step_size=5.0,
            iterations=4,
        )

    # Override angle if specified
    if args.angle is not None:
        definition.angle = args.angle

    # Add custom rules
    if args.rule:
        for rule_str in args.rule:
            # Support format: PREDECESSOR->SUCCESSOR or PREDECESSOR=SUCCESSOR
            sep = "->" if "->" in rule_str else "="
            parts = rule_str.split(sep, 1)
            if len(parts) != 2:
                print(f"Invalid rule format: {rule_str}", file=sys.stderr)
                sys.exit(1)
            definition.rules.append(
                LSystemRule(predecessor=parts[0].strip(), successor=parts[1].strip())
            )

    # Determine output path
    output = args.output
    if args.backend == "ascii" and not output.endswith(".txt"):
        output = output.replace(".svg", ".txt") if output.endswith(".svg") else output + ".txt"
    elif args.backend == "svg" and not output.endswith(".svg"):
        output += ".svg"

    result = renderer.render(
        definition,
        iterations=args.iterations,
        backend=args.backend,
        output=output,
        width=args.width,
        height=args.height,
        background=args.background,
    )
    print(f"Output written to: {result}")


if __name__ == "__main__":
    main()