"""
High-level L-System Renderer API.

Provides the main LSystemRenderer class that orchestrates the full
pipeline: definition → engine → interpreter → color → renderer.
"""

from __future__ import annotations

import copy
import logging
import os
from typing import Dict, List, Optional, Tuple, Union

from .types import (
    LSystemDefinition,
    LSystemRule,
    RenderBackend,
    Segment,
)
from .engine import LSystemEngine
from .interpreter import TurtleInterpreter
from .color_postprocessor import ColorPostProcessor
from .presets import PRESETS
from ..renderers.svg import SVGRenderer
from ..renderers.ascii import ASCIIRenderer
from ..renderers.png import PNGRenderer
from ..renderers.pdf import PDFRenderer
from ..renderers.grid import GridRenderer
from ..core.config import LSystemConfig
from ..utils.svg_optimizer import optimize_svg, merge_svg_paths

logger = logging.getLogger(__name__)


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
        background: Optional[str] = None,
        margin: float = 20.0,
        animate: bool = False,
        animation_duration: float = 5.0,
    ) -> str:
        """Render an L-system to the specified backend.

        Args:
            preset_or_definition: Either a preset name (str) or an
                LSystemDefinition instance.
            iterations: Override the default iteration count.
            backend: Rendering backend ('svg', 'ascii', 'png', or RenderBackend enum).
            output: Output file path.
            width: Canvas width (for SVG/PNG).
            height: Canvas height (for SVG/PNG).
            background: Background color (overrides definition).
            margin: Margin around the drawing (for SVG).
            animate: If True and backend=SVG, generate animation.
            animation_duration: Duration of animation in seconds.

        Returns:
            Path to the output file.
        """
        if isinstance(backend, str):
            try:
                backend = RenderBackend[backend.upper()]
            except KeyError:
                valid = [b.name.lower() for b in RenderBackend]
                raise ValueError(
                    f"Unknown backend '{backend}'. Valid: {', '.join(valid)}"
                )

        # Resolve definition
        if isinstance(preset_or_definition, str):
            if preset_or_definition not in PRESETS:
                available = ", ".join(sorted(PRESETS.keys()))
                raise ValueError(
                    f"Unknown preset '{preset_or_definition}'. "
                    f"Available presets: {available}"
                )
            definition = copy.deepcopy(PRESETS[preset_or_definition])
        else:
            definition = copy.deepcopy(preset_or_definition)

        # Override background if provided
        if background is not None:
            definition.background = background

        # Generate string
        engine = LSystemEngine(definition, seed=self.seed)
        lstring = engine.iterate(iterations)
        logger.info("Generated L-string of length %d", len(lstring))

        # Interpret with turtle
        interpreter = TurtleInterpreter(
            angle=definition.angle,
            step_size=definition.step_size,
            line_width=definition.line_width,
            colors=definition.colors,
            perturbation=definition.perturbation,
            step_perturbation=definition.step_perturbation,
            seed=self.seed,
        )
        segments = interpreter.interpret(lstring)
        logger.info("Interpreted %d segments", len(segments))

        # Apply color post-processing
        segments = ColorPostProcessor.apply(
            segments,
            color_mode=definition.color_mode,
            colors=definition.colors,
            gradient=definition.gradient,
        )

        # Render
        if backend == RenderBackend.SVG:
            renderer = SVGRenderer(
                width=width,
                height=height,
                background=definition.background,
                margin=margin,
                title=definition.name,
            )
            return renderer.render(segments, output, animate=animate,
                                   animation_duration=animation_duration)
        elif backend == RenderBackend.ASCII:
            renderer = ASCIIRenderer(
                width=min(width // 8, 120),
                height=min(height // 16, 60)
            )
            result = renderer.render(segments)
            actual_output = output
            if not actual_output.endswith(".txt"):
                # Replace extension or append .txt
                if "." in os.path.basename(actual_output):
                    actual_output = actual_output.rsplit(".", 1)[0] + ".txt"
                else:
                    actual_output += ".txt"
            with open(actual_output, "w") as f:
                f.write(result)
            return actual_output
        elif backend == RenderBackend.PNG:
            png_renderer = PNGRenderer(
                width=width,
                height=height,
                background=definition.background,
                margin=margin,
            )
            return png_renderer.render(segments, output)
        elif backend == RenderBackend.PDF:
            pdf_renderer = PDFRenderer(
                width=width,
                height=height,
                background=definition.background,
                margin=margin,
                title=definition.name,
            )
            return pdf_renderer.render(segments, output)
        elif backend == RenderBackend.TERMINAL:
            renderer = ASCIIRenderer(width=80, height=40)
            result = renderer.render(segments)
            print(result)
            return output
        else:
            raise ValueError(f"Unsupported backend: {backend}")

    def render_all_presets(
        self,
        output_dir: str = ".",
        iterations: Optional[int] = None,
        backend: str = "svg",
        width: int = 800,
        height: int = 800,
    ) -> Dict[str, str]:
        """Render all presets to files in the given directory.

        Returns a dict mapping preset name -> output file path.
        """
        os.makedirs(output_dir, exist_ok=True)
        results = {}
        for name in self.list_presets():
            definition = self.get_preset(name)
            ext = "svg" if backend == "svg" else ("png" if backend == "png" else "txt")
            output_path = os.path.join(output_dir, f"{name}.{ext}")
            try:
                path = self.render(
                    definition,
                    iterations=iterations,
                    backend=backend,
                    output=output_path,
                    width=width,
                    height=height,
                )
                results[name] = path
            except Exception as e:
                logger.error("Failed to render preset '%s': %s", name, e)
                results[name] = f"ERROR: {e}"
        return results

    def animate_growth(
        self,
        preset_or_definition: Union[str, LSystemDefinition],
        output_dir: str = ".",
        iterations: Optional[int] = None,
        width: int = 800,
        height: int = 800,
    ) -> List[str]:
        """Render each iteration step as a separate SVG file.

        Creates files named step_0.svg, step_1.svg, etc.
        Useful for creating growth animations.

        Returns list of output file paths.
        """
        os.makedirs(output_dir, exist_ok=True)

        if isinstance(preset_or_definition, str):
            definition = self.get_preset(preset_or_definition)
        else:
            definition = copy.deepcopy(preset_or_definition)

        engine = LSystemEngine(definition, seed=self.seed)
        steps = engine.iterate_steps(iterations)

        paths = []
        for i, lstring in enumerate(steps):
            interpreter = TurtleInterpreter(
                angle=definition.angle,
                step_size=definition.step_size,
                line_width=definition.line_width,
                colors=definition.colors,
                perturbation=definition.perturbation,
                step_perturbation=definition.step_perturbation,
                seed=self.seed,
            )
            segments = interpreter.interpret(lstring)
            segments = ColorPostProcessor.apply(
                segments,
                color_mode=definition.color_mode,
                colors=definition.colors,
                gradient=definition.gradient,
            )

            svg_renderer = SVGRenderer(
                width=width, height=height,
                background=definition.background,
                title=f"{definition.name} — Step {i}",
            )
            path = os.path.join(output_dir, f"step_{i}.svg")
            svg_renderer.render(segments, path)
            paths.append(path)

        logger.info("Generated %d growth step files", len(paths))
        return paths

    def render_gallery_grid(
        self,
        output_path: str = "gallery.svg",
        iterations: int = 2,
        cell_width: int = 300,
        cell_height: int = 300,
        columns: int = 4,
        seed: Optional[int] = None,
    ) -> str:
        """Render all presets as a tiled grid in a single SVG.

        Args:
            output_path: Path to write the output SVG file.
            iterations: Number of iterations per preset.
            cell_width: Width of each cell in pixels.
            cell_height: Height of each cell in pixels.
            columns: Number of columns in the grid.
            seed: Random seed for stochastic L-systems.

        Returns:
            Path to the output file.
        """
        import copy
        definitions = {name: copy.deepcopy(defn) for name, defn in PRESETS.items()}
        grid = GridRenderer(
            cell_width=cell_width,
            cell_height=cell_height,
            columns=columns,
        )
        return grid.render_grid(definitions, output_path, iterations=iterations, seed=seed)

    def render_optimized(
        self,
        preset_or_definition: Union[str, LSystemDefinition],
        iterations: Optional[int] = None,
        output: str = "output.svg",
        width: int = 800,
        height: int = 800,
        background: Optional[str] = None,
        margin: float = 20.0,
    ) -> str:
        """Render an L-system to an optimized (smaller) SVG file.

        Like render() but applies SVG optimization (whitespace removal,
        float truncation, path merging) to reduce file size.

        Args:
            preset_or_definition: Preset name or LSystemDefinition.
            iterations: Override default iteration count.
            output: Output file path.
            width: Canvas width.
            height: Canvas height.
            background: Background color override.
            margin: Margin around the drawing.

        Returns:
            Path to the output file.
        """
        # Resolve definition
        if isinstance(preset_or_definition, str):
            if preset_or_definition not in PRESETS:
                available = ", ".join(sorted(PRESETS.keys()))
                raise ValueError(
                    f"Unknown preset '{preset_or_definition}'. "
                    f"Available presets: {available}"
                )
            definition = copy.deepcopy(PRESETS[preset_or_definition])
        else:
            definition = copy.deepcopy(preset_or_definition)

        if background is not None:
            definition.background = background

        # Generate and interpret
        engine = LSystemEngine(definition, seed=self.seed)
        lstring = engine.iterate(iterations)

        interpreter = TurtleInterpreter(
            angle=definition.angle,
            step_size=definition.step_size,
            line_width=definition.line_width,
            colors=definition.colors,
            perturbation=definition.perturbation,
            step_perturbation=definition.step_perturbation,
            seed=self.seed,
        )
        segments = interpreter.interpret(lstring)
        segments = ColorPostProcessor.apply(
            segments,
            color_mode=definition.color_mode,
            colors=definition.colors,
            gradient=definition.gradient,
        )

        # Render to SVG string, then optimize
        svg_renderer = SVGRenderer(
            width=width,
            height=height,
            background=definition.background,
            margin=margin,
            title=definition.name,
        )

        # Render to file, then read back, optimize, and rewrite
        svg_renderer.render(segments, output)
        with open(output, "r") as f:
            svg_content = f.read()

        optimized = optimize_svg(svg_content, precision=2)
        optimized = merge_svg_paths(optimized)

        with open(output, "w") as f:
            f.write(optimized)

        logger.info("Optimized SVG written to %s", output)
        return output

    def list_presets(self) -> List[str]:
        """Return a list of available preset names."""
        return list(PRESETS.keys())

    def get_preset(self, name: str) -> LSystemDefinition:
        """Return a copy of a preset definition."""
        if name not in PRESETS:
            available = ", ".join(sorted(PRESETS.keys()))
            raise ValueError(f"Unknown preset '{name}'. Available: {available}")
        return copy.deepcopy(PRESETS[name])

    def render_from_config(self, config: LSystemConfig) -> str:
        """Render using a configuration object.

        Args:
            config: LSystemConfig with all rendering parameters.

        Returns:
            Path to the output file.
        """
        if config.preset:
            target = config.preset
        elif config.definition:
            target = config.definition
        else:
            raise ValueError("Config must specify either 'preset' or 'definition'")

        output_dir = config.output.output_dir
        os.makedirs(output_dir, exist_ok=True)

        ext = config.backend
        name = config.preset or config.definition.name if config.definition else "output"
        safe_name = name.lower().replace(" ", "_").replace("(", "").replace(")", "")
        output_path = os.path.join(output_dir, f"{safe_name}.{ext}")

        return self.render(
            target,
            iterations=config.iterations,
            backend=config.backend,
            output=output_path,
            width=config.render.width,
            height=config.render.height,
            background=config.render.background,
            margin=config.render.margin,
            animate=config.render.animate,
            animation_duration=config.render.animation_duration,
        )