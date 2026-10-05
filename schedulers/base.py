"""
Abstract Base Scheduler for Electronic Support (ES) Spectrum Scanning.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import numpy as np


class BaseScheduler(ABC):
    def __init__(self, num_bands: int, name: str, description: str):
        self.num_bands = num_bands
        self.name = name
        self.description = description
        self.total_steps = 0
        self.total_hits = 0

    @abstractmethod
    def reset(self):
        """Resets internal state at start of simulation episode."""
        self.total_steps = 0
        self.total_hits = 0

    @abstractmethod
    def select_band(self, obs: np.ndarray) -> int:
        """Chooses the next frequency band to dwell on (0 .. num_bands - 1)."""
        pass

    def update(
        self,
        action: int,
        hit: bool,
        snr: float,
        reward: float,
        next_obs: np.ndarray,
        pdw: Optional[Dict[str, Any]] = None
    ):
        """
        Feedback hook called after each receiver dwell.
        Online learning algorithms update weights / value functions here.
        """
        self.total_steps += 1
        if hit:
            self.total_hits += 1
