"""
L-System Renderer — A formal grammar-based generative art engine.

Implements Lindenmayer Systems (L-systems) with multiple rendering backends,
advanced coloring, animation, and a comprehensive Python + CLI interface.
"""

__version__ = "2.0.0"
__author__ = "lsystem-renderer contributors"

from .core.types import (
    RenderBackend,
    ColorMode,
    TurtleState,
    Segment,
    LSystemRule,
    LSystemDefinition,
)
from .core.engine import LSystemEngine
from .core.interpreter import TurtleInterpreter
from .core.color_postprocessor import ColorPostProcessor
from .renderers.svg import SVGRenderer
from .renderers.ascii import ASCIIRenderer
from .renderers.png import PNGRenderer
from .core.renderer import LSystemRenderer
from .utils.colors import (
    hex_to_rgb,
    rgb_to_hex,
    lerp_color,
    hsl_to_rgb,
    rainbow_color,
    _escape_xml,
)
from .core.presets import PRESETS
from .core.config import LSystemConfig

__all__ = [
    "RenderBackend",
    "ColorMode",
    "TurtleState",
    "Segment",
    "LSystemRule",
    "LSystemDefinition",
    "LSystemEngine",
    "TurtleInterpreter",
    "ColorPostProcessor",
    "SVGRenderer",
    "ASCIIRenderer",
    "PNGRenderer",
    "LSystemRenderer",
    "LSystemConfig",
    "hex_to_rgb",
    "rgb_to_hex",
    "lerp_color",
    "hsl_to_rgb",
    "rainbow_color",
    "_escape_xml",
    "PRESETS",
]