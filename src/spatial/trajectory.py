from __future__ import annotations

import math
from collections import deque
from typing import Deque


class Trajectory:
    """Bounded history of a person's movements."""

    def __init__(self, max_points: int = 50) -> None:
        self.max_points = max_points
        self.positions: Deque[tuple[float, float]] = deque(maxlen=max_points)

    def update(self, position: tuple[float, float]) -> None:
        if position is None:
            return
        self.positions.append(position)

    def total_distance(self) -> float:
        if len(self.positions) < 2:
            return 0.0
        total = 0.0
        for previous, current in zip(self.positions, list(self.positions)[1:]):
            total += math.dist(previous, current)
        return total

    def average_movement(self) -> float:
        if len(self.positions) < 2:
            return 0.0
        return self.total_distance() / (len(self.positions) - 1)

    def direction(self) -> tuple[float, float] | None:
        if len(self.positions) < 2:
            return None
        start = self.positions[0]
        end = self.positions[-1]
        delta_x = end[0] - start[0]
        delta_y = end[1] - start[1]
        magnitude = math.hypot(delta_x, delta_y)
        if magnitude == 0:
            return (0.0, 0.0)
        return (delta_x / magnitude, delta_y / magnitude)

    def is_stationary(self, threshold: float = 2.0) -> bool:
        if len(self.positions) < 2:
            return True
        return self.total_distance() <= threshold

    def extract(self) -> list[tuple[float, float]]:
        return list(self.positions)
