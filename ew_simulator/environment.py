"""
Simulated RF Electronic Warfare Environment.
Maintains ground truth of all frequency channels across time slots,
steps emitters, executes ES receiver dwells, and computes rewards.
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from .emitters import BaseEmitter, EmitterTransmission, create_standard_ew_scenario
from .receiver import ESReceiver, ReceiverMeasurement


@dataclass
class SimulationStepResult:
    step_idx: int
    time_sec: float
    measurement: ReceiverMeasurement
    ground_truth_active_bands: List[int]
    all_bands_status: np.ndarray        # Boolean array [num_bands]: True = active
    all_bands_powers: np.ndarray        # Float array [num_bands]: True rx power in dBm
    active_transmissions: List[EmitterTransmission]
    reward: float
    threats_missed: List[str]


class RFEnvironment:
    """
    Simulation Environment for Electronic Support Receiver Scheduling.
    Provides discrete time-step transitions, full ground truth recording,
    and reward computation for reinforcement learning.
    """
    def __init__(
        self,
        num_bands: int = 8,
        dt_sec: float = 0.025,  # 25 ms dwell/time slot
        max_steps: int = 1000,
        emitters: Optional[List[BaseEmitter]] = None,
        receiver: Optional[ESReceiver] = None,
        hit_reward_base: float = 10.0,
        miss_penalty_base: float = 1.0,
        switching_cost: float = 0.5,
        false_alarm_penalty: float = 2.0,
        seed: int = 42
    ):
        self.num_bands = num_bands
        self.dt_sec = dt_sec
        self.max_steps = max_steps
        self.emitters = emitters if emitters is not None else create_standard_ew_scenario(num_bands)
        self.receiver = receiver if receiver is not None else ESReceiver(num_bands=num_bands, seed=seed)

        self.hit_reward_base = hit_reward_base
        self.miss_penalty_base = miss_penalty_base
        self.switching_cost = switching_cost
        self.false_alarm_penalty = false_alarm_penalty

        self.step_idx = 0
        self.current_time_sec = 0.0
        self.rng = np.random.RandomState(seed)

        # History tracking
        self.history_actions: List[int] = []
        self.history_hits: List[bool] = []
        self.history_ground_truth: List[np.ndarray] = []

    def reset(self) -> np.ndarray:
        """
        Resets environment to t=0 and returns initial state vector.
        """
        self.step_idx = 0
        self.current_time_sec = 0.0
        self.history_actions.clear()
        self.history_hits.clear()
        self.history_ground_truth.clear()

        # Reset receiver state
        self.receiver.current_band = 0

        # Return state representation (e.g. zeros for hit history)
        return self.get_observation()

    def step(self, action_band: int) -> SimulationStepResult:
        """
        Executes one time-step:
        1. Emitters evolve and transmit.
        2. Receiver dwells on action_band.
        3. Measurement is gathered.
        4. Reward is calculated.
        """
        assert 0 <= action_band < self.num_bands, f"Invalid band {action_band}"

        self.current_time_sec = self.step_idx * self.dt_sec

        # 1. Step all emitters and collect active transmissions
        active_txs: List[EmitterTransmission] = []
        for emitter in self.emitters:
            tx = emitter.step(t=self.current_time_sec, dt=self.dt_sec)
            if tx is not None:
                active_txs.append(tx)

        # Ground truth status array across all channels
        all_bands_status = np.zeros(self.num_bands, dtype=bool)
        all_bands_powers = np.full(self.num_bands, self.receiver.noise_floor_dbm, dtype=float)

        for tx in active_txs:
            b = tx.band
            all_bands_status[b] = True
            rx_pwr = tx.tx_power_dbm + self.receiver.rx_antenna_gain_dbi - self.receiver.path_loss_db
            if rx_pwr > all_bands_powers[b]:
                all_bands_powers[b] = rx_pwr

        active_bands = [i for i, active in enumerate(all_bands_status) if active]

        # 2. Execute receiver dwell and measurement
        meas = self.receiver.tune_and_measure(action_band, active_txs)

        # 3. Threat accounting
        # Which emitters were transmitting elsewhere that we missed?
        missed_threats = []
        for tx in active_txs:
            if tx.band != action_band:
                missed_threats.append(tx.emitter_id)

        # 4. Compute composite EW reward
        reward = 0.0
        if meas.hit and not meas.false_alarm:
            # Intercept bonus scaled by threat priority (1 to 5)
            reward += self.hit_reward_base * meas.priority_weight
        elif meas.false_alarm:
            # False alarm penalty
            reward -= self.false_alarm_penalty
        else:
            # Miss: penalty scaled by number and priority of active hostile threats missed
            total_missed_priority = sum(tx.priority_weight for tx in active_txs if tx.band != action_band)
            reward -= (self.miss_penalty_base + 0.5 * total_missed_priority)

        # Switching overhead penalty (cost of tuning synthesizers)
        if meas.switched_band:
            reward -= self.switching_cost

        # Record history
        self.history_actions.append(action_band)
        self.history_hits.append(meas.hit and not meas.false_alarm)
        self.history_ground_truth.append(all_bands_status.copy())

        self.step_idx += 1

        return SimulationStepResult(
            step_idx=self.step_idx,
            time_sec=self.current_time_sec,
            measurement=meas,
            ground_truth_active_bands=active_bands,
            all_bands_status=all_bands_status,
            all_bands_powers=all_bands_powers,
            active_transmissions=active_txs,
            reward=reward,
            threats_missed=missed_threats
        )

    def get_observation(self, window_size: int = 10) -> np.ndarray:
        """
        Constructs an observation vector for RL/ML schedulers:
        - Recent hit/miss rate per band over window
        - Steps elapsed since last visit per band
        - Steps elapsed since last hit per band
        - Current band (one-hot)
        """
        obs = []

        # 1. Band occupancy / hit history in recent window
        recent_hits = np.zeros(self.num_bands, dtype=np.float32)
        recent_visits = np.zeros(self.num_bands, dtype=np.float32)

        start_idx = max(0, len(self.history_actions) - window_size)
        for i in range(start_idx, len(self.history_actions)):
            b = self.history_actions[i]
            recent_visits[b] += 1.0
            if self.history_hits[i]:
                recent_hits[b] += 1.0

        hit_rates = np.divide(recent_hits, np.maximum(1.0, recent_visits))
        obs.extend(hit_rates.tolist())

        # 2. Time since last visit per band (normalized)
        time_since_visit = np.full(self.num_bands, fill_value=1.0, dtype=np.float32)
        for b in range(self.num_bands):
            # Find reverse index of last visit
            for rev_i, act in enumerate(reversed(self.history_actions)):
                if act == b:
                    time_since_visit[b] = min(1.0, (rev_i + 1) / 50.0)
                    break
        obs.extend(time_since_visit.tolist())

        # 3. Current band one-hot
        cur_band_onehot = np.zeros(self.num_bands, dtype=np.float32)
        cur_band_onehot[self.receiver.current_band] = 1.0
        obs.extend(cur_band_onehot.tolist())

        return np.array(obs, dtype=np.float32)
