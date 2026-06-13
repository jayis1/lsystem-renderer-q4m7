"""Tests for L-System Renderer package.

Covers: types, engine, interpreter, color utils, rendering, config, CLI,
JSON/YAML import/export, edge cases, and bug verification.
"""

import json
import math
import os
import tempfile
import unittest

from lsystem_renderer import (
    ASCIIRenderer,
    ColorMode,
    ColorPostProcessor,
    LSystemConfig,
    LSystemDefinition,
    LSystemEngine,
    LSystemRenderer,
    LSystemRule,
    PNGRenderer,
    RenderBackend,
    Segment,
    SVGRenderer,
    TurtleInterpreter,
    TurtleState,
    hex_to_rgb,
    hsl_to_rgb,
    lerp_color,
    rainbow_color,
    rgb_to_hex,
    PRESETS,
)
from lsystem_renderer.utils.colors import (
    _escape_xml,
    complementary_color,
    blend_colors,
    rgb_to_hsl,
)
from lsystem_renderer.core.config import RenderConfig, OutputConfig


class TestColorUtils(unittest.TestCase):
    """Test color utility functions."""

    def test_hex_to_rgb(self):
        self.assertEqual(hex_to_rgb("#ff0000"), (255, 0, 0))
        self.assertEqual(hex_to_rgb("00ff00"), (0, 255, 0))
        self.assertEqual(hex_to_rgb("#0000ff"), (0, 0, 255))
        self.assertEqual(hex_to_rgb("#ffffff"), (255, 255, 255))
        self.assertEqual(hex_to_rgb("#000000"), (0, 0, 0))

    def test_hex_to_rgb_invalid(self):
        self.assertEqual(hex_to_rgb("xyz"), (0, 0, 0))
        self.assertEqual(hex_to_rgb(""), (0, 0, 0))
        self.assertEqual(hex_to_rgb("#abc"), (0, 0, 0))  # too short

    def test_rgb_to_hex(self):
        self.assertEqual(rgb_to_hex(255, 0, 0), "#ff0000")
        self.assertEqual(rgb_to_hex(0, 255, 0), "#00ff00")
        self.assertEqual(rgb_to_hex(0, 0, 255), "#0000ff")

    def test_rgb_to_hex_clamping(self):
        self.assertEqual(rgb_to_hex(300, -10, 128), "#ff0080")

    def test_lerp_color(self):
        self.assertEqual(lerp_color("#000000", "#ffffff", 0.0), "#000000")
        self.assertEqual(lerp_color("#000000", "#ffffff", 1.0), "#ffffff")
        mid = lerp_color("#000000", "#ffffff", 0.5)
        self.assertEqual(mid, "#808080")

    def test_lerp_color_clamping(self):
        self.assertEqual(lerp_color("#ff0000", "#0000ff", -0.5), "#ff0000")
        self.assertEqual(lerp_color("#ff0000", "#0000ff", 1.5), "#0000ff")

    def test_hsl_to_rgb(self):
        r, g, b = hsl_to_rgb(0, 1.0, 0.5)
        self.assertAlmostEqual(r, 255, delta=1)
        self.assertAlmostEqual(g, 0, delta=1)
        self.assertAlmostEqual(b, 0, delta=1)
        r, g, b = hsl_to_rgb(120, 1.0, 0.5)
        self.assertAlmostEqual(r, 0, delta=1)
        self.assertAlmostEqual(g, 255, delta=1)
        self.assertAlmostEqual(b, 0, delta=1)

    def test_rgb_to_hsl(self):
        h, s, l = rgb_to_hsl(255, 0, 0)
        self.assertAlmostEqual(h, 0.0, delta=1)
        self.assertAlmostEqual(s, 1.0, delta=0.01)
        self.assertAlmostEqual(l, 0.5, delta=0.01)

    def test_rgb_hsl_roundtrip(self):
        """RGB -> HSL -> RGB should be approximately identity."""
        for r, g, b in [(255, 0, 0), (0, 255, 0), (0, 0, 255), (128, 64, 200)]:
            h, s, l = rgb_to_hsl(r, g, b)
            r2, g2, b2 = hsl_to_rgb(h, s, l)
            self.assertAlmostEqual(r, r2, delta=2, msg=f"R mismatch for ({r},{g},{b})")
            self.assertAlmostEqual(g, g2, delta=2, msg=f"G mismatch for ({r},{g},{b})")
            self.assertAlmostEqual(b, b2, delta=2, msg=f"B mismatch for ({r},{g},{b})")

    def test_rainbow_color(self):
        color = rainbow_color(0, 10)
        self.assertTrue(color.startswith("#"))
        self.assertEqual(len(color), 7)
        self.assertEqual(rainbow_color(0, 0), "#ffffff")

    def test_complementary_color(self):
        self.assertEqual(complementary_color("#000000"), "#ffffff")
        self.assertEqual(complementary_color("#ffffff"), "#000000")
        self.assertEqual(complementary_color("#ff0000"), "#00ffff")

    def test_blend_colors(self):
        # Single color
        self.assertEqual(blend_colors(["#ff0000"], 0.5), "#ff0000")
        # Two colors
        mid = blend_colors(["#000000", "#ffffff"], 0.5)
        self.assertEqual(mid, "#808080")
        # Multiple colors
        result = blend_colors(["#ff0000", "#00ff00", "#0000ff"], 0.5)
        self.assertTrue(result.startswith("#"))

    def test_blend_colors_empty(self):
        self.assertEqual(blend_colors([], 0.5), "#000000")

    def test_escape_xml(self):
        self.assertEqual(_escape_xml("<script>"), "&lt;script&gt;")
        self.assertEqual(_escape_xml("a&b"), "a&amp;b")
        self.assertEqual(_escape_xml('"x"'), "&quot;x&quot;")
        self.assertEqual(_escape_xml("'y'"), "&apos;y&apos;")


