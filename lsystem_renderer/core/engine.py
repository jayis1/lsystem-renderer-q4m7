"""
L-system string rewriting engine.

Supports deterministic, stochastic, context-sensitive, and parametric rules.
"""

from __future__ import annotations

import logging
import random
from collections import defaultdict
from typing import Any, Dict, List, Optional

from .types import LSystemDefinition, LSystemRule

logger = logging.getLogger(__name__)


class LSystemEngine:
    """Core engine that performs L-system string rewriting.

    Supports:
      - Deterministic rules
      - Stochastic rules (probability weights)
      - Context-sensitive rules (left/right context matching)
      - Parametric rules (conditions evaluated as Python expressions)
    """

    # Maximum estimated string length to allow (safety guard)
    MAX_ESTIMATED_LENGTH = 10_000_000
    # Maximum allowed iterations (hard limit)
    MAX_ITERATIONS = 50

    def __init__(self, definition: LSystemDefinition, seed: Optional[int] = None):
        self.definition = definition
        self.rng = random.Random(seed)
        self._param_context: Dict[str, Any] = {}
        logger.debug(
            "Initialized engine for '%s' with seed=%s",
            definition.name, seed,
        )

    def _build_rule_map(self) -> Dict[str, List[LSystemRule]]:
        """Index rules by predecessor symbol for O(1) lookup."""
        rule_map: Dict[str, List[LSystemRule]] = defaultdict(list)
        for rule in self.definition.rules:
            rule_map[rule.predecessor].append(rule)
        return rule_map

    def _match_context(
        self, rule: LSystemRule, symbol: str, string: str, pos: int
    ) -> bool:
        """Check left and right context for context-sensitive rules.

        Context matching ignores bracket symbols [] when scanning for neighbors,
        matching the standard L-system context-sensitive semantics.
        """
        if rule.left_context is not None:
            # Walk left skipping brackets
            depth = 0
            chars_matched = 0
            i = pos - 1
            left_str = ""
            while i >= 0 and chars_matched < len(rule.left_context):
                ch = string[i]
                if ch == "]":
                    depth += 1
                elif ch == "[":
                    depth -= 1
                    if depth < 0:
                        depth = 0
                elif depth == 0:
                    left_str = ch + left_str
                    chars_matched += 1
                i -= 1
            if left_str != rule.left_context:
                return False

        if rule.right_context is not None:
            depth = 0
            chars_matched = 0
            i = pos + 1
            right_str = ""
            while i < len(string) and chars_matched < len(rule.right_context):
                ch = string[i]
                if ch == "[":
                    depth += 1
                elif ch == "]":
                    depth -= 1
                    if depth < 0:
                        depth = 0
                elif depth == 0:
                    right_str += ch
                    chars_matched += 1
                i += 1
            if right_str != rule.right_context:
                return False

        return True

    def _evaluate_condition(self, rule: LSystemRule) -> bool:
        """Evaluate a parametric rule's condition safely."""
        if rule.condition is None:
            return True
        try:
            # Restricted eval: only allow basic math operations
            safe_builtins = {
                "abs": abs, "min": min, "max": max,
                "int": int, "float": float, "round": round,
            }
            return bool(eval(rule.condition, {"__builtins__": safe_builtins}, self._param_context))
        except Exception:
            logger.debug("Condition evaluation failed for: %s", rule.condition)
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

        # Stochastic selection using weighted sampling
        total_weight = sum(r.probability for r in matching)
        if total_weight <= 0:
            return matching[0]
        roll = self.rng.uniform(0, total_weight)
        cumulative = 0.0
        for rule in matching:
            cumulative += rule.probability
            if roll <= cumulative:
                return rule
        return matching[-1]

    def _validate_iterations(self, n: int) -> None:
        """Validate iteration count and check safety limits."""
        if n < 0:
            raise ValueError(f"Iterations must be non-negative, got {n}")
        if n > self.MAX_ITERATIONS:
            estimated_length = len(self.definition.axiom) * (
                max(len(r.successor) for r in self.definition.rules)
                if self.definition.rules else 2
            ) ** n
            if estimated_length > self.MAX_ESTIMATED_LENGTH:
                raise ValueError(
                    f"Iteration {n} would produce an estimated "
                    f"{estimated_length:,} characters. "
                    f"Reduce iterations or use a simpler L-system."
                )

    def _apply_rules(self, current: str, rule_map: Dict[str, List[LSystemRule]]) -> str:
        """Apply production rules to the current string for one iteration."""
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
        return "".join(next_str_parts)

    def iterate(self, iterations: Optional[int] = None) -> str:
        """Apply production rules for the given number of iterations.

        Returns the produced string.
        """
        n = iterations if iterations is not None else self.definition.iterations
        self._validate_iterations(n)

        current = self.definition.axiom
        rule_map = self._build_rule_map()

        for i in range(n):
            current = self._apply_rules(current, rule_map)
            logger.debug(
                "Iteration %d/%d: string length = %d",
                i + 1, n, len(current),
            )

        return current

    def iterate_steps(self, iterations: Optional[int] = None) -> List[str]:
        """Apply production rules, returning the string at each iteration step.

        Useful for growth animations and debugging.
        """
        n = iterations if iterations is not None else self.definition.iterations
        self._validate_iterations(n)

        results = [self.definition.axiom]
        current = self.definition.axiom
        rule_map = self._build_rule_map()

        for i in range(n):
            current = self._apply_rules(current, rule_map)
            results.append(current)
            logger.debug(
                "Step %d/%d: string length = %d",
                i + 1, n, len(current),
            )

        return results

    @staticmethod
    def analyze(lstring: str) -> Dict[str, Any]:
        """Analyze an L-system string and return statistics."""
        if not lstring:
            return {
                "length": 0,
                "symbols": {},
                "draw_symbols": 0,
                "unique_symbols": 0,
                "branch_depth": 0,
            }

        symbol_counts: Dict[str, int] = defaultdict(int)
        draw_symbols = 0
        max_depth = 0
        depth = 0

        for ch in lstring:
            symbol_counts[ch] += 1
            if ch in ("F", "G"):
                draw_symbols += 1
            if ch == "[":
                depth += 1
                max_depth = max(max_depth, depth)
            elif ch == "]":
                depth = max(0, depth - 1)

        return {
            "length": len(lstring),
            "symbols": dict(symbol_counts),
            "draw_symbols": draw_symbols,
            "unique_symbols": len(symbol_counts),
            "branch_depth": max_depth,
        }