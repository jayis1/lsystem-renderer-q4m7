"""
L-System Renderer — A formal grammar-based generative art engine.

Implements Lindenmayer Systems (L-systems) with multiple rendering backends,
advanced coloring, animation, and a comprehensive Python + CLI interface.
"""

__version__ = "3.0.0"
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
from .renderers.pdf import PDFRenderer
from .renderers.grid import GridRenderer
from .core.renderer import LSystemRenderer
from .utils.colors import (
    hex_to_rgb,
    rgb_to_hex,
    lerp_color,
    hsl_to_rgb,
    rainbow_color,
    _escape_xml,
)
from .utils.svg_optimizer import optimize_svg, merge_svg_paths, stats_svg
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
    "PDFRenderer",
    "GridRenderer",
    "LSystemRenderer",
    "LSystemConfig",
    "hex_to_rgb",
    "rgb_to_hex",
    "lerp_color",
    "hsl_to_rgb",
    "rainbow_color",
    "_escape_xml",
    "optimize_svg",
    "merge_svg_paths",
    "stats_svg",
    "PRESETS",
]