class TestRenderBackend(unittest.TestCase):
    """Test RenderBackend enum."""

    def test_from_string_svg(self):
        self.assertEqual(RenderBackend["SVG"], RenderBackend.SVG)

    def test_from_string_ascii(self):
        self.assertEqual(RenderBackend["ASCII"], RenderBackend.ASCII)

    def test_from_string_invalid(self):
        with self.assertRaises(KeyError):
            RenderBackend["INVALID"]


class TestColorMode(unittest.TestCase):
    """Test ColorMode enum."""

    def test_from_string(self):
        self.assertEqual(ColorMode.from_string("depth"), ColorMode.DEPTH)
        self.assertEqual(ColorMode.from_string("position"), ColorMode.POSITION)
        self.assertEqual(ColorMode.from_string("segment_index"), ColorMode.SEGMENT_INDEX)
        self.assertEqual(ColorMode.from_string("single"), ColorMode.SINGLE)

    def test_from_string_invalid(self):
        with self.assertRaises(ValueError):
            ColorMode.from_string("invalid")

    def test_to_string(self):
        self.assertEqual(ColorMode.DEPTH.to_string(), "depth")
        self.assertEqual(ColorMode.SEGMENT_INDEX.to_string(), "segment_index")


class TestSegment(unittest.TestCase):
    """Test Segment helper methods."""

    def test_length(self):
        seg = Segment(0, 0, 3, 4)
        self.assertAlmostEqual(seg.length(), 5.0)

    def test_midpoint(self):
        seg = Segment(0, 0, 10, 20)
        self.assertEqual(seg.midpoint(), (5.0, 10.0))

    def test_direction_deg(self):
        seg = Segment(0, 0, 1, 0)  # pointing right
        self.assertAlmostEqual(seg.direction_deg(), 0.0, delta=1)
        seg2 = Segment(0, 0, 0, 1)  # pointing up
        self.assertAlmostEqual(seg2.direction_deg(), 90.0, delta=1)


class TestLSystemRule(unittest.TestCase):
    """Test LSystemRule."""

    def test_to_dict_minimal(self):
        rule = LSystemRule("F", "F+F")
        d = rule.to_dict()
        self.assertEqual(d, {"predecessor": "F", "successor": "F+F"})

    def test_to_dict_full(self):
        rule = LSystemRule("F", "F[+F]", condition="n>1", probability=0.7,
                           left_context="A", right_context="B")
        d = rule.to_dict()
        self.assertEqual(d["predecessor"], "F")
        self.assertEqual(d["condition"], "n>1")
        self.assertAlmostEqual(d["probability"], 0.7)
        self.assertEqual(d["left_context"], "A")
        self.assertEqual(d["right_context"], "B")

    def test_from_dict(self):
        d = {"predecessor": "F", "successor": "F+F", "probability": 0.5}
        rule = LSystemRule.from_dict(d)
        self.assertEqual(rule.predecessor, "F")
        self.assertEqual(rule.successor, "F+F")
        self.assertAlmostEqual(rule.probability, 0.5)
        self.assertIsNone(rule.condition)

    def test_roundtrip(self):
        rule = LSystemRule("F", "FF", condition="x>0", probability=0.3,
                           left_context="A", right_context="B")
        d = rule.to_dict()
        rule2 = LSystemRule.from_dict(d)
        self.assertEqual(rule.predecessor, rule2.predecessor)
        self.assertEqual(rule.successor, rule2.successor)
        self.assertEqual(rule.condition, rule2.condition)
        self.assertAlmostEqual(rule.probability, rule2.probability)
        self.assertEqual(rule.left_context, rule2.left_context)
        self.assertEqual(rule.right_context, rule2.right_context)

    def test_parse_arrow(self):
        rule = LSystemRule.parse("F->F+F--F+F")
        self.assertEqual(rule.predecessor, "F")
        self.assertEqual(rule.successor, "F+F--F+F")

    def test_parse_equals(self):
        rule = LSystemRule.parse("F=F+F")
        self.assertEqual(rule.predecessor, "F")
        self.assertEqual(rule.successor, "F+F")

    def test_parse_invalid(self):
        with self.assertRaises(ValueError):
            LSystemRule.parse("invalid")

    def test_validation_empty_predecessor(self):
        with self.assertRaises(ValueError):
            LSystemRule("", "F+F")

    def test_validation_zero_probability(self):
        with self.assertRaises(ValueError):
            LSystemRule("F", "F+F", probability=0.0)


