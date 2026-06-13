"""
Turtle graphics interpreter for L-system strings.

Converts L-system strings into geometric segments using turtle graphics semantics.
"""

from __future__ import annotations

import copy
import logging
import math
import random
from typing import Dict, List, Optional

from .types import TurtleState, Segment

logger = logging.getLogger(__name__)


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
      <      — Divide step size by 2
      >      — Multiply step size by 2
      @      — Multiply step size by 0.8 (shrink slightly)
    """

    DEFAULT_STEP_FACTOR = 0.7  # For ( and ) symbols

    def __init__(
        self,
        angle: float = 25.0,
        step_size: float = 5.0,
        line_width: float = 1.0,
        colors: Optional[Dict[int, str]] = None,
        perturbation: float = 0.0,
        step_perturbation: float = 0.0,
        seed: Optional[int] = None,
    ):
        self.initial_angle = angle
        self.initial_step_size = step_size
        self.initial_line_width = line_width
        self.colors = colors or {}
        self.perturbation = perturbation
        self.step_perturbation = step_perturbation
        self.rng = random.Random(seed)

    def interpret(self, lstring: str) -> List[Segment]:
        """Interpret an L-system string and return a list of line segments.

        Args:
            lstring: The L-system string to interpret.

        Returns:
            List of Segment objects representing the drawn lines.
        """
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
        step_factor = self.DEFAULT_STEP_FACTOR
        seg_index = 0

        for ch in lstring:
            if ch in ("F", "G"):
                # Apply perturbation to angle and step for organic feel
                angle_pert = 0.0
                step_pert_factor = 1.0
                if self.perturbation > 0:
                    angle_pert = self.rng.gauss(0, self.perturbation)
                if self.step_perturbation > 0:
                    step_pert_factor = 1.0 + self.rng.gauss(0, self.step_perturbation)
                    step_pert_factor = max(0.5, min(1.5, step_pert_factor))

                actual_angle = state.angle + angle_pert
                actual_step = state.step_size * step_pert_factor

                rad = math.radians(actual_angle)
                new_x = state.x + actual_step * math.cos(rad)
                new_y = state.y + actual_step * math.sin(rad)

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
                        segment_index=seg_index,
                    )
                )
                seg_index += 1
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

            elif ch == "@":
                state.step_size *= 0.8

        logger.debug(
            "Interpreted string of length %d → %d segments",
            len(lstring), len(segments),
        )
        return segments