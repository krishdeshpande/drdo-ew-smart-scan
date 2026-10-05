"""
Predictive Temporal Scheduler for Spatially Scanning Radars.
Learns rotation periods and beam arrival times online to execute lookahead
interceptions with minimal Average Intercept Time Error.
"""

import numpy as np
from collections import deque
from typing import Optional, Dict, Any, List
from .base import BaseScheduler


class PredictiveTemporalScheduler(BaseScheduler):
    """
    Predictive Lookahead Interceptor:
    Estimates emitter rotation/scan period (T_scan) for each frequency band
    from intercepted pulse trains. Proactively tunes the receiver to the target
    band immediately before the mainlobe beam is predicted to illuminate the antenna.
    
    Tracks:
    - Average Intercept Time Error: |t_predicted - t_actual|
    - Percentage of Correct Predictions: Successful intercepts during predicted windows.
    """
    def __init__(
        self,
        num_bands: int,
        dt_sec: float = 0.025,
        lookahead_tolerance_slots: int = 2,
        min_hits_for_period_est: int = 3,
        fallback_scheduler: Optional[BaseScheduler] = None
    ):
        super().__init__(
            num_bands=num_bands,
            name="Predictive Temporal Interceptor",
            description="Anticipates periodic radar beam illumination times to minimize intercept time error."
        )
        self.dt_sec = dt_sec
        self.lookahead_tolerance_slots = lookahead_tolerance_slots
        self.min_hits_for_period_est = min_hits_for_period_est

        # Band tracking state
        self.hit_timestamps: List[deque] = [deque(maxlen=20) for _ in range(num_bands)]
        self.estimated_periods: np.ndarray = np.zeros(num_bands, dtype=float)
        self.last_hit_step: np.ndarray = np.full(num_bands, -9999, dtype=int)
        self.predicted_next_step: np.ndarray = np.full(num_bands, -9999, dtype=int)

        # Performance figures of merit
        self.total_predictions_made = 0
        self.correct_predictions = 0
        self.time_errors: List[float] = []

        # Sequential fallback for bands without periodic estimate
        self.fallback_idx = 0
        self.current_step = 0
        self.active_prediction_band: Optional[int] = None

    def reset(self):
        super().reset()
        for d in self.hit_timestamps:
            d.clear()
        self.estimated_periods.fill(0.0)
        self.last_hit_step.fill(-9999)
        self.predicted_next_step.fill(-9999)
        self.total_predictions_made = 0
        self.correct_predictions = 0
        self.time_errors.clear()
        self.fallback_idx = 0
        self.current_step = 0
        self.active_prediction_band = None

    def select_band(self, obs: np.ndarray) -> int:
        self.current_step += 1

        # Check if any band has a predicted beam arrival within tolerance window
        imminent_bands = []
        for b in range(self.num_bands):
            if self.predicted_next_step[b] > 0:
                time_diff = self.predicted_next_step[b] - self.current_step
                if abs(time_diff) <= self.lookahead_tolerance_slots:
                    urgency = -abs(time_diff)  # Closer to 0 = higher urgency
                    imminent_bands.append((urgency, b))

        if imminent_bands:
            # Sort by urgency
            imminent_bands.sort(key=lambda x: x[0], reverse=True)
            chosen_band = imminent_bands[0][1]
            self.active_prediction_band = chosen_band
            self.total_predictions_made += 1
            return chosen_band

        # If no arrival is imminent, explore via systematic sweep to discover new emitters
        self.active_prediction_band = None
        chosen_band = self.fallback_idx
        self.fallback_idx = (self.fallback_idx + 1) % self.num_bands
        return chosen_band

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

        # Check if this dwell was a prediction
        if self.active_prediction_band == action:
            if hit:
                self.correct_predictions += 1
                pred_step = self.predicted_next_step[action]
                error_sec = abs(self.current_step - pred_step) * self.dt_sec
                self.time_errors.append(error_sec)

        # Update period estimation on real hit
        if hit:
            self.hit_timestamps[action].append(self.current_step)
            prev_step = self.last_hit_step[action]
            self.last_hit_step[action] = self.current_step

            # Calculate period if we have enough observations
            if len(self.hit_timestamps[action]) >= self.min_hits_for_period_est:
                ts_list = list(self.hit_timestamps[action])
                diffs = [ts_list[i] - ts_list[i-1] for i in range(1, len(ts_list))]
                # Filter out adjacent bursts (e.g. diffs < 3 slots)
                scan_diffs = [d for d in diffs if d > 10]
                if scan_diffs:
                    median_period_slots = float(np.median(scan_diffs))
                    self.estimated_periods[action] = median_period_slots * self.dt_sec
                    # Schedule next arrival
                    self.predicted_next_step[action] = int(round(self.current_step + median_period_slots))

    @property
    def prediction_accuracy_pct(self) -> float:
        if self.total_predictions_made == 0:
            return 0.0
        return (self.correct_predictions / self.total_predictions_made) * 100.0

    @property
    def avg_intercept_time_error_sec(self) -> float:
        if not self.time_errors:
            return 0.0
        return float(np.mean(self.time_errors))
