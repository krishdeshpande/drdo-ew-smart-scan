"""
Electronic Support (ES) Receiver System Model for Wideband Spectrum Surveillance.
Includes Instantaneous Bandwidth constraints, Sensitivity Thresholding,
Noise Floor, Switching Delay, and Detection Statistics (Pd, Pfa).
"""

import math
import numpy as np
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from .emitters import EmitterTransmission


@dataclass
class ReceiverMeasurement:
    band: int
    hit: bool                   # Signal detected above threshold
    false_alarm: bool           # Detection triggered solely by noise
    true_signal_present: bool   # Ground-truth signal presence
    rx_power_dbm: float         # Measured power in dBm
    snr_db: float               # Estimated Signal-to-Noise Ratio
    emitter_id: Optional[str]   # Identified/ground-truth emitter if intercepted
    threat_level: int           # Threat level of intercepted emitter
    priority_weight: float      # Intercept priority weight
    switched_band: bool         # True if receiver incurred switching overhead
    pdw: Optional[Dict[str, Any]] # Extracted Pulse Descriptor Word if intercepted


class ESReceiver:
    """
    Tunable Electronic Support (ES) Receiver.
    - Instantaneous Bandwidth: Tunes to 1 band at a time out of N surveillance bands.
    - Dwell time: Fixed or variable dwell duration per time slot.
    - Switching overhead: Latency penalty when hopping to a non-adjacent or different band.
    - Detection model: Thermal noise floor + Rayleigh/Gaussian exceedance with specified Pfa / Sensitivity.
    """
    def __init__(
        self,
        num_bands: int = 8,
        noise_floor_dbm: float = -95.0,
        noise_std_db: float = 2.0,
        sensitivity_threshold_dbm: float = -85.0,
        p_fa_nominal: float = 1e-3,
        switching_penalty_cost: float = 0.5,
        path_loss_db: float = 100.0,
        rx_antenna_gain_dbi: float = 3.0,
        seed: int = 42
    ):
        self.num_bands = num_bands
        self.noise_floor_dbm = noise_floor_dbm
        self.noise_std_db = noise_std_db
        self.sensitivity_threshold_dbm = sensitivity_threshold_dbm
        self.p_fa_nominal = p_fa_nominal
        self.switching_penalty_cost = switching_penalty_cost
        self.path_loss_db = path_loss_db
        self.rx_antenna_gain_dbi = rx_antenna_gain_dbi

        self.current_band = 0
        self.rng = np.random.RandomState(seed)

    def tune_and_measure(
        self,
        target_band: int,
        transmissions: List[EmitterTransmission]
    ) -> ReceiverMeasurement:
        """
        Dwells on target_band and measures RF power and pulse characteristics.
        """
        switched = (target_band != self.current_band)
        self.current_band = target_band

        # Check if any emitter transmitted in the tuned band
        matching_transmissions = [t for t in transmissions if t.band == target_band]

        # Add Gaussian thermal noise sample
        noise_sample = self.rng.normal(self.noise_floor_dbm, self.noise_std_db)

        if matching_transmissions:
            # Signal present: select the strongest transmission in the band
            best_tx = max(matching_transmissions, key=lambda tx: tx.tx_power_dbm)
            
            # Friis free-space attenuation / propagation model
            rx_signal_power_dbm = best_tx.tx_power_dbm + self.rx_antenna_gain_dbi - self.path_loss_db
            
            # Combine signal power + noise in linear milliwatt domain
            sig_mw = 10.0 ** (rx_signal_power_dbm / 10.0)
            noise_mw = 10.0 ** (noise_sample / 10.0)
            total_mw = sig_mw + noise_mw
            total_rx_power_dbm = 10.0 * math.log10(max(1e-12, total_mw))
            
            snr_db = max(0.0, rx_signal_power_dbm - self.noise_floor_dbm)

            # Detection decision: power must exceed sensitivity threshold
            # High SNR gives Pd ~ 1.0; low SNR rolls off
            if total_rx_power_dbm >= self.sensitivity_threshold_dbm:
                hit = True
                false_alarm = False
            else:
                hit = False
                false_alarm = False

            return ReceiverMeasurement(
                band=target_band,
                hit=hit,
                false_alarm=false_alarm,
                true_signal_present=True,
                rx_power_dbm=total_rx_power_dbm,
                snr_db=snr_db,
                emitter_id=best_tx.emitter_id,
                threat_level=best_tx.threat_level,
                priority_weight=best_tx.priority_weight,
                switched_band=switched,
                pdw=best_tx.pdw if hit else None
            )

        else:
            # No signal present: noise-only measurement
            total_rx_power_dbm = noise_sample
            snr_db = 0.0

            # False alarm generated if noise fluctuation exceeds threshold
            # or with probability p_fa_nominal
            false_alarm = (total_rx_power_dbm >= self.sensitivity_threshold_dbm) or (self.rng.rand() < self.p_fa_nominal)
            hit = false_alarm

            return ReceiverMeasurement(
                band=target_band,
                hit=hit,
                false_alarm=false_alarm,
                true_signal_present=False,
                rx_power_dbm=total_rx_power_dbm,
                snr_db=snr_db,
                emitter_id=None,
                threat_level=0,
                priority_weight=0.0,
                switched_band=switched,
                pdw=None
            )
