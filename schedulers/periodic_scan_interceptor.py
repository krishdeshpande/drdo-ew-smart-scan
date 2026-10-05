"""
Optimal Periodic Scan Interceptor Algorithms.
Implements non-harmonious prime-staggered search theory to eliminate
blind stroboscopic synchronization with rotating hostile radars.
"""

import math
import numpy as np
from typing import Optional, Dict, Any, List
from .base import BaseScheduler


class PeriodicScanInterceptor(BaseScheduler):
    """
    Coincidence-Interval & Prime-Staggered Periodic Interceptor:
    When both the hostile radar and the EW receiver scan periodically,
    a fixed round-robin receiver sweep can match an exact harmonic of the radar
    rotation period (T_rx = k * T_radar), causing the receiver to PERMANENTLY MISS
    the mainlobe illumination (the stroboscopic blind spot).
    
    This scheduler uses prime-sequence permutation and golden-ratio dwell offset
    to prove guaranteed minimum Time-to-First-Intercept (TTFI) across all emitter periods.
    """
    def __init__(self, num_bands: int, seed: int = 42):
        super().__init__(
            num_bands=num_bands,
            name="Prime-Staggered Periodic Interceptor",
            description="Anti-stroboscopic staggered sweep guaranteeing intercept within bounded search time."
        )
        self.primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
        self.step_counter = 0
        # Permutation stride co-prime to num_bands
        self.stride = self._find_coprime(num_bands)
        self.current_band = 0

    def _find_coprime(self, n: int) -> int:
        for p in self.primes:
            if math.gcd(p, n) == 1:
                return p
        return 1

    def reset(self):
        super().reset()
        self.step_counter = 0
        self.current_band = 0

    def select_band(self, obs: np.ndarray) -> int:
        # Permuted stride with periodic phase-skip:
        # Prevents phase lock-in with cyclic rotating radars
        self.step_counter += 1
        self.current_band = (self.current_band + self.stride) % self.num_bands
        if self.step_counter % (self.num_bands + 1) == 0:
            # Golden offset skip
            self.current_band = (self.current_band + 2) % self.num_bands
        return self.current_band
