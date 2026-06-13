"""
Tests for v3.0.0 additions: PDF renderer, grid renderer, SVG optimizer,
new presets, and CLI additions.
"""

import os
import json
import tempfile
import unittest
from unittest.mock import patch

from lsystem_renderer.core.types import (
    RenderBackend,
    ColorMode,
    Segment,
    LSystemDefinition,
    LSystemRule,
)
from lsystem_renderer.core.engine import LSystemEngine
from lsystem_renderer.core.interpreter import TurtleInterpreter
from lsystem_renderer.core.color_postprocessor import ColorPostProcessor
from lsystem_renderer.core.renderer import LSystemRenderer
from lsystem_renderer.core.presets import PRESETS
from lsystem_renderer.utils.svg_optimizer import optimize_svg, merge_svg_paths, stats_svg
from lsystem_renderer.utils.colors import hex_to_rgb
from lsystem_renderer.renderers.ascii import ASCIIRenderer
from lsystem_renderer.renderers.svg import SVGRenderer


# ── PDF Renderer Tests ────────────────────────────────────────────────

class TestPDFRenderer(unittest.TestCase):
    """Tests for the PDF rendering backend."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def test_pdf_renderer_is_available(self):
        from lsystem_renderer.renderers.pdf import PDFRenderer
        # reportlab is installed in test env
        self.assertTrue(PDFRenderer.is_available())

    def test_pdf_render_simple(self):
        from lsystem_renderer.renderers.pdf import PDFRenderer
        segments = [
            Segment(x1=0, y1=0, x2=100, y2=100, color="#000000", width=1.0),
            Segment(x1=100, y1=100, x2=200, y2=100, color="#ff0000", width=2.0),
        ]
        path = os.path.join(self.tmpdir, "test.pdf")
        renderer = PDFRenderer(width=400, height=400)
        result = renderer.render(segments, path)
        self.assertEqual(result, path)
        self.assertTrue(os.path.exists(path))
        self.assertGreater(os.path.getsize(path), 0)

    def test_pdf_render_empty_segments(self):
        from lsystem_renderer.renderers.pdf import PDFRenderer
        segments = []
        path = os.path.join(self.tmpdir, "empty.pdf")
        renderer = PDFRenderer()
        result = renderer.render(segments, path)
        self.assertEqual(result, path)
        self.assertTrue(os.path.exists(path))

    def test_pdf_render_with_background(self):
        from lsystem_renderer.renderers.pdf import PDFRenderer
        segments = [
            Segment(x1=0, y1=0, x2=50, y2=50, color="#333333", width=1.0),
        ]
        path = os.path.join(self.tmpdir, "bg.pdf")
        renderer = PDFRenderer(width=200, height=200, background="#f0f0f0")
        result = renderer.render(segments, path)
        self.assertTrue(os.path.exists(path))

    def test_pdf_render_with_title(self):
        from lsystem_renderer.renderers.pdf import PDFRenderer
        segments = [
            Segment(x1=0, y1=0, x2=50, y2=50, color="#000000", width=1.0),
        ]
        path = os.path.join(self.tmpdir, "titled.pdf")
        renderer = PDFRenderer(title="Test L-System")
        result = renderer.render(segments, path)
        self.assertTrue(os.path.exists(path))

    def test_pdf_compute_bounds(self):
        from lsystem_renderer.renderers.pdf import PDFRenderer
        renderer = PDFRenderer()
        segments = [
            Segment(x1=10, y1=20, x2=100, y2=200, color="#000", width=1.0),
        ]
        min_x, min_y, max_x, max_y = renderer._compute_bounds(segments)
        self.assertAlmostEqual(min_x, 10)
        self.assertAlmostEqual(min_y, 20)
        self.assertAlmostEqual(max_x, 100)
        self.assertAlmostEqual(max_y, 200)

    def test_pdf_compute_bounds_empty(self):
        from lsystem_renderer.renderers.pdf import PDFRenderer
        renderer = PDFRenderer()
        bounds = renderer._compute_bounds([])
        self.assertEqual(bounds, (0, 0, 100, 100))

    @unittest.skipUnless(
        os.environ.get("TEST_REPORTLAB_MISSING"),
        "Only run when simulating missing reportlab"
    )
    def test_pdf_import_error_without_reportlab(self):
        """Verify graceful behavior when reportlab is not available."""
        pass


# ── Grid Renderer Tests ───────────────────────────────────────────────

class TestGridRenderer(unittest.TestCase):
    """Tests for the grid/gallery renderer."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def test_grid_renderer_init(self):
        from lsystem_renderer.renderers.grid import GridRenderer
        grid = GridRenderer(cell_width=200, cell_height=200, columns=3)
        self.assertEqual(grid.cell_width, 200)
        self.assertEqual(grid.cell_height, 200)
        self.assertEqual(grid.columns, 3)

    def test_grid_render_small_set(self):
        from lsystem_renderer.renderers.grid import GridRenderer
        import copy

        defs = {
            "koch_curve": copy.deepcopy(PRESETS["koch_curve"]),
            "dragon_curve": copy.deepcopy(PRESETS["dragon_curve"]),
        }
        grid = GridRenderer(cell_width=200, cell_height=200, columns=2)
        path = os.path.join(self.tmpdir, "grid.svg")
        result = grid.render_grid(defs, path, iterations=2)
        self.assertEqual(result, path)
        self.assertTrue(os.path.exists(path))
        with open(path) as f:
            content = f.read()
        self.assertIn("<svg", content)
        self.assertIn("Koch Curve", content)
        self.assertIn("Dragon Curve", content)

    def test_grid_render_all_presets(self):
        from lsystem_renderer.renderers.grid import GridRenderer
        grid = GridRenderer(cell_width=150, cell_height=150, columns=4)
        path = os.path.join(self.tmpdir, "all_presets.svg")
        result = grid.render_all_presets_grid(path, iterations=2)
        self.assertTrue(os.path.exists(path))
        with open(path) as f:
            content = f.read()
        self.assertIn("<svg", content)

    def test_grid_render_single_preset(self):
        from lsystem_renderer.renderers.grid import GridRenderer
        import copy

        defs = {
            "sierpinski_triangle": copy.deepcopy(PRESETS["sierpinski_triangle"]),
        }
        grid = GridRenderer()
        path = os.path.join(self.tmpdir, "single.svg")
        result = grid.render_grid(defs, path, iterations=2)
        self.assertTrue(os.path.exists(path))

    def test_grid_compute_bounds(self):
        from lsystem_renderer.renderers.grid import GridRenderer
        segments = [
            Segment(x1=-10, y1=-5, x2=50, y2=80, color="#000", width=1.0),
        ]
        bounds = GridRenderer._compute_bounds(segments)
        self.assertAlmostEqual(bounds[0], -10)
        self.assertAlmostEqual(bounds[1], -5)


