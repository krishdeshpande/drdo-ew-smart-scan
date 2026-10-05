"""
Synthetic Radar Emitter Dataset Generator and Parser.
Implements the Alan Turing Institute Synthetic Radar Dataset & JC Wise Radar Emitter Database schema:
Pulse Descriptor Words (PDWs): TOA, PW, PRI, RF (Carrier Frequency), Amplitude/SNR, AOA, Scan Type.
"""

import os
import csv
import json
import numpy as np
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional


@dataclass
class PulseDescriptorWord:
    pulse_id: int
    emitter_id: str
    emitter_type: str
    time_of_arrival_sec: float
    pulse_width_sec: float
    carrier_frequency_mhz: float
    frequency_band: int
    pulse_repetition_interval_sec: float
    amplitude_dbm: float
    snr_db: float
    angle_of_arrival_deg: float
    antenna_scan_type: str
    modulation: str


class TuringSyntheticRadarDataset:
    """
    Generator and Serializer for synthetic EW radar emitter pulses matching
    the Alan Turing Institute / JC Wise dataset benchmark specifications.
    """
    def __init__(self, num_bands: int = 8, base_freq_mhz: float = 2000.0, band_step_mhz: float = 100.0):
        self.num_bands = num_bands
        self.base_freq_mhz = base_freq_mhz
        self.band_step_mhz = band_step_mhz

    def band_to_frequency_mhz(self, band: int) -> float:
        return self.base_freq_mhz + band * self.band_step_mhz

    def frequency_to_band(self, freq_mhz: float) -> int:
        idx = int(round((freq_mhz - self.base_freq_mhz) / self.band_step_mhz))
        return max(0, min(self.num_bands - 1, idx))

    def generate_dataset(
        self,
        duration_sec: float = 10.0,
        seed: int = 42
    ) -> List[PulseDescriptorWord]:
        """
        Generates an interleaved pulse stream of diverse radar emitters:
        - 3D Surveillance Radar (Circular scan 3.0s, PRI 1ms, S-band)
        - Frequency-Agile Tracker (PRI 200us, hopping across 3 channels, X-band)
        - Drone Command Telemetry (Burst chirps, L-band)
        """
        rng = np.random.RandomState(seed)
        pdws: List[PulseDescriptorWord] = []
        pulse_id = 1

        # 1. Spatially Scanning Air Search Radar
        surv_scan_period = 3.0
        surv_pri = 1.2e-3
        surv_pw = 15e-6
        surv_band = 2 % self.num_bands
        surv_freq = self.band_to_frequency_mhz(surv_band)
        surv_beamwidth_deg = 3.5

        t = 0.0
        while t < duration_sec:
            antenna_angle = (360.0 * (t / surv_scan_period)) % 360.0
            # Receiver is at 0 degrees
            diff = min(antenna_angle, 360.0 - antenna_angle)
            if diff <= (surv_beamwidth_deg / 2.0):
                # In mainlobe
                power = rng.normal(-55.0, 1.5)
                snr = max(5.0, power - (-95.0))
                pdws.append(PulseDescriptorWord(
                    pulse_id=pulse_id,
                    emitter_id="RADAR_SURV_01",
                    emitter_type="SURVEILLANCE_3D",
                    time_of_arrival_sec=round(t, 7),
                    pulse_width_sec=surv_pw,
                    carrier_frequency_mhz=surv_freq,
                    frequency_band=surv_band,
                    pulse_repetition_interval_sec=surv_pri,
                    amplitude_dbm=round(power, 2),
                    snr_db=round(snr, 2),
                    angle_of_arrival_deg=0.0,
                    antenna_scan_type="CIRCULAR",
                    modulation="PULSED_LFM"
                ))
                pulse_id += 1
            t += surv_pri

        # 2. Agile Targeting Radar
        agile_pri = 0.5e-3
        agile_pw = 4e-6
        agile_bands = [4 % self.num_bands, 5 % self.num_bands, 6 % self.num_bands]
        t = 0.0
        cur_hop_idx = 0
        hop_counter = 0
        while t < duration_sec:
            if hop_counter % 20 == 0:
                cur_hop_idx = rng.randint(0, len(agile_bands))
            hop_counter += 1

            band = agile_bands[cur_hop_idx]
            freq = self.band_to_frequency_mhz(band)
            power = rng.normal(-60.0, 2.0)
            snr = max(5.0, power - (-95.0))
            pdws.append(PulseDescriptorWord(
                pulse_id=pulse_id,
                emitter_id="RADAR_AGILE_02",
                emitter_type="FIRE_CONTROL_AGILE",
                time_of_arrival_sec=round(t, 7),
                pulse_width_sec=agile_pw,
                carrier_frequency_mhz=freq,
                frequency_band=band,
                pulse_repetition_interval_sec=agile_pri,
                amplitude_dbm=round(power, 2),
                snr_db=round(snr, 2),
                angle_of_arrival_deg=45.0,
                antenna_scan_type="SECTOR_TRACK",
                modulation="FREQUENCY_HOPPED"
            ))
            pulse_id += 1
            t += agile_pri

        # 3. Intermittent Drone Uplink
        t = 0.1
        drone_pri = 2.0e-3
        drone_pw = 30e-6
        drone_band = 1 % self.num_bands
        drone_freq = self.band_to_frequency_mhz(drone_band)
        while t < duration_sec:
            # Burst pattern: 50 pulses burst, then silent for 0.4s
            for _ in range(30):
                power = rng.normal(-72.0, 3.0)
                snr = max(2.0, power - (-95.0))
                pdws.append(PulseDescriptorWord(
                    pulse_id=pulse_id,
                    emitter_id="DRONE_UPLINK_03",
                    emitter_type="UAS_DATALINK",
                    time_of_arrival_sec=round(t, 7),
                    pulse_width_sec=drone_pw,
                    carrier_frequency_mhz=drone_freq,
                    frequency_band=drone_band,
                    pulse_repetition_interval_sec=drone_pri,
                    amplitude_dbm=round(power, 2),
                    snr_db=round(snr, 2),
                    angle_of_arrival_deg=120.0,
                    antenna_scan_type="STATIONARY",
                    modulation="LORA_CHIRP"
                ))
                pulse_id += 1
                t += drone_pri
                if t >= duration_sec:
                    break
            t += rng.uniform(0.3, 0.7)

        # Sort interleaved stream by Time of Arrival (TOA)
        pdws.sort(key=lambda p: p.time_of_arrival_sec)
        # Re-number pulse IDs sequentially
        for i, p in enumerate(pdws, 1):
            p.pulse_id = i

        return pdws

    def export_csv(self, pdws: List[PulseDescriptorWord], filepath: str):
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        if not pdws:
            return
        fieldnames = list(asdict(pdws[0]).keys())
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for p in pdws:
                writer.writerow(asdict(p))

    def export_json(self, pdws: List[PulseDescriptorWord], filepath: str):
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        data = [asdict(p) for p in pdws]
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_csv(self, filepath: str) -> List[PulseDescriptorWord]:
        pdws = []
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                pdws.append(PulseDescriptorWord(
                    pulse_id=int(row["pulse_id"]),
                    emitter_id=row["emitter_id"],
                    emitter_type=row["emitter_type"],
                    time_of_arrival_sec=float(row["time_of_arrival_sec"]),
                    pulse_width_sec=float(row["pulse_width_sec"]),
                    carrier_frequency_mhz=float(row["carrier_frequency_mhz"]),
                    frequency_band=int(row["frequency_band"]),
                    pulse_repetition_interval_sec=float(row["pulse_repetition_interval_sec"]),
                    amplitude_dbm=float(row["amplitude_dbm"]),
                    snr_db=float(row["snr_db"]),
                    angle_of_arrival_deg=float(row["angle_of_arrival_deg"]),
                    antenna_scan_type=row["antenna_scan_type"],
                    modulation=row["modulation"]
                ))
        return pdws
