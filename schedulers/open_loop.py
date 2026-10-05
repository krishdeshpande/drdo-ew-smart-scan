"""
Classical Open-Loop Scanning Strategies (Baselines).
Includes Uniform Sequential Sweep, Random Sweep, and Priority Open-Loop.
"""

import numpy as np
from typing import Optional, List
from .base import BaseScheduler


class UniformSequentialScheduler(BaseScheduler):
    """
    Classical Open-Loop Sequential Sweep:
    Sweeps bands in fixed round-robin order: 0 -> 1 -> ... -> N-1 -> 0.
    Maximizes sweep speed, but blind to emitter activity and hostile threats.
    """
    def __init__(self, num_bands: int):
        super().__init__(
            num_bands=num_bands,
            name="Uniform Sequential (Open-Loop)",
            description="Classical round-robin sweep across all surveillance bands."
        )
        self.current_band = 0

    def reset(self):
        super().reset()
        self.current_band = 0

    def select_band(self, obs: np.ndarray) -> int:
        chosen = self.current_band
        self.current_band = (self.current_band + 1) % self.num_bands
        return chosen


class RandomSweepScheduler(BaseScheduler):
    """
    Random Sweep (Open-Loop):
    Randomly chooses a frequency band uniformly at each step.
    Prevents adversarial anticipation but has high variance.
    """
    def __init__(self, num_bands: int, seed: int = 42):
        super().__init__(
            num_bands=num_bands,
            name="Random Sweep (Open-Loop)",
            description="Uniformly random channel sampling."
        )
        self.rng = np.random.RandomState(seed)

    def reset(self):
        super().reset()

    def select_band(self, obs: np.ndarray) -> int:
        return int(self.rng.randint(0, self.num_bands))


class StaticPriorityScheduler(BaseScheduler):
    """
    Static Priority Sweep (Open-Loop):
    Bands are sampled according to static pre-mission intelligence weights.
    Vulnerable if real-world emitters differ from pre-mission assumptions.
    """
    def __init__(self, num_bands: int, prior_weights: Optional[List[float]] = None, seed: int = 42):
        super().__init__(
            num_bands=num_bands,
            name="Static Priority (Open-Loop)",
            description="Dwell allocation governed by fixed pre-mission intelligence weights."
        )
        if prior_weights is None:
            # Default: heavier weight on center bands
            weights = np.ones(num_bands)
            weights[num_bands // 2] = 3.0
            self.probs = weights / weights.sum()
        else:
            arr = np.array(prior_weights, dtype=float)
            self.probs = arr / arr.sum()
        self.rng = np.random.RandomState(seed)

    def reset(self):
        super().reset()

    def select_band(self, obs: np.ndarray) -> int:
        return int(self.rng.choice(self.num_bands, p=self.probs))
