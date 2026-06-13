"""
Core data types for the L-System Renderer.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple


class RenderBackend(Enum):
    """Available rendering backends."""
    SVG = auto()
    ASCII = auto()
    TERMINAL = auto()
    PNG = auto()
    PDF = auto()


class ColorMode(Enum):
    """Determines how segments are colored."""
    DEPTH = auto()          # Color by turtle stack depth
    POSITION = auto()       # Color by normalized position (gradient)
    SEGMENT_INDEX = auto()  # Color by segment order (rainbow)
    SINGLE = auto()         # Single color for all segments

    @classmethod
    def from_string(cls, s: str) -> "ColorMode":
        """Convert a string to a ColorMode enum value."""
        mapping = {
            "depth": cls.DEPTH,
            "position": cls.POSITION,
            "segment_index": cls.SEGMENT_INDEX,
            "single": cls.SINGLE,
        }
        s_lower = s.lower().strip()
        if s_lower not in mapping:
            raise ValueError(
                f"Unknown color mode '{s}'. "
                f"Valid modes: {', '.join(mapping.keys())}"
            )
        return mapping[s_lower]

    def to_string(self) -> str:
        """Convert to string representation."""
        return self.name.lower()


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
    segment_index: int = 0  # Order index for color modes

    def length(self) -> float:
        """Compute the geometric length of this segment."""
        import math
        return math.sqrt((self.x2 - self.x1) ** 2 + (self.y2 - self.y1) ** 2)

    def midpoint(self) -> Tuple[float, float]:
        """Return the midpoint of this segment."""
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)

    def direction_deg(self) -> float:
        """Return the direction angle of this segment in degrees."""
        import math
        return math.degrees(math.atan2(self.y2 - self.y1, self.x2 - self.x1))


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

    def __post_init__(self) -> None:
        """Validate rule fields after initialization."""
        if not self.predecessor:
            raise ValueError("Rule predecessor must be a non-empty string")
        if not self.successor:
            raise ValueError("Rule successor must be a non-empty string")
        if self.probability <= 0:
            raise ValueError(
                f"Rule probability must be positive, got {self.probability}"
            )

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        d = {
            "predecessor": self.predecessor,
            "successor": self.successor,
        }
        if self.condition is not None:
            d["condition"] = self.condition
        if self.probability != 1.0:
            d["probability"] = self.probability
        if self.left_context is not None:
            d["left_context"] = self.left_context
        if self.right_context is not None:
            d["right_context"] = self.right_context
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "LSystemRule":
        """Deserialize from dictionary."""
        return cls(
            predecessor=d["predecessor"],
            successor=d["successor"],
            condition=d.get("condition"),
            probability=d.get("probability", 1.0),
            left_context=d.get("left_context"),
            right_context=d.get("right_context"),
        )

    @classmethod
    def parse(cls, rule_str: str) -> "LSystemRule":
        """Parse a rule from a string like 'F->F+F--F+F' or 'F=F+F'.

        Supports '->' and '=' as separators.
        """
        sep = "->" if "->" in rule_str else "="
        parts = rule_str.split(sep, 1)
        if len(parts) != 2:
            raise ValueError(
                f"Invalid rule format: '{rule_str}'. "
                f"Use 'PREDECESSOR->SUCCESSOR' format."
            )
        return cls(
            predecessor=parts[0].strip(),
            successor=parts[1].strip(),
        )


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
        color_mode: How to assign colors to segments.
        gradient: Optional (start_color, end_color) for position/segment gradients.
        perturbation: Std deviation of random angle perturbation in degrees (0 = none).
        step_perturbation: Std deviation of random step size perturbation (0 = none).
        background: Background color for rendering.
    """
    name: str
    axiom: str
    rules: List[LSystemRule]
    angle: float = 25.0
    step_size: float = 5.0
    iterations: int = 4
    line_width: float = 1.0
    colors: Dict[int, str] = field(default_factory=dict)
    color_mode: str = "depth"  # "depth", "position", "segment_index", "single"
    gradient: Optional[Tuple[str, str]] = None  # (start_color, end_color)
    perturbation: float = 0.0
    step_perturbation: float = 0.0
    background: str = "#ffffff"

    def __post_init__(self) -> None:
        """Validate definition fields after initialization."""
        if not self.name:
            raise ValueError("L-system name must be a non-empty string")
        if self.iterations < 0:
            raise ValueError(
                f"Iterations must be non-negative, got {self.iterations}"
            )
        if self.angle < 0 or self.angle > 360:
            raise ValueError(
                f"Angle must be in [0, 360], got {self.angle}"
            )
        if self.step_size <= 0:
            raise ValueError(
                f"Step size must be positive, got {self.step_size}"
            )
        # Validate color_mode
        valid_modes = {"depth", "position", "segment_index", "single"}
        if self.color_mode not in valid_modes:
            raise ValueError(
                f"Invalid color_mode '{self.color_mode}'. "
                f"Valid modes: {', '.join(sorted(valid_modes))}"
            )

    def to_dict(self) -> dict:
        """Serialize to a JSON-compatible dictionary."""
        d = {
            "name": self.name,
            "axiom": self.axiom,
            "rules": [r.to_dict() for r in self.rules],
            "angle": self.angle,
            "step_size": self.step_size,
            "iterations": self.iterations,
            "line_width": self.line_width,
        }
        if self.colors:
            # JSON keys must be strings
            d["colors"] = {str(k): v for k, v in self.colors.items()}
        d["color_mode"] = self.color_mode
        if self.gradient:
            d["gradient"] = list(self.gradient)
        if self.perturbation != 0.0:
            d["perturbation"] = self.perturbation
        if self.step_perturbation != 0.0:
            d["step_perturbation"] = self.step_perturbation
        if self.background != "#ffffff":
            d["background"] = self.background
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "LSystemDefinition":
        """Deserialize from dictionary."""
        colors_raw = d.get("colors", {})
        colors = {int(k): v for k, v in colors_raw.items()} if colors_raw else {}
        gradient_raw = d.get("gradient")
        gradient = tuple(gradient_raw) if gradient_raw else None
        return cls(
            name=d["name"],
            axiom=d["axiom"],
            rules=[LSystemRule.from_dict(r) for r in d.get("rules", [])],
            angle=d.get("angle", 25.0),
            step_size=d.get("step_size", 5.0),
            iterations=d.get("iterations", 4),
            line_width=d.get("line_width", 1.0),
            colors=colors,
            color_mode=d.get("color_mode", "depth"),
            gradient=gradient,
            perturbation=d.get("perturbation", 0.0),
            step_perturbation=d.get("step_perturbation", 0.0),
            background=d.get("background", "#ffffff"),
        )

    def to_json(self, path: str) -> None:
        """Save definition to a JSON file."""
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def from_json(cls, path: str) -> "LSystemDefinition":
        """Load definition from a JSON file."""
        with open(path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)