"""
RF Emitter Models for Electronic Warfare Simulation.
Includes Spatially Scanning Radars, Frequency Agile Hoppers, and Burst Transmitters.
"""

import math
import numpy as np
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class EmitterTransmission:
    emitter_id: str
    emitter_type: str
    threat_level: int       # 1 (lowest) to 5 (critical hostile)
    priority_weight: float  # Multiplier for reward on intercept
    band: int               # Frequency channel index (0 .. N-1)
    tx_power_dbm: float     # Radiated power toward receiver
    is_mainlobe: bool       # True if receiver is illuminated by mainlobe
    pdw: Dict[str, Any]     # Pulse Descriptor Word (TOA, PW, PRI, RF, AOA, etc.)


class BaseEmitter:
    def __init__(self, emitter_id: str, name: str, emitter_type: str, threat_level: int = 1):
        self.emitter_id = emitter_id
        self.name = name
        self.emitter_type = emitter_type
        self.threat_level = threat_level
        self.priority_weight = float(threat_level)

    def step(self, t: float, dt: float, receiver_azimuth_deg: float = 0.0) -> Optional[EmitterTransmission]:
        raise NotImplementedError


class SpatialScanningRadar(BaseEmitter):
    """
    Rotating beam surveillance/targeting radar.
    Mainlobe sweeps past the receiver once per scan period T_scan.
    Can be single-frequency or frequency agile.
    """
    def __init__(
        self,
        emitter_id: str,
        name: str,
        bands: List[int],
        scan_period_sec: float = 4.0,
        beamwidth_deg: float = 3.5,
        peak_gain_dbi: float = 34.0,
        sidelobe_gain_dbi: float = -5.0,
        tx_power_dbm: float = 65.0,
        pri_sec: float = 1e-3,
        pw_sec: float = 10e-6,
        initial_phase_deg: float = 0.0,
        threat_level: int = 4,
        frequency_agility: bool = False
    ):
        super().__init__(emitter_id, name, "SPATIAL_SCAN_RADAR", threat_level)
        self.bands = bands
        self.scan_period_sec = scan_period_sec
        self.beamwidth_deg = beamwidth_deg
        self.peak_gain_dbi = peak_gain_dbi
        self.sidelobe_gain_dbi = sidelobe_gain_dbi
        self.tx_power_dbm = tx_power_dbm
        self.pri_sec = pri_sec
        self.pw_sec = pw_sec
        self.initial_phase_deg = initial_phase_deg % 360.0
        self.current_angle_deg = self.initial_phase_deg
        self.frequency_agility = frequency_agility
        self._band_idx = 0
        self._hop_step = 0

    def step(self, t: float, dt: float, receiver_azimuth_deg: float = 0.0) -> Optional[EmitterTransmission]:
        scan_rate_deg_per_sec = 360.0 / self.scan_period_sec
        self.current_angle_deg = (self.initial_phase_deg + scan_rate_deg_per_sec * t) % 360.0

        diff = abs(self.current_angle_deg - receiver_azimuth_deg)
        diff = min(diff, 360.0 - diff)

        is_mainlobe = diff <= (self.beamwidth_deg / 2.0)
        if diff <= (self.beamwidth_deg * 1.5):
            loss = 12.0 * ((diff / self.beamwidth_deg) ** 2)
            antenna_gain = max(self.sidelobe_gain_dbi, self.peak_gain_dbi - loss)
        else:
            antenna_gain = self.sidelobe_gain_dbi

        if self.frequency_agility:
            self._hop_step += 1
            if self._hop_step % 5 == 0:
                self._band_idx = (self._band_idx + 1) % len(self.bands)
            active_band = self.bands[self._band_idx]
        else:
            active_band = self.bands[0]

        effective_tx_power = self.tx_power_dbm + antenna_gain

        pdw = {
            "toa_sec": t,
            "pw_sec": self.pw_sec,
            "pri_sec": self.pri_sec,
            "carrier_band": active_band,
            "aoa_deg": (receiver_azimuth_deg + 180.0) % 360.0,
            "tx_power_dbm": effective_tx_power,
            "is_mainlobe": is_mainlobe,
            "scan_period_sec": self.scan_period_sec
        }

        return EmitterTransmission(
            emitter_id=self.emitter_id,
            emitter_type=self.emitter_type,
            threat_level=self.threat_level,
            priority_weight=self.priority_weight,
            band=active_band,
            tx_power_dbm=effective_tx_power,
            is_mainlobe=is_mainlobe,
            pdw=pdw
        )


