"""
Unit and Integration Test Suite for DRDO Electronic Warfare Smart Scan System.
"""

import unittest
import numpy as np
import tempfile
import os
import shutil

from ew_simulator import (
    SpatialScanningRadar,
    FrequencyAgileEmitter,
    BurstCommunicationEmitter,
    ESReceiver,
    RFEnvironment,
    create_standard_ew_scenario
)
from schedulers import (
    UniformSequentialScheduler,
    RandomSweepScheduler,
    StaticPriorityScheduler,
    DiscountedUCBScheduler,
    Exp3Scheduler,
    DQNScheduler,
    PredictiveTemporalScheduler,
    PeriodicScanInterceptor
)
from metrics import FOMTracker
from dataset import TuringSyntheticRadarDataset


class TestEWSystem(unittest.TestCase):
    def setUp(self):
        self.num_bands = 8
        self.env = RFEnvironment(num_bands=self.num_bands, dt_sec=0.025, seed=42)

    def test_spatial_scanning_radar(self):
        radar = SpatialScanningRadar(
            emitter_id="TEST_RADAR",
            name="Test Radar",
            bands=[2],
            scan_period_sec=2.0,
            beamwidth_deg=4.0,
            peak_gain_dbi=30.0,
            sidelobe_gain_dbi=-10.0,
            tx_power_dbm=60.0,
            initial_phase_deg=0.0
        )
        # At t=0, pointing at 0 deg -> mainlobe to receiver at 0 deg
        tx = radar.step(t=0.0, dt=0.025, receiver_azimuth_deg=0.0)
        self.assertIsNotNone(tx)
        self.assertTrue(tx.is_mainlobe)
        self.assertEqual(tx.band, 2)
        self.assertGreater(tx.tx_power_dbm, 80.0)

        # Advance 1.0s (half period) -> pointing at 180 deg -> sidelobe
        tx_side = radar.step(t=1.0, dt=0.025, receiver_azimuth_deg=0.0)
        self.assertIsNotNone(tx_side)
        self.assertFalse(tx_side.is_mainlobe)
        self.assertLess(tx_side.tx_power_dbm, 60.0)

    def test_frequency_agile_emitter(self):
        agile = FrequencyAgileEmitter(
            emitter_id="TEST_AGILE",
            name="Test Agile",
            bands=[1, 3, 5],
            hop_dwell_steps=2
        )
        visited_bands = set()
        for s in range(20):
            tx = agile.step(t=s*0.025, dt=0.025)
            if tx is not None:
                visited_bands.add(tx.band)
        # Verify it hops across specified bands
        for b in visited_bands:
            self.assertIn(b, [1, 3, 5])

    def test_receiver_measurement(self):
        rx = ESReceiver(num_bands=8, sensitivity_threshold_dbm=-85.0, noise_floor_dbm=-95.0)
        radar = SpatialScanningRadar("R1", "R1", bands=[3], tx_power_dbm=70.0, peak_gain_dbi=30.0)
        tx = radar.step(0.0, 0.025, 0.0)

        # Dwell on tuned band
        meas_hit = rx.tune_and_measure(target_band=3, transmissions=[tx])
        self.assertTrue(meas_hit.hit)
        self.assertTrue(meas_hit.true_signal_present)
        self.assertEqual(meas_hit.band, 3)

        # Dwell on empty band
        meas_miss = rx.tune_and_measure(target_band=0, transmissions=[tx])
        self.assertFalse(meas_miss.true_signal_present)
        self.assertEqual(meas_miss.band, 0)

    def test_environment_step(self):
        obs = self.env.reset()
        self.assertEqual(len(obs), 3 * self.num_bands)

        res = self.env.step(action_band=2)
        self.assertIsNotNone(res)
        self.assertEqual(res.step_idx, 1)
        self.assertEqual(len(res.all_bands_status), self.num_bands)

    def test_all_schedulers_run(self):
        scheds = [
            UniformSequentialScheduler(self.num_bands),
            RandomSweepScheduler(self.num_bands),
            StaticPriorityScheduler(self.num_bands),
            DiscountedUCBScheduler(self.num_bands),
            Exp3Scheduler(self.num_bands),
            DQNScheduler(self.num_bands),
            PredictiveTemporalScheduler(self.num_bands),
            PeriodicScanInterceptor(self.num_bands)
        ]

        for s in scheds:
            obs = self.env.reset()
            s.reset()
            for _ in range(15):
                action = s.select_band(obs)
                self.assertTrue(0 <= action < self.num_bands)
                res = self.env.step(action)
                next_obs = self.env.get_observation()
                s.update(action, res.measurement.hit, res.measurement.snr_db, res.reward, next_obs, res.measurement.pdw)
                obs = next_obs

    def test_fom_tracker(self):
        tracker = FOMTracker("Test Tracker")
        obs = self.env.reset()
        for _ in range(50):
            res = self.env.step(2)
            tracker.record_step(res, None)
        fom = tracker.compute()
        self.assertEqual(fom.total_dwells, 50)
        self.assertTrue(0.0 <= fom.probability_of_detection_pd <= 1.0)
        self.assertTrue(0.0 <= fom.probability_of_false_alarm_pfa <= 1.0)

    def test_turing_dataset_export_and_load(self):
        temp_dir = tempfile.mkdtemp()
        try:
            ds = TuringSyntheticRadarDataset(num_bands=self.num_bands)
            pdws = ds.generate_dataset(duration_sec=1.0)
            self.assertGreater(len(pdws), 0)

            csv_file = os.path.join(temp_dir, "test_pdws.csv")
            ds.export_csv(pdws, csv_file)
            self.assertTrue(os.path.exists(csv_file))

            loaded = ds.load_csv(csv_file)
            self.assertEqual(len(loaded), len(pdws))
            self.assertEqual(loaded[0].emitter_id, pdws[0].emitter_id)
        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    unittest.main()
