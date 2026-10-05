"""
Multi-Armed Bandit Schedulers for Non-Stationary Electronic Warfare Spectrum Surveillance.
Includes Discounted UCB (D-UCB) and EXP3 (Adversarial Bandit).
"""

import math
import numpy as np
from typing import Optional, Dict, Any
from .base import BaseScheduler


class DiscountedUCBScheduler(BaseScheduler):
    """
    Discounted Upper Confidence Bound (D-UCB) for Non-Stationary Spectrum:
    In EW, hostile emitters hop and rotate, making old observations stale.
    D-UCB discounts older observations geometrically by factor gamma in (0, 1),
    enabling fast adaptation to newly active or silent emitters without prior intelligence.
    """
    def __init__(
        self,
        num_bands: int,
        gamma: float = 0.90,       # Discount factor (0.80 .. 0.98)
        xi: float = 0.5,           # Exploration factor
        b_upper: float = 1.0,      # Reward upper bound
        seed: int = 42
    ):
        super().__init__(
            num_bands=num_bands,
            name="Discounted UCB (Online MAB)",
            description=f"Adaptive Non-Stationary Bandit with geometric discounting (gamma={gamma})."
        )
        self.gamma = gamma
        self.xi = xi
        self.b_upper = b_upper
        self.rng = np.random.RandomState(seed)

        self.effective_counts = np.zeros(num_bands, dtype=float)
        self.effective_rewards = np.zeros(num_bands, dtype=float)
        self.t = 0

    def reset(self):
        super().reset()
        self.effective_counts = np.zeros(self.num_bands, dtype=float)
        self.effective_rewards = np.zeros(self.num_bands, dtype=float)
        self.t = 0

    def select_band(self, obs: np.ndarray) -> int:
        self.t += 1

        # Initial exploration: try each arm once
        for b in range(self.num_bands):
            if self.effective_counts[b] < 0.5:
                return b

        # Compute discounted total trials: n(gamma, t) = sum_i N_i(gamma, t)
        n_gamma = max(1.0, float(np.sum(self.effective_counts)))

        ucb_indices = np.zeros(self.num_bands, dtype=float)
        for b in range(self.num_bands):
            n_b = max(1e-4, self.effective_counts[b])
            empirical_mean = self.effective_rewards[b] / n_b
            # Exploration padding
            padding = 2.0 * self.b_upper * math.sqrt((self.xi * math.log(n_gamma)) / n_b)
            ucb_indices[b] = empirical_mean + padding

        # Break ties with small random noise
        noisy_indices = ucb_indices + self.rng.normal(0, 1e-6, size=self.num_bands)
        return int(np.argmax(noisy_indices))

    def update(
        self,
        action: int,
        hit: bool,
        snr: float,
        reward: float,
        next_obs: np.ndarray,
        pdw: Optional[Dict[str, Any]] = None
    ):
        super().update(action, hit, snr, reward, next_obs, pdw)

        # Apply geometric decay to all arms
        self.effective_counts *= self.gamma
        self.effective_rewards *= self.gamma

        # Increment selected arm
        self.effective_counts[action] += 1.0
        # Normalize reward to [0, 1] range for bandit stability
        normalized_reward = 1.0 if hit else 0.0
        if pdw and "is_mainlobe" in pdw and pdw["is_mainlobe"]:
            normalized_reward = 1.0
        self.effective_rewards[action] += normalized_reward


class Exp3Scheduler(BaseScheduler):
    """
    Exp3 (Exponential-weight algorithm for Exploration and Exploitation):
    Designed for adversarial environments, such as hostile emitters deliberately
    hopping frequency to evade electronic interception.
    """
    def __init__(self, num_bands: int, gamma: float = 0.15, seed: int = 42):
        super().__init__(
            num_bands=num_bands,
            name="EXP3 (Adversarial MAB)",
            description=f"Adversarial bandit with exponential weighting (gamma={gamma})."
        )
        self.gamma = gamma
        self.weights = np.ones(num_bands, dtype=float)
        self.probs = np.ones(num_bands, dtype=float) / num_bands
        self.rng = np.random.RandomState(seed)

    def reset(self):
        super().reset()
        self.weights = np.ones(self.num_bands, dtype=float)
        self.probs = np.ones(self.num_bands, dtype=float) / self.num_bands

    def select_band(self, obs: np.ndarray) -> int:
        sum_w = np.sum(self.weights)
        if sum_w <= 0 or np.isnan(sum_w):
            self.weights = np.ones(self.num_bands, dtype=float)
            sum_w = float(self.num_bands)

        self.probs = (1.0 - self.gamma) * (self.weights / sum_w) + (self.gamma / self.num_bands)
        self.probs = np.clip(self.probs, 1e-6, 1.0)
        self.probs /= np.sum(self.probs)

        return int(self.rng.choice(self.num_bands, p=self.probs))

    def update(
        self,
        action: int,
        hit: bool,
        snr: float,
        reward: float,
        next_obs: np.ndarray,
        pdw: Optional[Dict[str, Any]] = None
    ):
        super().update(action, hit, snr, reward, next_obs, pdw)
        norm_r = 1.0 if hit else 0.0
        est_reward = norm_r / max(1e-4, self.probs[action])
        # Update exponential weight
        self.weights[action] *= math.exp((self.gamma * est_reward) / self.num_bands)
        # Prevent numerical overflow
        max_w = np.max(self.weights)
        if max_w > 1e12:
            self.weights /= max_w
