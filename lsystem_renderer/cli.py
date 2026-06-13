"""
Command-line interface for the L-System Renderer.

Provides a full-featured argparse CLI with support for presets,
custom definitions, multiple backends, animation, and more.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from typing import List, Optional

from .core.types import LSystemDefinition, LSystemRule
from .core.engine import LSystemEngine
from .core.renderer import LSystemRenderer
from .core.presets import PRESETS
from .core.config import LSystemConfig

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the CLI."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="lsystem-renderer",
        description="L-System Renderer — Generate fractals and plant-like structures",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Render Koch snowflake
  lsystem-renderer --preset koch_snowflake -i 4 -o koch.svg

  # Render a stochastic plant with a specific seed
  lsystem-renderer --preset plant_stochastic -i 5 --seed 42 -o plant.svg

  # Render to ASCII
  lsystem-renderer --preset dragon_curve -i 10 --backend ascii -o dragon.txt

  # Render all presets
  lsystem-renderer --render-all -d ./output

  # Animate growth steps
  lsystem-renderer --preset koch_snowflake --animate-steps -d ./growth

  # List available presets
  lsystem-renderer --list-presets

  # Custom L-system (Sierpinski arrowhead)
  lsystem-renderer --axiom "A" --rule "A->B-A-B" --rule "B->A+B+A" --angle 60 -i 7 -o custom.svg

  # Load from JSON definition
  lsystem-renderer --load definition.json -o output.svg

  # Use a config file
  lsystem-renderer --config config.json

  # Render to PNG (requires Pillow)
  lsystem-renderer --preset dragon_curve -i 10 --backend png -o dragon.png

  # Verbose logging
  lsystem-renderer -v --preset koch_curve -i 3 -o koch.svg
        """,
    )

    # Definition source
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
        "--load",
        help="Load L-system definition from a JSON file",
    )
    parser.add_argument(
        "--config",
        help="Load rendering configuration from a JSON/YAML/TOML file",
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

    # Rendering options
    parser.add_argument(
        "--backend", "-b",
        choices=["svg", "ascii", "terminal", "png"],
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
        help="Canvas width (default: 1000)",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=1000,
        help="Canvas height (default: 1000)",
    )
    parser.add_argument(
        "--background",
        default=None,
        help="Background color (overrides preset default)",
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=None,
        help="Random seed for stochastic L-systems",
    )

    # Customization
    parser.add_argument(
        "--angle",
        type=float,
        default=None,
        help="Custom angle in degrees (overrides preset)",
    )
    parser.add_argument(
        "--step-size",
        type=float,
        default=None,
        help="Custom step size (overrides preset)",
    )
    parser.add_argument(
        "--line-width",
        type=float,
        default=None,
        help="Custom line width (overrides preset)",
    )
    parser.add_argument(
        "--color-mode",
        choices=["depth", "position", "segment_index", "single"],
        default=None,
        help="Color mode for rendering",
    )
    parser.add_argument(
        "--gradient",
        help="Gradient colors as 'start_color,end_color' (e.g. '#ff0000,#0000ff')",
    )
    parser.add_argument(
        "--perturbation",
        type=float,
        default=None,
        help="Angle perturbation (std dev in degrees) for organic variation",
    )

    # Actions
    parser.add_argument(
        "--list-presets", "-l",
        action="store_true",
        help="List available presets and exit",
    )
    parser.add_argument(
        "--render-all",
        action="store_true",
        help="Render all presets to output directory",
    )
    parser.add_argument(
        "--animate",
        action="store_true",
        help="Generate SVG animation (progressive draw)",
    )
    parser.add_argument(
        "--animate-steps",
        action="store_true",
        help="Render each iteration step as a separate SVG file",
    )
    parser.add_argument(
        "--directory", "-d",
        default=".",
        help="Output directory for --render-all and --animate-steps",
    )
    parser.add_argument(
        "--save",
        help="Save the resolved L-system definition to a JSON file (don't render)",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Print string statistics without rendering",
    )

    # Logging
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    """Main entry point for the CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    setup_logging(verbose=args.verbose)

    renderer = LSystemRenderer(seed=args.seed)

    # List presets
    if args.list_presets:
        print("Available presets:")
        for name in sorted(renderer.list_presets()):
            preset = PRESETS[name]
            print(f"  {name:25s} — {preset.name}")
        return

    # Render all presets — no definition needed
    if args.render_all:
        results = renderer.render_all_presets(
            output_dir=args.directory,
            iterations=args.iterations,
            backend=args.backend,
            width=args.width,
            height=args.height,
        )
        print("Rendered all presets:")
        for name, path in sorted(results.items()):
            print(f"  {name}: {path}")
        return

    # Load from config file
    if args.config:
        try:
            config = LSystemConfig.from_file(args.config)
            result = renderer.render_from_config(config)
            print(f"Output written to: {result}")
            return
        except Exception as e:
            print(f"Error loading config: {e}", file=sys.stderr)
            sys.exit(1)

    # Load from JSON or build definition
    if args.load:
        definition = LSystemDefinition.from_json(args.load)
    elif args.preset:
        definition = renderer.get_preset(args.preset)
    elif args.axiom:
        definition = LSystemDefinition(
            name="Custom",
            axiom=args.axiom,
            rules=[],
            angle=args.angle or 90.0,
            step_size=args.step_size or 5.0,
            iterations=args.iterations or 4,
            line_width=args.line_width or 1.0,
        )
    else:
        parser.error("One of --preset, --axiom, --load, or --config is required "
                     "(unless using --list-presets or --render-all)")

    # Apply CLI overrides
    if args.angle is not None:
        definition.angle = args.angle
    if args.step_size is not None:
        definition.step_size = args.step_size
    if args.line_width is not None:
        definition.line_width = args.line_width
    if args.color_mode is not None:
        definition.color_mode = args.color_mode
    if args.gradient is not None:
        parts = args.gradient.split(",")
        if len(parts) == 2:
            definition.gradient = (parts[0].strip(), parts[1].strip())
    if args.perturbation is not None:
        definition.perturbation = args.perturbation
    if args.background is not None:
        definition.background = args.background
    if args.iterations is not None:
        definition.iterations = args.iterations

    # Add custom rules
    if args.rule:
        for rule_str in args.rule:
            try:
                rule = LSystemRule.parse(rule_str)
                definition.rules.append(rule)
            except ValueError as e:
                print(f"Invalid rule: {e}", file=sys.stderr)
                sys.exit(1)

    # Save definition if requested
    if args.save:
        definition.to_json(args.save)
        print(f"Definition saved to: {args.save}")
        return

    # Stats mode
    if args.stats:
        engine = LSystemEngine(definition, seed=args.seed)
        lstring = engine.iterate()
        stats = LSystemEngine.analyze(lstring)
        print(f"L-System: {definition.name}")
        print(f"  Axiom: {definition.axiom[:60]}{'...' if len(definition.axiom) > 60 else ''}")
        print(f"  String length: {stats['length']:,}")
        print(f"  Drawing symbols (F/G): {stats['draw_symbols']:,}")
        print(f"  Unique symbols: {stats['unique_symbols']}")
        print(f"  Max branch depth: {stats.get('branch_depth', 'N/A')}")
        print(f"  Symbol breakdown:")
        # Sort by count descending
        for sym, count in sorted(stats['symbols'].items(), key=lambda x: -x[1])[:15]:
            pct = 100 * count / stats['length'] if stats['length'] > 0 else 0
            print(f"    '{sym}': {count:,} ({pct:.1f}%)")
        if stats['length'] > 15 * 1000:
            print("  (showing top 15 symbols)")
        return

    # Animate steps
    if args.animate_steps:
        paths = renderer.animate_growth(
            definition,
            output_dir=args.directory,
            iterations=args.iterations,
            width=args.width,
            height=args.height,
        )
        print(f"Generated {len(paths)} step files:")
        for path in paths:
            print(f"  {path}")
        return

    # Normal render
    output = args.output
    if args.backend == "ascii" and not output.endswith(".txt"):
        output = output.rsplit(".", 1)[0] + ".txt" if "." in output else output + ".txt"
    elif args.backend == "svg" and not output.endswith(".svg"):
        output += ".svg"
    elif args.backend == "png" and not output.endswith(".png"):
        output += ".png"

    try:
        result = renderer.render(
            definition,
            iterations=args.iterations,
            backend=args.backend,
            output=output,
            width=args.width,
            height=args.height,
            background=args.background,
            animate=args.animate,
        )
        print(f"Output written to: {result}")

        # Print brief stats
        engine = LSystemEngine(definition, seed=args.seed)
        lstring = engine.iterate(args.iterations)
        stats = LSystemEngine.analyze(lstring)
        print(f"Segments: {stats['draw_symbols']:,} | String length: {stats['length']:,}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()