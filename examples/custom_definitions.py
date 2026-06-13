#!/usr/bin/env python3
"""
Example: Custom L-System Definitions.

This example shows how to define your own L-systems from scratch
and save/load them as JSON.
"""

from lsystem_renderer import (
    LSystemRenderer,
    LSystemDefinition,
    LSystemRule,
    LSystemEngine,
)

renderer = LSystemRenderer(seed=42)

# 1. Simple custom fractal
print("=== Custom Sierpinski Arrowhead ===")
arrowhead = LSystemDefinition(
    name="Custom Sierpinski Arrowhead",
    axiom="A",
    rules=[
        LSystemRule("A", "B-A-B"),
        LSystemRule("B", "A+B+A"),
    ],
    angle=60.0,
    step_size=5.0,
    iterations=7,
    color_mode="segment_index",
)
renderer.render(arrowhead, output="custom_arrowhead.svg")
print("  → custom_arrowhead.svg")

# 2. Stochastic branching plant
print("=== Stochastic Branching Plant ===")
stochastic_plant = LSystemDefinition(
    name="Stochastic Branching Plant",
    axiom="X",
    rules=[
        LSystemRule("X", "F[+X][-X]FX", probability=0.4),
        LSystemRule("X", "F[+X]FX", probability=0.3),
        LSystemRule("X", "F[-X]FX", probability=0.3),
        LSystemRule("F", "FF"),
    ],
    angle=25.0,
    step_size=3.0,
    iterations=5,
    line_width=1.5,
    perturbation=2.0,
    colors={
        0: "#5a3e1b",
        1: "#3d6b2e",
        2: "#4a8c3a",
        3: "#6bb55a",
        4: "#8dd77a",
        5: "#a8f08a",
    },
)
renderer.render(stochastic_plant, output="custom_stochastic_plant.svg")
print("  → custom_stochastic_plant.svg")

# 3. Context-sensitive rule
print("=== Context-Sensitive L-System ===")
context_def = LSystemDefinition(
    name="Context-Sensitive Test",
    axiom="ABCBA",
    rules=[
        LSystemRule("B", "BB", left_context="A", right_context="A"),
        LSystemRule("B", "B", left_context="C", right_context="B"),
    ],
    angle=90.0,
    step_size=5.0,
    iterations=3,
)
engine = LSystemEngine(context_def, seed=42)
lstring = engine.iterate(3)
stats = LSystemEngine.analyze(lstring)
print(f"  String length: {stats['length']:,}")
print(f"  Drawing symbols: {stats['draw_symbols']:,}")

# 4. Save and load custom definition
print("=== Save/Load JSON ===")
arrowhead.to_json("custom_arrowhead.json")
print("  Saved to custom_arrowhead.json")

loaded = LSystemDefinition.from_json("custom_arrowhead.json")
renderer.render(loaded, output="custom_reloaded.svg")
print("  Reloaded and rendered → custom_reloaded.svg")

# 5. Create a definition using rule parsing
print("=== Rule Parsing ===")
rule1 = LSystemRule.parse("F->F+F-F-F+F")
rule2 = LSystemRule.parse("X->F+[[X]-X]-F[-FX]+X")
print(f"  Parsed rule: {rule1.predecessor} → {rule1.successor}")
print(f"  Parsed rule: {rule2.predecessor} → {rule2.successor}")

print("\nDone!")