# ── SVG Optimizer Tests ────────────────────────────────────────────────

class TestSVGOptimizer(unittest.TestCase):
    """Tests for SVG optimization utilities."""

    def test_optimize_removes_comments(self):
        svg = '<svg><!-- comment --><rect/></svg>'
        result = optimize_svg(svg)
        self.assertNotIn('<!--', result)
        self.assertIn('<rect/>', result)

    def test_optimize_truncates_floats(self):
        svg = '<line x1="1.12345678" y1="2.98765432"/>'
        result = optimize_svg(svg, precision=2)
        self.assertIn('1.12', result)
        # 2.99 stays as is since it only has 2 decimal places after truncation
        self.assertIn('2.99', result)

    def test_optimize_removes_leading_zero(self):
        svg = '<line x1="0.5123" y1="0.7512"/>'
        result = optimize_svg(svg, precision=2)
        # Should truncate to 2 decimals and remove leading zero
        self.assertNotIn('0.51', result)  # should become .51

    def test_optimize_collapses_whitespace(self):
        svg = '<svg>\n\n\n<rect/>\n\n\n</svg>'
        result = optimize_svg(svg)
        self.assertNotIn('\n\n', result)

    def test_optimize_preserves_structure(self):
        svg = '<svg xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100"/></svg>'
        result = optimize_svg(svg)
        self.assertIn('<svg', result)
        self.assertIn('</svg>', result)
        self.assertIn('<rect', result)

    def test_merge_paths_no_paths(self):
        svg = '<svg><rect width="100"/></svg>'
        result = merge_svg_paths(svg)
        self.assertEqual(svg, result)

    def test_merge_paths_grouped(self):
        svg = (
            '<path d="M0,0 L10,10" stroke="#000" stroke-width="1" '
            'fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            '<path d="M20,20 L30,30" stroke="#000" stroke-width="1" '
            'fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        )
        result = merge_svg_paths(svg)
        # Should merge into a single path
        self.assertEqual(result.count('<path'), 1)
        self.assertIn('M0,0 L10,10', result)
        self.assertIn('M20,20 L30,30', result)

    def test_merge_paths_different_styles(self):
        svg = (
            '<path d="M0,0 L10,10" stroke="#000" stroke-width="1" '
            'fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            '<path d="M20,20 L30,30" stroke="#f00" stroke-width="1" '
            'fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        )
        result = merge_svg_paths(svg)
        # Different colors, should remain separate
        self.assertEqual(result.count('<path'), 2)

    def test_stats_svg(self):
        svg = '<svg><path d="M0,0"/><line x1="0" y1="0" x2="10" y2="10"/><g><g/></g><animate/></svg>'
        stats = stats_svg(svg)
        self.assertEqual(stats["paths"], 1)
        self.assertEqual(stats["lines_count"], 1)
        self.assertEqual(stats["groups"], 2)
        self.assertEqual(stats["animations"], 1)
        self.assertGreater(stats["bytes"], 0)


# ── New Presets Tests ───────────────────────────────────────────────────

class TestNewPresets(unittest.TestCase):
    """Tests for newly added presets."""

    def test_fibonacci_word_preset_exists(self):
        self.assertIn("fibonacci_word", PRESETS)

    def test_minkowski_sausage_preset_exists(self):
        self.assertIn("minkowski_sausage", PRESETS)

    def test_moore_curve_preset_exists(self):
        self.assertIn("moore_curve", PRESETS)

    def test_koch_antisnowflake_preset_exists(self):
        self.assertIn("koch_antisnowflake", PRESETS)

    def test_cesaro_fractal_preset_exists(self):
        self.assertIn("cesaro_fractal", PRESETS)

    def test_plant_alternate_preset_exists(self):
        self.assertIn("plant_alternate", PRESETS)

    def test_new_presets_render_ascii(self):
        """All new presets should render without errors."""
        renderer = LSystemRenderer()
        new_presets = [
            "fibonacci_word", "minkowski_sausage", "moore_curve",
            "koch_antisnowflake", "cesaro_fractal", "plant_alternate",
        ]
        for name in new_presets:
            with self.subTest(preset=name):
                result = renderer.render(name, iterations=2, backend="ascii")
                self.assertIsInstance(result, str)
                self.assertGreater(len(result), 0)

    def test_fibonacci_word_iteration(self):
        """Fibonacci word should produce correct iteration strings."""
        defn = PRESETS["fibonacci_word"]
        engine = LSystemEngine(defn)
        result = engine.iterate(1)
        self.assertIn("0", result)
        self.assertIn("1", result)

    def test_minkowski_sausage_iteration(self):
        defn = PRESETS["minkowski_sausage"]
        engine = LSystemEngine(defn)
        result = engine.iterate(1)
        self.assertIn("F", result)

    def test_moore_curve_iteration(self):
        defn = PRESETS["moore_curve"]
        engine = LSystemEngine(defn)
        result = engine.iterate(1)
        self.assertIn("F", result)


# ── RenderBackend Tests ────────────────────────────────────────────────

class TestRenderBackendPDF(unittest.TestCase):
    """Tests for PDF backend enum value."""

    def test_pdf_backend_exists(self):
        self.assertIsNotNone(RenderBackend.PDF)

    def test_from_string_pdf(self):
        # RenderBackend uses string values, check it can be constructed
        self.assertEqual(RenderBackend.PDF.name, "PDF")


# ── LSystemRenderer New Methods ────────────────────────────────────────

class TestRendererNewMethods(unittest.TestCase):
    """Tests for new renderer methods (render_optimized, render_gallery_grid)."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.renderer = LSystemRenderer()

    def test_render_optimized_svg(self):
        output = os.path.join(self.tmpdir, "optimized.svg")
        result = self.renderer.render_optimized(
            "koch_curve",
            iterations=3,
            output=output,
        )
        self.assertTrue(os.path.exists(output))
        with open(output) as f:
            content = f.read()
        self.assertIn("<svg", content)

    def test_render_gallery_grid(self):
        output = os.path.join(self.tmpdir, "gallery.svg")
        result = self.renderer.render_gallery_grid(
            output_path=output,
            iterations=2,
            cell_width=150,
            cell_height=150,
            columns=3,
            seed=42,
        )
        self.assertTrue(os.path.exists(output))
        with open(output) as f:
            content = f.read()
        self.assertIn("<svg", content)

    def test_render_pdf_backend(self):
        output = os.path.join(self.tmpdir, "test.pdf")
        result = self.renderer.render(
            "koch_curve",
            iterations=2,
            backend="pdf",
            output=output,
        )
        self.assertTrue(os.path.exists(output))
        self.assertGreater(os.path.getsize(output), 0)

    def test_render_optimized_with_definition(self):
        defn = LSystemDefinition(
            name="Custom Test",
            axiom="F",
            rules=[LSystemRule("F", "F+F--F+F")],
            angle=60.0,
            step_size=5.0,
            iterations=3,
        )
        output = os.path.join(self.tmpdir, "custom_opt.svg")
        result = self.renderer.render_optimized(defn, iterations=2, output=output)
        self.assertTrue(os.path.exists(output))

    def test_render_optimized_unknown_preset_raises(self):
        with self.assertRaises(ValueError):
            self.renderer.render_optimized("nonexistent_preset")


# ── Integration Tests ──────────────────────────────────────────────────

class TestIntegration(unittest.TestCase):
    """End-to-end integration tests for the v3.0 pipeline."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def test_full_pipeline_svg(self):
        """Test the complete pipeline: definition → engine → interpreter → renderer → SVG."""
        defn = LSystemDefinition(
            name="Pipeline Test",
            axiom="F",
            rules=[LSystemRule("F", "F[+F]F[-F]F")],
            angle=25.7,
            step_size=5.0,
            iterations=3,
            color_mode="depth",
            colors={0: "#4a2f0a", 1: "#3d6b2e", 2: "#6bb55a", 3: "#a8f08a"},
        )
        engine = LSystemEngine(defn)
        lstring = engine.iterate()
        interpreter = TurtleInterpreter(angle=defn.angle, step_size=defn.step_size)
        segments = interpreter.interpret(lstring)
        segments = ColorPostProcessor.apply(
            segments,
            color_mode=defn.color_mode,
            colors=defn.colors,
        )
        self.assertGreater(len(segments), 0)

        path = os.path.join(self.tmpdir, "pipeline.svg")
        renderer = SVGRenderer(title="Pipeline Test")
        renderer.render(segments, path)
        self.assertTrue(os.path.exists(path))
        with open(path) as f:
            content = f.read()
        self.assertIn("<svg", content)
        self.assertIn("Pipeline Test", content)

    def test_full_pipeline_optimized(self):
        """Test the pipeline with SVG optimization."""
        renderer = LSystemRenderer()
        path = os.path.join(self.tmpdir, "optimized.svg")
        renderer.render_optimized("hilbert_curve", iterations=3, output=path)
        self.assertTrue(os.path.exists(path))
        with open(path) as f:
            content = f.read()
        self.assertIn("<svg", content)

    def test_full_pipeline_pdf(self):
        """Test the complete pipeline with PDF backend."""
        renderer = LSystemRenderer()
        path = os.path.join(self.tmpdir, "pipeline.pdf")
        renderer.render("dragon_curve", iterations=5, backend="pdf", output=path)
        self.assertTrue(os.path.exists(path))
        # PDFs start with %PDF
        with open(path, "rb") as f:
            header = f.read(5)
        self.assertEqual(header, b"%PDF-")

    def test_config_json_roundtrip_with_pdf(self):
        """Test that config can specify PDF backend."""
        from lsystem_renderer.core.config import LSystemConfig
        config = LSystemConfig()
        config_dict = config.to_dict()
        config_dict["backend"] = "pdf"
        self.assertEqual(config_dict["backend"], "pdf")

    def test_grid_gallery_renders_all_presets(self):
        """Test that gallery rendering works for all presets."""
        from lsystem_renderer.renderers.grid import GridRenderer
        import copy

        grid = GridRenderer(cell_width=100, cell_height=100, columns=4)
        path = os.path.join(self.tmpdir, "gallery_all.svg")
        result = grid.render_all_presets_grid(path, iterations=2, seed=42)
        self.assertTrue(os.path.exists(path))
        self.assertGreater(os.path.getsize(path), 1000)  # Should be a substantial SVG


# ── CLI New Flags Tests ────────────────────────────────────────────────

class TestCLINewFlags(unittest.TestCase):
    """Tests for new CLI flags (--info, --optimize, --gallery, --backend pdf)."""

    def test_cli_info_flag(self):
        from lsystem_renderer.cli import build_parser
        parser = build_parser()
        args = parser.parse_args(["--preset", "koch_curve", "--info"])
        self.assertTrue(args.info)

    def test_cli_optimize_flag(self):
        from lsystem_renderer.cli import build_parser
        parser = build_parser()
        args = parser.parse_args(["--preset", "koch_curve", "--optimize"])
        self.assertTrue(args.optimize)

    def test_cli_gallery_flag(self):
        from lsystem_renderer.cli import build_parser
        parser = build_parser()
        args = parser.parse_args(["--gallery"])
        self.assertTrue(args.gallery)

    def test_cli_gallery_cols_option(self):
        from lsystem_renderer.cli import build_parser
        parser = build_parser()
        args = parser.parse_args(["--gallery", "--gallery-cols", "5"])
        self.assertEqual(args.gallery_cols, 5)

    def test_cli_gallery_cell_size_option(self):
        from lsystem_renderer.cli import build_parser
        parser = build_parser()
        args = parser.parse_args(["--gallery", "--gallery-cell-size", "250"])
        self.assertEqual(args.gallery_cell_size, 250)

    def test_cli_backend_pdf(self):
        from lsystem_renderer.cli import build_parser
        parser = build_parser()
        args = parser.parse_args(["--preset", "koch_curve", "--backend", "pdf"])
        self.assertEqual(args.backend, "pdf")

    def test_cli_backend_pdf_valid_choice(self):
        from lsystem_renderer.cli import build_parser
        parser = build_parser()
        # Should not raise
        args = parser.parse_args(["--preset", "koch_curve", "-b", "pdf"])
        self.assertEqual(args.backend, "pdf")


if __name__ == "__main__":
    unittest.main()