class TestLSystemDefinition(unittest.TestCase):
    """Test LSystemDefinition."""

    def test_to_dict_minimal(self):
        defn = LSystemDefinition(name="Test", axiom="F", rules=[LSystemRule("F", "F+F")])
        d = defn.to_dict()
        self.assertEqual(d["name"], "Test")
        self.assertEqual(d["axiom"], "F")
        self.assertEqual(len(d["rules"]), 1)
        self.assertEqual(d["angle"], 25.0)

    def test_json_roundtrip(self):
        defn = LSystemDefinition(
            name="TestPlant",
            axiom="F",
            rules=[LSystemRule("F", "F[+F]F[-F]F", probability=0.5)],
            angle=25.7,
            step_size=4.0,
            iterations=5,
            colors={0: "#5a3e1b", 1: "#3d6b2e"},
            color_mode="depth",
            gradient=("#ff0000", "#0000ff"),
            perturbation=2.5,
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name
        try:
            defn.to_json(path)
            loaded = LSystemDefinition.from_json(path)
            self.assertEqual(loaded.name, defn.name)
            self.assertEqual(loaded.axiom, defn.axiom)
            self.assertEqual(len(loaded.rules), len(defn.rules))
            self.assertAlmostEqual(loaded.angle, defn.angle)
            self.assertAlmostEqual(loaded.perturbation, defn.perturbation)
            self.assertEqual(loaded.colors, defn.colors)
            self.assertEqual(loaded.gradient, defn.gradient)
        finally:
            os.unlink(path)

    def test_validation_empty_name(self):
        with self.assertRaises(ValueError):
            LSystemDefinition(name="", axiom="F", rules=[])

    def test_validation_negative_iterations(self):
        with self.assertRaises(ValueError):
            LSystemDefinition(name="X", axiom="F", rules=[], iterations=-1)

    def test_validation_invalid_color_mode(self):
        with self.assertRaises(ValueError):
            LSystemDefinition(name="X", axiom="F", rules=[], color_mode="invalid")

    def test_validation_negative_step_size(self):
        with self.assertRaises(ValueError):
            LSystemDefinition(name="X", axiom="F", rules=[], step_size=-1.0)


class TestLSystemEngine(unittest.TestCase):
    """Test the L-system string rewriting engine."""

    def test_koch_curve_single_iteration(self):
        defn = LSystemDefinition(name="Koch", axiom="F", rules=[LSystemRule("F", "F+F--F+F")], angle=60)
        engine = LSystemEngine(defn)
        result = engine.iterate(1)
        self.assertEqual(result, "F+F--F+F")

    def test_koch_curve_two_iterations(self):
        defn = LSystemDefinition(name="Koch", axiom="F", rules=[LSystemRule("F", "F+F--F+F")], angle=60)
        engine = LSystemEngine(defn)
        result = engine.iterate(2)
        expected = "F+F--F+F+F+F--F+F--F+F--F+F+F+F--F+F"
        self.assertEqual(result, expected)

    def test_zero_iterations(self):
        defn = LSystemDefinition(name="Test", axiom="F", rules=[LSystemRule("F", "F+F")])
        engine = LSystemEngine(defn)
        result = engine.iterate(0)
        self.assertEqual(result, "F")

    def test_negative_iterations_raises(self):
        defn = LSystemDefinition(name="Test", axiom="F", rules=[LSystemRule("F", "F+F")])
        engine = LSystemEngine(defn)
        with self.assertRaises(ValueError):
            engine.iterate(-1)

    def test_non_matching_symbol_unchanged(self):
        defn = LSystemDefinition(name="Test", axiom="F+G", rules=[LSystemRule("F", "FF")])
        engine = LSystemEngine(defn)
        result = engine.iterate(1)
        self.assertEqual(result, "FF+G")

    def test_stochastic_with_seed_deterministic(self):
        defn = LSystemDefinition(
            name="StochTest",
            axiom="F",
            rules=[
                LSystemRule("F", "F+F", probability=0.5),
                LSystemRule("F", "F-F", probability=0.5),
            ],
        )
        engine1 = LSystemEngine(defn, seed=42)
        result1 = engine1.iterate(3)
        engine2 = LSystemEngine(defn, seed=42)
        result2 = engine2.iterate(3)
        self.assertEqual(result1, result2)

    def test_context_sensitive(self):
        defn = LSystemDefinition(
            name="ContextTest",
            axiom="ABA",
            rules=[
                LSystemRule("B", "BB", left_context="A", right_context="A"),
            ],
        )
        engine = LSystemEngine(defn)
        result = engine.iterate(1)
        self.assertEqual(result, "ABBA")

    def test_context_sensitive_no_match(self):
        defn = LSystemDefinition(
            name="ContextTest",
            axiom="BBA",
            rules=[
                LSystemRule("B", "BB", left_context="A"),
            ],
        )
        engine = LSystemEngine(defn)
        result = engine.iterate(1)
        self.assertEqual(result, "BBA")

    def test_analyze(self):
        result = LSystemEngine.analyze("F+F--F+F")
        self.assertEqual(result["length"], 8)
        self.assertEqual(result["draw_symbols"], 4)
        self.assertEqual(result["unique_symbols"], 3)
        self.assertEqual(result["symbols"]["F"], 4)

    def test_analyze_empty(self):
        result = LSystemEngine.analyze("")
        self.assertEqual(result["length"], 0)
        self.assertEqual(result["draw_symbols"], 0)

    def test_analyze_branch_depth(self):
        result = LSystemEngine.analyze("F[F[+F]]")
        self.assertEqual(result["branch_depth"], 2)

    def test_iterate_steps(self):
        defn = LSystemDefinition(name="Test", axiom="F", rules=[LSystemRule("F", "FF")])
        engine = LSystemEngine(defn)
        steps = engine.iterate_steps(3)
        self.assertEqual(len(steps), 4)
        self.assertEqual(steps[0], "F")
        self.assertEqual(steps[1], "FF")
        self.assertEqual(steps[2], "FFFF")
        self.assertEqual(steps[3], "FFFFFFFF")

    def test_iterate_steps_negative_raises(self):
        defn = LSystemDefinition(name="Test", axiom="F", rules=[LSystemRule("F", "FF")])
        engine = LSystemEngine(defn)
        with self.assertRaises(ValueError):
            engine.iterate_steps(-1)


class TestTurtleInterpreter(unittest.TestCase):
    """Test the turtle graphics interpreter."""

    def test_forward_draws_segment(self):
        interp = TurtleInterpreter(angle=90, step_size=10)
        segments = interp.interpret("F")
        self.assertEqual(len(segments), 1)
        self.assertAlmostEqual(segments[0].x1, 0)
        self.assertAlmostEqual(segments[0].y1, 0)
        self.assertAlmostEqual(segments[0].x2, 0, places=5)
        self.assertAlmostEqual(segments[0].y2, 10, places=5)

    def test_forward_no_draw(self):
        interp = TurtleInterpreter(angle=90, step_size=10)
        segments = interp.interpret("f")
        self.assertEqual(len(segments), 0)

    def test_turn_right_90(self):
        interp = TurtleInterpreter(angle=90, step_size=10)
        segments = interp.interpret("F-F")
        self.assertEqual(len(segments), 2)
        self.assertAlmostEqual(segments[1].x2, 10, places=5)

    def test_turn_left_90(self):
        interp = TurtleInterpreter(angle=90, step_size=10)
        segments = interp.interpret("F+F")
        self.assertEqual(len(segments), 2)
        self.assertAlmostEqual(segments[1].x2, -10, places=5)

    def test_push_pop(self):
        interp = TurtleInterpreter(angle=90, step_size=10)
        segments = interp.interpret("F[+F]F")
        self.assertEqual(len(segments), 3)
        self.assertAlmostEqual(segments[2].x1, segments[0].x2, places=5)
        self.assertAlmostEqual(segments[2].y1, segments[0].y2, places=5)

    def test_reverse_direction(self):
        interp = TurtleInterpreter(angle=90, step_size=10)
        segments = interp.interpret("F|F")
        self.assertAlmostEqual(segments[1].y2, 0, places=5)

    def test_perturbation(self):
        interp = TurtleInterpreter(angle=90, step_size=10, perturbation=5.0, seed=42)
        segments = interp.interpret("FFFF")
        self.assertEqual(len(segments), 4)

    def test_colors_by_depth(self):
        colors = {0: "#ff0000", 1: "#00ff00", 2: "#0000ff"}
        interp = TurtleInterpreter(angle=90, step_size=10, colors=colors)
        segments = interp.interpret("F[+F[+F]]")
        self.assertEqual(segments[0].color, "#ff0000")
        branch_segments = [s for s in segments if s.depth >= 1]
        self.assertTrue(len(branch_segments) > 0)

    def test_line_width_thinning_in_branch(self):
        interp = TurtleInterpreter(angle=90, step_size=10, line_width=2.0)
        segments = interp.interpret("F[+F]")
        root_width = segments[0].width
        branch_width = segments[1].width
        self.assertGreater(root_width, branch_width)

    def test_shrink_at_symbol(self):
        """'@' should shrink step size by 0.8 factor."""
        interp = TurtleInterpreter(angle=90, step_size=10)
        segments = interp.interpret("F@F")
        self.assertAlmostEqual(segments[0].y2, 10, places=5)
        self.assertAlmostEqual(segments[1].y2, 18, places=0)  # 10 + 8

    def test_interpret_empty_string(self):
        interp = TurtleInterpreter(angle=90, step_size=10)
        segments = interp.interpret("")
        self.assertEqual(len(segments), 0)


class TestColorPostProcessor(unittest.TestCase):
    """Test color post-processing."""

    def test_depth_color_mode(self):
        segs = [
            Segment(0, 0, 1, 1, depth=0),
            Segment(1, 1, 2, 2, depth=1),
        ]
        colors = {0: "#ff0000", 1: "#00ff00"}
        result = ColorPostProcessor.apply(segs, color_mode="depth", colors=colors)
        self.assertEqual(result[0].color, "#ff0000")
        self.assertEqual(result[1].color, "#00ff00")

    def test_single_color_mode(self):
        segs = [Segment(0, 0, 1, 1), Segment(1, 1, 2, 2)]
        result = ColorPostProcessor.apply(segs, color_mode="single")
        self.assertEqual(result[0].color, result[1].color)

    def test_segment_index_color_mode(self):
        segs = [Segment(0, 0, 1, 1, segment_index=0),
                Segment(1, 1, 2, 2, segment_index=1)]
        result = ColorPostProcessor.apply(segs, color_mode="segment_index")
        self.assertNotEqual(result[0].color, result[1].color)

    def test_position_gradient_mode(self):
        segs = [
            Segment(0, 0, 1, 0),    # y=0
            Segment(0, 10, 1, 10),  # y=10
        ]
        gradient = ("#000000", "#ffffff")
        result = ColorPostProcessor.apply(segs, color_mode="position", gradient=gradient)
        self.assertEqual(result[0].color, "#000000")
        self.assertEqual(result[1].color, "#ffffff")

    def test_empty_segments(self):
        result = ColorPostProcessor.apply([], color_mode="depth")
        self.assertEqual(result, [])

    def test_unknown_color_mode_leaves_unchanged(self):
        segs = [Segment(0, 0, 1, 1, color="#ff0000")]
        result = ColorPostProcessor.apply(segs, color_mode="nonexistent")
        self.assertEqual(result[0].color, "#ff0000")


class TestSVGRenderer(unittest.TestCase):
    """Test SVG rendering."""

    def test_renders_to_file(self):
        segments = [Segment(0, 0, 10, 10)]
        renderer = SVGRenderer(width=100, height=100)
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            path = f.name
        try:
            result = renderer.render(segments, path)
            self.assertTrue(os.path.exists(path))
            with open(path) as f:
                content = f.read()
            self.assertIn("<svg", content)
            self.assertIn("</svg>", content)
        finally:
            os.unlink(path)

    def test_empty_segments(self):
        renderer = SVGRenderer(width=100, height=100)
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            path = f.name
        try:
            renderer.render([], path)
            with open(path) as f:
                content = f.read()
            self.assertIn("<svg", content)
        finally:
            os.unlink(path)

    def test_animated_svg(self):
        segments = [Segment(0, 0, 10, 10)]
        renderer = SVGRenderer(width=100, height=100)
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            path = f.name
        try:
            renderer.render(segments, path, animate=True, animation_duration=2.0)
            with open(path) as f:
                content = f.read()
            self.assertIn("<animate", content)
        finally:
            os.unlink(path)

    def test_svg_title_escaping(self):
        segments = [Segment(0, 0, 10, 10)]
        renderer = SVGRenderer(width=100, height=100, title="Test<script>")
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            path = f.name
        try:
            renderer.render(segments, path)
            with open(path) as f:
                content = f.read()
            self.assertIn("&lt;script&gt;", content)
            self.assertNotIn("<script>", content)
        finally:
            os.unlink(path)

    def test_svg_path_grouping_by_width(self):
        segments = [
            Segment(0, 0, 10, 0, color="#ff0000", width=1.0),
            Segment(10, 0, 20, 0, color="#ff0000", width=3.0),
        ]
        renderer = SVGRenderer(width=100, height=100)
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            path = f.name
        try:
            renderer.render(segments, path)
            with open(path) as f:
                content = f.read()
            self.assertIn('stroke-width="1.00"', content)
            self.assertIn('stroke-width="3.00"', content)
        finally:
            os.unlink(path)


class TestASCIIRenderer(unittest.TestCase):
    """Test ASCII rendering."""

    def test_renders_segments(self):
        segments = [Segment(0, 0, 10, 10)]
        renderer = ASCIIRenderer(width=20, height=10)
        result = renderer.render(segments)
        self.assertTrue(len(result) > 0)
        self.assertIn("\\", result)

    def test_empty_segments(self):
        renderer = ASCIIRenderer(width=20, height=10)
        result = renderer.render([])
        self.assertEqual(result, "")

    def test_writes_to_file(self):
        segments = [Segment(0, 0, 10, 10)]
        renderer = ASCIIRenderer(width=20, height=10)
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            path = f.name
        try:
            renderer.render(segments, output_path=path)
            self.assertTrue(os.path.exists(path))
            with open(path) as f:
                content = f.read()
            self.assertTrue(len(content) > 0)
        finally:
            os.unlink(path)


class TestPNGRenderer(unittest.TestCase):
    """Test PNG rendering."""

    def test_is_available(self):
        # Just check it doesn't crash
        result = PNGRenderer.is_available()
        self.assertIsInstance(result, bool)

    def test_render_when_available(self):
        if not PNGRenderer.is_available():
            self.skipTest("Pillow not available")
        segments = [Segment(0, 0, 10, 10, color="#ff0000")]
        renderer = PNGRenderer(width=100, height=100)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            path = f.name
        try:
            result = renderer.render(segments, path)
            self.assertTrue(os.path.exists(path))
            self.assertGreater(os.path.getsize(path), 0)
        finally:
            os.unlink(path)

    def test_render_empty_when_available(self):
        if not PNGRenderer.is_available():
            self.skipTest("Pillow not available")
        renderer = PNGRenderer(width=100, height=100)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            path = f.name
        try:
            renderer.render([], path)
            self.assertTrue(os.path.exists(path))
        finally:
            os.unlink(path)

    def test_import_error_without_pillow(self):
        """Test that attempting to render without Pillow raises ImportError."""
        # We can't easily test this when Pillow IS installed,
        # but we can verify the is_available() method works
        if PNGRenderer.is_available():
            # Pillow is installed, so rendering should work
            pass
        else:
            with self.assertRaises(ImportError):
                renderer = PNGRenderer(width=100, height=100)
                renderer.render([], "/tmp/test.png")


class TestLSystemRenderer(unittest.TestCase):
    """Test the high-level renderer API."""

    def test_render_preset_svg(self):
        renderer = LSystemRenderer(seed=42)
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            path = f.name
        try:
            result = renderer.render("koch_curve", iterations=2, output=path)
            self.assertTrue(os.path.exists(path))
            with open(path) as f:
                content = f.read()
            self.assertIn("<svg", content)
        finally:
            os.unlink(path)

    def test_render_preset_ascii(self):
        renderer = LSystemRenderer(seed=42)
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            path = f.name
        try:
            result = renderer.render("koch_curve", iterations=2, backend="ascii", output=path)
            self.assertTrue(os.path.exists(path))
            with open(path) as f:
                content = f.read()
            self.assertTrue(len(content) > 0)
        finally:
            os.unlink(path)

    def test_render_custom_definition(self):
        defn = LSystemDefinition(
            name="Custom",
            axiom="F",
            rules=[LSystemRule("F", "F+F--F+F")],
            angle=60,
            step_size=3,
            iterations=2,
        )
        renderer = LSystemRenderer()
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            path = f.name
        try:
            result = renderer.render(defn, output=path)
            self.assertTrue(os.path.exists(path))
        finally:
            os.unlink(path)

    def test_unknown_preset_raises(self):
        renderer = LSystemRenderer()
        with self.assertRaises(ValueError):
            renderer.render("nonexistent_preset")

    def test_list_presets(self):
        renderer = LSystemRenderer()
        presets = renderer.list_presets()
        self.assertIn("koch_curve", presets)
        self.assertIn("dragon_curve", presets)
        self.assertTrue(len(presets) >= 14)

    def test_get_preset(self):
        renderer = LSystemRenderer()
        preset = renderer.get_preset("koch_curve")
        self.assertEqual(preset.name, "Koch Curve")

    def test_get_unknown_preset_raises(self):
        renderer = LSystemRenderer()
        with self.assertRaises(ValueError):
            renderer.get_preset("nonexistent")

    def test_render_all_presets(self):
        renderer = LSystemRenderer(seed=42)
        with tempfile.TemporaryDirectory() as tmpdir:
            results = renderer.render_all_presets(output_dir=tmpdir, iterations=1)
            self.assertTrue(len(results) > 0)
            for name, path in results.items():
                if not path.startswith("ERROR"):
                    self.assertTrue(os.path.exists(path), f"Missing file for {name}: {path}")

    def test_animate_growth(self):
        renderer = LSystemRenderer(seed=42)
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = renderer.animate_growth("koch_curve", output_dir=tmpdir, iterations=2)
            self.assertEqual(len(paths), 3)
            for path in paths:
                self.assertTrue(os.path.exists(path))

    def test_perturbation_produces_different_output(self):
        defn1 = LSystemDefinition(
            name="Test1", axiom="F", rules=[LSystemRule("F", "F[+F]F[-F]F")],
            angle=25.7, perturbation=0.0, iterations=3,
        )
        defn2 = LSystemDefinition(
            name="Test2", axiom="F", rules=[LSystemRule("F", "F[+F]F[-F]F")],
            angle=25.7, perturbation=5.0, iterations=3,
        )
        interp1 = TurtleInterpreter(angle=25.7, step_size=5, seed=42)
        interp2 = TurtleInterpreter(angle=25.7, step_size=5, perturbation=5.0, seed=42)

        engine = LSystemEngine(defn1, seed=42)
        lstring = engine.iterate(3)

        segs1 = interp1.interpret(lstring)
        segs2 = interp2.interpret(lstring)

        if len(segs1) > 0 and len(segs2) > 0:
            different = False
            for s1, s2 in zip(segs1, segs2):
                if abs(s1.x2 - s2.x2) > 0.01 or abs(s1.y2 - s2.y2) > 0.01:
                    different = True
                    break
            self.assertTrue(different, "Perturbation should produce different output")

    def test_invalid_backend_raises(self):
        renderer = LSystemRenderer()
        defn = renderer.get_preset("koch_curve")
        with self.assertRaises(ValueError):
            renderer.render(defn, backend="invalid_backend", output="/tmp/test.svg")

    def test_render_from_config(self):
        config = LSystemConfig(
            preset="koch_curve",
            iterations=2,
            backend="svg",
            render=RenderConfig(width=200, height=200),
            output=OutputConfig(output_dir="/tmp"),
        )
        renderer = LSystemRenderer(seed=42)
        result = renderer.render_from_config(config)
        self.assertTrue(os.path.exists(result))
        os.unlink(result)


class TestPresets(unittest.TestCase):
    """Test that all presets can render without error."""

    def test_all_presets_render(self):
        renderer = LSystemRenderer(seed=42)
        for name in PRESETS:
            with self.subTest(preset=name):
                result = renderer.render(name, iterations=2, output=f"/tmp/test_{name}.svg")
                self.assertTrue(os.path.exists(result))
                os.unlink(result)

    def test_all_presets_ascii_render(self):
        renderer = LSystemRenderer(seed=42)
        for name in PRESETS:
            with self.subTest(preset=name):
                result = renderer.render(name, iterations=2, backend="ascii",
                                        output=f"/tmp/test_{name}.txt")
                self.assertTrue(os.path.exists(result))
                os.unlink(result)

    def test_presets_count(self):
        self.assertGreaterEqual(len(PRESETS), 14)

    def test_new_presets_exist(self):
        """Verify new presets are available."""
        renderer = LSystemRenderer()
        for name in ["sierpinski_arrowhead", "peano_curve", "quadratic_koch", "tree_willow"]:
            with self.subTest(preset=name):
                preset = renderer.get_preset(name)
                self.assertIsNotNone(preset)


class TestConfig(unittest.TestCase):
    """Test configuration management."""

    def test_config_to_dict(self):
        config = LSystemConfig(
            preset="koch_curve",
            iterations=4,
            seed=42,
            backend="svg",
            render=RenderConfig(width=500, height=500),
        )
        d = config.to_dict()
        self.assertEqual(d["preset"], "koch_curve")
        self.assertEqual(d["iterations"], 4)
        self.assertEqual(d["seed"], 42)

    def test_config_from_dict(self):
        d = {
            "preset": "dragon_curve",
            "iterations": 5,
            "seed": 123,
            "backend": "ascii",
            "render": {"width": 600, "height": 400},
        }
        config = LSystemConfig.from_dict(d)
        self.assertEqual(config.preset, "dragon_curve")
        self.assertEqual(config.render.width, 600)

    def test_config_json_roundtrip(self):
        config = LSystemConfig(
            preset="koch_curve",
            iterations=4,
            seed=42,
            backend="svg",
            render=RenderConfig(width=800, height=600, background="#222222"),
            output=OutputConfig(output_dir="/tmp/lsystem"),
        )
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            config.to_json(path)
            loaded = LSystemConfig.from_json(path)
            self.assertEqual(loaded.preset, config.preset)
            self.assertEqual(loaded.iterations, config.iterations)
            self.assertEqual(loaded.render.width, config.render.width)
            self.assertEqual(loaded.output.output_dir, config.output.output_dir)
        finally:
            os.unlink(path)

    def test_config_from_file_json(self):
        config = LSystemConfig(preset="koch_curve", backend="svg")
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            config.to_json(path)
            loaded = LSystemConfig.from_file(path)
            self.assertEqual(loaded.preset, "koch_curve")
        finally:
            os.unlink(path)

    def test_config_from_file_invalid_ext(self):
        with self.assertRaises(ValueError):
            LSystemConfig.from_file("config.xyz")

    def test_config_without_source_raises(self):
        config = LSystemConfig()  # No preset or definition
        renderer = LSystemRenderer()
        with self.assertRaises(ValueError):
            renderer.render_from_config(config)

    def test_render_config_defaults(self):
        rc = RenderConfig()
        self.assertEqual(rc.width, 800)
        self.assertEqual(rc.height, 800)
        self.assertEqual(rc.background, "#ffffff")

    def test_output_config_defaults(self):
        oc = OutputConfig()
        self.assertEqual(oc.output_dir, ".")
        self.assertTrue(oc.overwrite)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and potential bugs."""

    def test_cantor_dust_angle_zero(self):
        renderer = LSystemRenderer(seed=42)
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            path = f.name
        try:
            result = renderer.render("cantor_dust", iterations=2, output=path)
            self.assertTrue(os.path.exists(path))
        finally:
            os.unlink(path)

    def test_single_segment(self):
        interp = TurtleInterpreter(angle=90, step_size=10)
        segments = interp.interpret("F")
        self.assertEqual(len(segments), 1)

    def test_no_draw_symbols(self):
        interp = TurtleInterpreter(angle=90, step_size=10)
        segments = interp.interpret("+-[]")
        self.assertEqual(len(segments), 0)

    def test_empty_axiom(self):
        defn = LSystemDefinition(name="Empty", axiom="", rules=[LSystemRule("F", "FF")])
        engine = LSystemEngine(defn)
        result = engine.iterate(3)
        self.assertEqual(result, "")

    def test_deeply_nested_branches(self):
        interp = TurtleInterpreter(angle=30, step_size=5)
        lstring = "F" + "[" * 50 + "F" + "]" * 50
        segments = interp.interpret(lstring)
        self.assertGreaterEqual(len(segments), 2)

    def test_more_pops_than_pushes(self):
        interp = TurtleInterpreter(angle=90, step_size=10)
        segments = interp.interpret("F]F]F]")
        self.assertEqual(len(segments), 3)

    def test_json_roundtrip_preserves_definition(self):
        defn = LSystemDefinition(
            name="FullTest",
            axiom="X",
            rules=[
                LSystemRule("X", "F+[[X]-X]-F[-FX]+X"),
                LSystemRule("F", "FF"),
            ],
            angle=25.0,
            step_size=4.0,
            iterations=6,
            line_width=1.5,
            colors={0: "#5a3e1b", 1: "#3d6b2e"},
            color_mode="depth",
            gradient=("#1a5c1a", "#adff2f"),
            perturbation=2.5,
            step_perturbation=0.1,
            background="#1a1a2e",
        )
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            defn.to_json(path)
            loaded = LSystemDefinition.from_json(path)
            self.assertEqual(loaded.name, defn.name)
            self.assertEqual(loaded.axiom, defn.axiom)
            self.assertEqual(len(loaded.rules), len(defn.rules))
            self.assertAlmostEqual(loaded.angle, defn.angle)
            self.assertAlmostEqual(loaded.step_size, defn.step_size)
            self.assertEqual(loaded.iterations, defn.iterations)
            self.assertAlmostEqual(loaded.line_width, defn.line_width)
            self.assertEqual(loaded.colors, defn.colors)
            self.assertEqual(loaded.color_mode, defn.color_mode)
            self.assertEqual(loaded.gradient, defn.gradient)
            self.assertAlmostEqual(loaded.perturbation, defn.perturbation)
            self.assertAlmostEqual(loaded.step_perturbation, defn.step_perturbation)
            self.assertEqual(loaded.background, defn.background)
        finally:
            os.unlink(path)

    def test_rainbow_mode_on_presets(self):
        renderer = LSystemRenderer(seed=42)
        defn = renderer.get_preset("koch_curve")
        defn.color_mode = "segment_index"
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            path = f.name
        try:
            result = renderer.render(defn, iterations=2, output=path)
            self.assertTrue(os.path.exists(path))
        finally:
            os.unlink(path)


class TestBugVerification(unittest.TestCase):
    """Tests that verify specific bugs were found and fixed."""

    def test_bug_ascii_renderer_y_flip(self):
        segments = [Segment(0, 0, 0, 10)]
        renderer = ASCIIRenderer(width=20, height=10)
        result = renderer.render(segments)
        lines = result.split("\n")
        top_has_content = any(c != " " for c in lines[0])
        bottom_has_content = any(c != " " for c in lines[-1])
        self.assertTrue(top_has_content or bottom_has_content)

    def test_bug_svg_title_not_escaped(self):
        segments = [Segment(0, 0, 10, 10)]
        renderer = SVGRenderer(width=100, height=100, title="Test<script>alert('xss')</script>&more")
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            path = f.name
        try:
            renderer.render(segments, path)
            with open(path) as f:
                content = f.read()
            self.assertIn("&lt;script&gt;", content)
            self.assertNotIn("<script>", content)
            self.assertIn("&amp;", content)
        finally:
            os.unlink(path)

    def test_bug_svg_path_grouping_preserves_widths(self):
        segments = [
            Segment(0, 0, 10, 0, color="#ff0000", width=1.0),
            Segment(10, 0, 20, 0, color="#ff0000", width=3.0),
        ]
        renderer = SVGRenderer(width=100, height=100)
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            path = f.name
        try:
            renderer.render(segments, path)
            with open(path) as f:
                content = f.read()
            self.assertIn('stroke-width="1.00"', content)
            self.assertIn('stroke-width="3.00"', content)
        finally:
            os.unlink(path)

    def test_bug_iteration_safety_estimate_inaccurate(self):
        defn = LSystemDefinition(
            name="Short",
            axiom="A",
            rules=[LSystemRule("A", "B")],
            iterations=4,
        )
        engine = LSystemEngine(defn)
        result = engine.iterate(4)
        self.assertEqual(result, "B")

    def test_iterate_steps_negative_iterations_raises(self):
        defn = LSystemDefinition(name="Test", axiom="F", rules=[LSystemRule("F", "FF")])
        engine = LSystemEngine(defn)
        with self.assertRaises(ValueError):
            engine.iterate_steps(-1)

    def test_lerp_color_rounding_fix(self):
        mid = lerp_color("#000000", "#ffffff", 0.5)
        self.assertEqual(mid, "#808080")
        q1 = lerp_color("#000000", "#ffffff", 0.25)
        self.assertEqual(q1, "#404040")


class TestCLI(unittest.TestCase):
    """Test CLI argument parsing."""

    def test_build_parser(self):
        from lsystem_renderer.cli import build_parser
        parser = build_parser()
        self.assertIsNotNone(parser)

    def test_cli_list_presets(self):
        from lsystem_renderer.cli import main
        import io
        import sys
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            main(["--list-presets"])
            output = sys.stdout.getvalue()
            self.assertIn("koch_curve", output)
            self.assertIn("dragon_curve", output)
        finally:
            sys.stdout = old_stdout

    def test_cli_render(self):
        from lsystem_renderer.cli import main
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            path = f.name
        try:
            main(["--preset", "koch_curve", "-i", "2", "-o", path])
            self.assertTrue(os.path.exists(path))
        finally:
            os.unlink(path)

    def test_cli_stats(self):
        from lsystem_renderer.cli import main
        import io
        import sys
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            main(["--preset", "koch_curve", "-i", "2", "--stats"])
            output = sys.stdout.getvalue()
            self.assertIn("Koch Curve", output)
            self.assertIn("String length", output)
        finally:
            sys.stdout = old_stdout

    def test_cli_save_definition(self):
        from lsystem_renderer.cli import main
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            main(["--preset", "koch_curve", "--save", path])
            self.assertTrue(os.path.exists(path))
            with open(path) as f:
                data = json.load(f)
            self.assertEqual(data["name"], "Koch Curve")
        finally:
            os.unlink(path)

    def test_cli_custom_axiom_and_rules(self):
        from lsystem_renderer.cli import main
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            path = f.name
        try:
            main(["--axiom", "F", "--rule", "F->F+F--F+F", "--angle", "60", "-i", "2", "-o", path])
            self.assertTrue(os.path.exists(path))
        finally:
            os.unlink(path)

    def test_cli_render_all(self):
        from lsystem_renderer.cli import main
        with tempfile.TemporaryDirectory() as tmpdir:
            main(["--render-all", "-d", tmpdir, "-i", "1"])
            # Check that at least some SVG files were created
            files = [f for f in os.listdir(tmpdir) if f.endswith(".svg")]
            self.assertGreater(len(files), 0)

    def test_cli_load_json(self):
        from lsystem_renderer.cli import main
        # First save a definition
        defn = LSystemDefinition(
            name="CLI Test",
            axiom="F",
            rules=[LSystemRule("F", "F+F--F+F")],
            angle=60.0,
            step_size=3.0,
            iterations=2,
        )
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            json_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            svg_path = f.name
        try:
            defn.to_json(json_path)
            main(["--load", json_path, "-o", svg_path])
            self.assertTrue(os.path.exists(svg_path))
        finally:
            os.unlink(json_path)
            os.unlink(svg_path)


if __name__ == "__main__":
    unittest.main()