class FrequencyAgileEmitter(BaseEmitter):
    """
    Frequency-Hopping / Agile emitter (e.g. Modern Tactical Radar or Jam-Resistant Comms).
    Changes channel every hop_dwell_steps.
    """
    def __init__(
        self,
        emitter_id: str,
        name: str,
        bands: List[int],
        hop_dwell_steps: int = 3,
        tx_power_dbm: float = 50.0,
        pattern: str = "pseudorandom",
        threat_level: int = 5,
        duty_cycle: float = 0.9
    ):
        super().__init__(emitter_id, name, "FREQUENCY_AGILE", threat_level)
        self.bands = bands
        self.hop_dwell_steps = hop_dwell_steps
        self.tx_power_dbm = tx_power_dbm
        self.pattern = pattern
        self.duty_cycle = duty_cycle
        self.current_step = 0
        self.current_band_idx = 0
        self.rng = np.random.RandomState(seed=abs(hash(emitter_id)) % (2**31 - 1))

    def step(self, t: float, dt: float, receiver_azimuth_deg: float = 0.0) -> Optional[EmitterTransmission]:
        if self.current_step % self.hop_dwell_steps == 0:
            if self.pattern == "pseudorandom":
                self.current_band_idx = self.rng.randint(0, len(self.bands))
            elif self.pattern == "cyclic":
                self.current_band_idx = (self.current_band_idx + 1) % len(self.bands)
            elif self.pattern == "adaptive":
                weights = np.ones(len(self.bands))
                weights[len(self.bands)//2] += 1.5
                weights = weights / weights.sum()
                self.current_band_idx = self.rng.choice(len(self.bands), p=weights)

        self.current_step += 1

        if self.rng.rand() > self.duty_cycle:
            return None

        active_band = self.bands[self.current_band_idx]
        pdw = {
            "toa_sec": t,
            "pw_sec": 5e-6,
            "pri_sec": 500e-6,
            "carrier_band": active_band,
            "aoa_deg": 45.0,
            "tx_power_dbm": self.tx_power_dbm,
            "is_mainlobe": True,
            "hop_dwell_steps": self.hop_dwell_steps
        }

        return EmitterTransmission(
            emitter_id=self.emitter_id,
            emitter_type=self.emitter_type,
            threat_level=self.threat_level,
            priority_weight=self.priority_weight,
            band=active_band,
            tx_power_dbm=self.tx_power_dbm,
            is_mainlobe=True,
            pdw=pdw
        )


class BurstCommunicationEmitter(BaseEmitter):
    """
    Burst / sporadic transmission (e.g. Drone command uplink / telemetry).
    """
    def __init__(
        self,
        emitter_id: str,
        name: str,
        band: int,
        burst_rate: float = 0.20,
        burst_duration_steps: int = 3,
        tx_power_dbm: float = 40.0,
        threat_level: int = 3
    ):
        super().__init__(emitter_id, name, "BURST_COMM", threat_level)
        self.band = band
        self.burst_rate = burst_rate
        self.burst_duration_steps = burst_duration_steps
        self.tx_power_dbm = tx_power_dbm
        self.active_remaining_steps = 0
        self.rng = np.random.RandomState(seed=abs(hash(emitter_id)) % (2**31 - 1))

    def step(self, t: float, dt: float, receiver_azimuth_deg: float = 0.0) -> Optional[EmitterTransmission]:
        if self.active_remaining_steps > 0:
            self.active_remaining_steps -= 1
            is_transmitting = True
        else:
            if self.rng.rand() < self.burst_rate:
                self.active_remaining_steps = self.burst_duration_steps - 1
                is_transmitting = True
            else:
                is_transmitting = False

        if not is_transmitting:
            return None

        pdw = {
            "toa_sec": t,
            "pw_sec": 20e-6,
            "pri_sec": 2e-3,
            "carrier_band": self.band,
            "aoa_deg": 120.0,
            "tx_power_dbm": self.tx_power_dbm,
            "is_mainlobe": True
        }

        return EmitterTransmission(
            emitter_id=self.emitter_id,
            emitter_type=self.emitter_type,
            threat_level=self.threat_level,
            priority_weight=self.priority_weight,
            band=self.band,
            tx_power_dbm=self.tx_power_dbm,
            is_mainlobe=True,
            pdw=pdw
        )


def create_standard_ew_scenario(num_bands: int = 8) -> List[BaseEmitter]:
    """
    Standard DRDO-representative EW scenario with mixed emitter threats:
    - E1: High-Threat Rotating Surveillance Radar (Scan period 3.0s, Band 2)
    - E2: Critical-Threat Frequency-Agile Fire-Control Radar (Hopping between Bands 4, 5, 6)
    - E3: Medium-Threat Drone Control Uplink (Sporadic bursts in Band 1)
    - E4: Medium-Threat Surface Nav Radar (Scan period 1.5s, Band 7)
    """
    emitters = [
        SpatialScanningRadar(
            emitter_id="RADAR_SURV_01",
            name="Air Search Radar 3D",
            bands=[2 % num_bands],
            scan_period_sec=3.0,
            beamwidth_deg=4.0,
            peak_gain_dbi=32.0,
            sidelobe_gain_dbi=-10.0,
            tx_power_dbm=60.0,
            threat_level=4
        ),
        FrequencyAgileEmitter(
            emitter_id="RADAR_AGILE_02",
            name="Frequency-Agile Tracker",
            bands=[4 % num_bands, 5 % num_bands, 6 % num_bands],
            hop_dwell_steps=4,
            tx_power_dbm=55.0,
            pattern="pseudorandom",
            threat_level=5
        ),
        BurstCommunicationEmitter(
            emitter_id="DRONE_UPLINK_03",
            name="UAS Command Link (ELRS-type)",
            band=1 % num_bands,
            burst_rate=0.20,
            burst_duration_steps=3,
            tx_power_dbm=38.0,
            threat_level=3
        ),
        SpatialScanningRadar(
            emitter_id="RADAR_NAV_04",
            name="Coastal / Surface Nav Radar",
            bands=[(num_bands - 1) % num_bands],
            scan_period_sec=1.5,
            beamwidth_deg=3.0,
            peak_gain_dbi=28.0,
            sidelobe_gain_dbi=-12.0,
            tx_power_dbm=50.0,
            threat_level=2
        )
    ]
    return emitters
