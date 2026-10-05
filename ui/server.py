"""
Async WebSocket & HTTP Server for Real-Time Tactical Electronic Warfare Dashboard.
Streams simulation telemetry, spectrum waterfall frames, and DRDO figures of merit.
"""

import os
import sys
import json
import asyncio
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import websockets
except ImportError:
    print("ERROR: websockets not installed. Run: pip install websockets")
    sys.exit(1)

from ew_simulator import RFEnvironment, create_standard_ew_scenario
from schedulers import (
    BaseScheduler,
    UniformSequentialScheduler,
    RandomSweepScheduler,
    DiscountedUCBScheduler,
    Exp3Scheduler,
    DQNScheduler,
    PredictiveTemporalScheduler,
    PeriodicScanInterceptor
)
from metrics import FOMTracker

WS_PORT = int(os.environ.get("EW_WS_PORT", "8765"))
HTTP_PORT = int(os.environ.get("EW_HTTP_PORT", "8080"))

SCHEDULER_REGISTRY = {
    "sequential": lambda n: UniformSequentialScheduler(n),
    "random": lambda n: RandomSweepScheduler(n),
    "ducb": lambda n: DiscountedUCBScheduler(n),
    "exp3": lambda n: Exp3Scheduler(n),
    "dqn": lambda n: DQNScheduler(n),
    "predictive": lambda n: PredictiveTemporalScheduler(n),
    "periodic": lambda n: PeriodicScanInterceptor(n),
}


class EWSimulationServer:
    def __init__(self, num_bands: int = 8):
        self.num_bands = num_bands
        self.env = RFEnvironment(num_bands=num_bands, dt_sec=0.025)
        self.current_scheduler_key = "ducb"
        self.scheduler: BaseScheduler = SCHEDULER_REGISTRY[self.current_scheduler_key](num_bands)
        self.fom_tracker = FOMTracker(self.scheduler.name)
        self.is_running = True
        self.step_delay = 0.06  # seconds per step for visual smoothness
        self.clients = set()
        self.lock = asyncio.Lock()

    def set_scheduler(self, key: str):
        if key in SCHEDULER_REGISTRY:
            self.current_scheduler_key = key
            self.scheduler = SCHEDULER_REGISTRY[key](self.num_bands)
            self.fom_tracker = FOMTracker(self.scheduler.name)
            print(f"[SERVER] Switched to scheduler: {self.scheduler.name}")

    def reset(self):
        self.env.reset()
        self.scheduler.reset()
        self.fom_tracker.reset()

    async def broadcast(self, payload: Dict[str, Any]):
        if not self.clients:
            return
        msg = json.dumps(payload)
        await asyncio.gather(
            *[client.send(msg) for client in list(self.clients)],
            return_exceptions=True
        )

    async def handle_client_message(self, data: str):
        try:
            req = json.loads(data)
            cmd = req.get("command")
            if cmd == "set_scheduler":
                self.set_scheduler(req.get("scheduler", "ducb"))
            elif cmd == "set_speed":
                self.step_delay = float(req.get("delay", 0.06))
            elif cmd == "pause":
                self.is_running = False
            elif cmd == "resume":
                self.is_running = True
            elif cmd == "reset":
                self.reset()
        except Exception as e:
            print(f"[SERVER] Error handling client message: {e}")

    async def run_simulation_loop(self):
        obs = self.env.reset()
        while True:
            if self.is_running:
                # 1. Scheduler selects target band
                action = self.scheduler.select_band(obs)

                # 2. Step environment
                res = self.env.step(action)
                next_obs = self.env.get_observation()

                # 3. Update scheduler
                self.scheduler.update(
                    action=action,
                    hit=res.measurement.hit,
                    snr=res.measurement.snr_db,
                    reward=res.reward,
                    next_obs=next_obs,
                    pdw=res.measurement.pdw
                )
                obs = next_obs

                # 4. Record Figures of Merit
                self.fom_tracker.record_step(res, self.scheduler)
                fom = self.fom_tracker.compute()

                # 5. Build telemetry packet
                packet = {
                    "step": res.step_idx,
                    "time_sec": round(res.time_sec, 3),
                    "action_band": action,
                    "hit": res.measurement.hit,
                    "false_alarm": res.measurement.false_alarm,
                    "rx_power_dbm": round(res.measurement.rx_power_dbm, 1),
                    "snr_db": round(res.measurement.snr_db, 1),
                    "emitter_id": res.measurement.emitter_id,
                    "threat_level": res.measurement.threat_level,
                    "ground_truth_bands": res.ground_truth_active_bands,
                    "all_bands_powers": [round(float(p), 1) for p in res.all_bands_powers],
                    "reward": round(res.reward, 2),
                    "cumulative_reward": fom.total_reward,
                    "scheduler_name": self.scheduler.name,
                    "scheduler_key": self.current_scheduler_key,
                    "fom": {
                        "pd_pct": round(fom.probability_of_detection_pd * 100.0, 1),
                        "pfa": round(fom.probability_of_false_alarm_pfa, 4),
                        "intercept_rate": fom.avg_intercept_rate_per_sec,
                        "total_hits": fom.total_hits,
                        "pred_accuracy_pct": fom.percentage_correct_predictions,
                        "time_error_ms": fom.avg_intercept_time_error_ms,
                        "emitter_ratios": fom.interception_ratio_by_type
                    }
                }

                await self.broadcast(packet)

            await asyncio.sleep(self.step_delay)


sim_server = EWSimulationServer()

async def ws_handler(websocket):
    sim_server.clients.add(websocket)
    try:
        async for message in websocket:
            await sim_server.handle_client_message(message)
    finally:
        sim_server.clients.discard(websocket)


def run_http_server():
    ui_dir = Path(__file__).parent.resolve()
    os.chdir(str(ui_dir))
    handler = SimpleHTTPRequestHandler
    handler.log_message = lambda *a: None
    httpd = HTTPServer(("0.0.0.0", HTTP_PORT), handler)
    print(f"[HTTP] Tactical EW Dashboard running at: http://localhost:{HTTP_PORT}/dashboard.html")
    httpd.serve_forever()


async def main():
    threading.Thread(target=run_http_server, daemon=True).start()
    async with websockets.serve(ws_handler, "0.0.0.0", WS_PORT):
        print(f"[WEBSOCKET] Telemetry server listening on ws://localhost:{WS_PORT}")
        await sim_server.run_simulation_loop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[SERVER] Stopped.")
