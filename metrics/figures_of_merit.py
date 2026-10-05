"""
Figures of Merit (FOM) Engine for Electronic Warfare Electronic Support Receiver.
Implements official DRDO performance evaluation criteria:
- Probability of Detection (Pd)
- Probability of False Alarm (Pfa)
- Receiver Sensitivity (MDS)
- Average Intercept Rate
- Average Reward / Cost Function
- Percentage of Correct Predictions
- Average Intercept Time Error
- Time to First Intercept (TTFI)
- Interception Ratio across Spatial Scanning and Agile Emitters
"""

import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
import numpy as np


@dataclass
class FiguresOfMerit:
    scheduler_name: str
    total_dwells: int
    total_simulation_time_sec: float
    total_hits: int
    total_false_alarms: int
    dwell_switches: int
    total_reward: float
    avg_reward_per_dwell: float
    avg_intercept_rate_per_sec: float
    probability_of_detection_pd: float
    probability_of_false_alarm_pfa: float
    receiver_sensitivity_dbm: float
    percentage_correct_predictions: float
    avg_intercept_time_error_ms: float
    time_to_first_intercept_sec: Dict[str, Optional[float]]
    interception_ratio_by_emitter: Dict[str, float]
    interception_ratio_by_type: Dict[str, float]


class FOMTracker:
    """
    Online tracker that ingests each simulation step and computes comprehensive
    Electronic Warfare figures of merit.
    """
    def __init__(self, scheduler_name: str, sensitivity_threshold_dbm: float = -85.0):
        self.scheduler_name = scheduler_name
        self.sensitivity_threshold_dbm = sensitivity_threshold_dbm
        self.reset()

    def reset(self):
        self.total_dwells = 0
        self.total_sim_time_sec = 0.0
        self.total_hits = 0
        self.total_false_alarms = 0
        self.total_switches = 0
        self.cumulative_reward = 0.0

        # Detection statistics
        self.signal_present_count = 0
        self.signal_detected_count = 0
        self.noise_only_count = 0

        # Emitter specific tracking
        self.emitter_opportunities: Dict[str, int] = {}
        self.emitter_intercepts: Dict[str, int] = {}
        self.emitter_types: Dict[str, str] = {}
        self.first_intercept_time: Dict[str, Optional[float]] = {}

        # Predictive tracking
        self.predictions_made = 0
        self.correct_predictions = 0
        self.time_errors_sec: List[float] = []

    def record_step(self, step_res, scheduler):
        self.total_dwells += 1
        self.total_sim_time_sec = step_res.time_sec
        self.cumulative_reward += step_res.reward

        meas = step_res.measurement
        if meas.switched_band:
            self.total_switches += 1

        # Track ground truth opportunities across all emitters
        for tx in step_res.active_transmissions:
            eid = tx.emitter_id
            self.emitter_opportunities[eid] = self.emitter_opportunities.get(eid, 0) + 1
            self.emitter_types[eid] = tx.emitter_type
            if eid not in self.first_intercept_time:
                self.first_intercept_time[eid] = None

        # Track hit / false alarm
        if meas.true_signal_present:
            self.signal_present_count += 1
            if meas.hit and not meas.false_alarm:
                self.signal_detected_count += 1
                self.total_hits += 1
                if meas.emitter_id:
                    eid = meas.emitter_id
                    self.emitter_intercepts[eid] = self.emitter_intercepts.get(eid, 0) + 1
                    if self.first_intercept_time.get(eid) is None:
                        self.first_intercept_time[eid] = step_res.time_sec
        else:
            self.noise_only_count += 1
            if meas.false_alarm:
                self.total_false_alarms += 1

        # Query predictive metrics if scheduler supports them
        if hasattr(scheduler, "total_predictions_made"):
            self.predictions_made = scheduler.total_predictions_made
            self.correct_predictions = scheduler.correct_predictions
            self.time_errors_sec = list(scheduler.time_errors)

    def compute(self) -> FiguresOfMerit:
        # Probability of Detection (Pd)
        pd = (self.signal_detected_count / self.signal_present_count) if self.signal_present_count > 0 else 0.0

        # Probability of False Alarm (Pfa)
        pfa = (self.total_false_alarms / self.noise_only_count) if self.noise_only_count > 0 else 0.0

        # Average Intercept Rate (intercepts per second)
        dur = max(0.001, self.total_sim_time_sec)
        intercept_rate = self.total_hits / dur

        # Average Reward
        avg_reward = (self.cumulative_reward / self.total_dwells) if self.total_dwells > 0 else 0.0

        # Predictive accuracy
        pred_acc = (self.correct_predictions / self.predictions_made * 100.0) if self.predictions_made > 0 else 0.0

        # Average Intercept Time Error in milliseconds
        avg_time_error_ms = (float(np.mean(self.time_errors_sec)) * 1000.0) if self.time_errors_sec else 0.0

        # Interception ratio per emitter (hits / opportunities)
        ratio_per_emitter = {}
        for eid, opps in self.emitter_opportunities.items():
            hits = self.emitter_intercepts.get(eid, 0)
            ratio_per_emitter[eid] = (hits / opps) if opps > 0 else 0.0

        # Interception ratio per emitter type (Spatial Scan vs Agile vs Comm)
        type_opps: Dict[str, int] = {}
        type_hits: Dict[str, int] = {}
        for eid, opps in self.emitter_opportunities.items():
            etype = self.emitter_types.get(eid, "UNKNOWN")
            type_opps[etype] = type_opps.get(etype, 0) + opps
            type_hits[etype] = type_hits.get(etype, 0) + self.emitter_intercepts.get(eid, 0)

        ratio_per_type = {}
        for etype, opps in type_opps.items():
            hits = type_hits.get(etype, 0)
            ratio_per_type[etype] = (hits / opps) if opps > 0 else 0.0

        return FiguresOfMerit(
            scheduler_name=self.scheduler_name,
            total_dwells=self.total_dwells,
            total_simulation_time_sec=round(self.total_sim_time_sec, 3),
            total_hits=self.total_hits,
            total_false_alarms=self.total_false_alarms,
            dwell_switches=self.total_switches,
            total_reward=round(self.cumulative_reward, 2),
            avg_reward_per_dwell=round(avg_reward, 3),
            avg_intercept_rate_per_sec=round(intercept_rate, 2),
            probability_of_detection_pd=round(pd, 4),
            probability_of_false_alarm_pfa=round(pfa, 4),
            receiver_sensitivity_dbm=self.sensitivity_threshold_dbm,
            percentage_correct_predictions=round(pred_acc, 2),
            avg_intercept_time_error_ms=round(avg_time_error_ms, 2),
            time_to_first_intercept_sec={k: (round(v, 3) if v is not None else None) for k, v in self.first_intercept_time.items()},
            interception_ratio_by_emitter={k: round(v, 4) for k, v in ratio_per_emitter.items()},
            interception_ratio_by_type={k: round(v, 4) for k, v in ratio_per_type.items()}
        )


def format_fom_markdown_table(foms: List[FiguresOfMerit]) -> str:
    """Formats comparison of multiple schedulers as a Markdown table."""
    headers = [
        "Strategy / Scheduler",
        "Pd (%)",
        "Pfa",
        "Intercept Rate (/s)",
        "Mean Reward",
        "TTFI Surv Radar (s)",
        "Agile Intercept Ratio",
        "Time Error (ms)"
    ]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]

    for f in foms:
        surv_ttfi = f.time_to_first_intercept_sec.get("RADAR_SURV_01", "N/A")
        agile_ratio = f.interception_ratio_by_type.get("FREQUENCY_AGILE", 0.0) * 100.0
        time_err = f"{f.avg_intercept_time_error_ms:.1f}" if f.avg_intercept_time_error_ms > 0 else "N/A"

        row = [
            f.scheduler_name,
            f"{f.probability_of_detection_pd * 100.0:.1f}%",
            f"{f.probability_of_false_alarm_pfa:.4f}",
            f"{f.avg_intercept_rate_per_sec:.1f}",
            f"{f.avg_reward_per_dwell:+.2f}",
            f"{surv_ttfi}",
            f"{agile_ratio:.1f}%",
            time_err
        ]
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)
