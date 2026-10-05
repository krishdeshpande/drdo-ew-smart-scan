"""
Enhanced Async WebSocket & HTTP Server for Tactical Electronic Warfare Dashboard.
Streams high-fidelity simulation telemetry: 2D waterfall, 360-deg radar PPI scope,
real-time Figures of Merit, PDW decodes, and interactive scenario injection.
"""

import os
import sys
import json
import asyncio
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Dict, Any, Optional, List

# Ensure repository root is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from aiohttp import web
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

if not HAS_AIOHTTP and not HAS_WEBSOCKETS:
    print("ERROR: Neither 'aiohttp' nor 'websockets' is installed. Run: pip install aiohttp websockets")
    sys.exit(1)

from ew_simulator import (
    RFEnvironment,
    create_standard_ew_scenario,
    SpatialScanningRadar,
    FrequencyAgileEmitter,
    BurstCommunicationEmitter
)
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

PORT = int(os.environ.get("PORT", os.environ.get("EW_HTTP_PORT", "8080")))
WS_PORT = int(os.environ.get("EW_WS_PORT", "8765"))
HTTP_PORT = PORT

SCHEDULER_REGISTRY = {
    "dqn": lambda n: DQNScheduler(n),
    "ducb": lambda n: DiscountedUCBScheduler(n),
    "exp3": lambda n: Exp3Scheduler(n),
    "predictive": lambda n: PredictiveTemporalScheduler(n),
    "periodic": lambda n: PeriodicScanInterceptor(n),
    "sequential": lambda n: UniformSequentialScheduler(n),
    "random": lambda n: RandomSweepScheduler(n),
}


class EWSimulationServer:
    def __init__(self, num_bands: int = 8):
        self.num_bands = num_bands
        self.env = RFEnvironment(num_bands=num_bands, dt_sec=0.025)
        self.current_scheduler_key = "dqn"
        self.scheduler: BaseScheduler = SCHEDULER_REGISTRY[self.current_scheduler_key](num_bands)
        
        # Load trained weights if available
        weights_path = Path("models/dqn_weights.pt")
        if weights_path.exists() and hasattr(self.scheduler, "load_weights"):
            try:
                self.scheduler.load_weights(str(weights_path))
                print(f"[SERVER] Loaded pre-trained DQN weights from {weights_path}")
            except Exception as e:
                print(f"[SERVER] Note on loading weights: {e}")

        self.fom_tracker = FOMTracker(self.scheduler.name)
        self.is_running = True
        self.step_delay = 0.05
        self.clients = set()

    def set_scheduler(self, key: str):
        if key in SCHEDULER_REGISTRY:
            self.current_scheduler_key = key
            self.scheduler = SCHEDULER_REGISTRY[key](self.num_bands)
            if key == "dqn":
                weights_path = Path("models/dqn_weights.pt")
                if weights_path.exists() and hasattr(self.scheduler, "load_weights"):
                    self.scheduler.load_weights(str(weights_path))
            self.fom_tracker = FOMTracker(self.scheduler.name)
            print(f"[SERVER] Switched to scheduler: {self.scheduler.name}")

    def reset(self):
        self.env.reset()
        self.scheduler.reset()
        self.fom_tracker.reset()

    def inject_threat(self, threat_type: str):
        if threat_type == "agile_surge":
            new_emitter = FrequencyAgileEmitter(
                emitter_id=f"SURGE_AGILE_{len(self.env.emitters)+1}",
                name="Hostile Agile Jammer/Radar",
                bands=[0, 1, 3, 5],
                hop_dwell_steps=2,
                tx_power_dbm=60.0,
                threat_level=5
            )
            self.env.emitters.append(new_emitter)
            print(f"[SERVER] Injected high-threat agile emitter: {new_emitter.name}")
        elif threat_type == "drone_swarm":
            new_emitter = BurstCommunicationEmitter(
                emitter_id=f"SWARM_UAS_{len(self.env.emitters)+1}",
                name="Kamikaze Drone Telemetry Link",
                band=3 % self.num_bands,
                burst_rate=0.45,
                burst_duration_steps=4,
                tx_power_dbm=42.0,
                threat_level=4
            )
            self.env.emitters.append(new_emitter)
            print(f"[SERVER] Injected drone swarm comm link: {new_emitter.name}")

    async def broadcast(self, payload: Dict[str, Any]):
        if not self.clients:
            return
        msg = json.dumps(payload)
        coros = []
        for client in list(self.clients):
            if hasattr(client, "send_str"):
                coros.append(client.send_str(msg))
            else:
                coros.append(client.send(msg))
        await asyncio.gather(*coros, return_exceptions=True)

    async def handle_client_message(self, data: str):
        try:
            req = json.loads(data)
            cmd = req.get("command")
            if cmd == "set_scheduler":
                self.set_scheduler(req.get("scheduler", "dqn"))
            elif cmd == "set_speed":
                self.step_delay = float(req.get("delay", 0.05))
            elif cmd == "pause":
                self.is_running = False
            elif cmd == "resume":
                self.is_running = True
            elif cmd == "reset":
                self.reset()
            elif cmd == "inject_threat":
                self.inject_threat(req.get("threat_type", "agile_surge"))
        except Exception as e:
            print(f"[SERVER] Error handling client message: {e}")

    async def run_simulation_loop(self):
        obs = self.env.reset()
        while True:
            if self.is_running:
                action = self.scheduler.select_band(obs)
                res = self.env.step(action)
                next_obs = self.env.get_observation()

                self.scheduler.update(
                    action=action,
                    hit=res.measurement.hit,
                    snr=res.measurement.snr_db,
                    reward=res.reward,
                    next_obs=next_obs,
                    pdw=res.measurement.pdw
                )
                obs = next_obs

                self.fom_tracker.record_step(res, self.scheduler)
                fom = self.fom_tracker.compute()

                # Collect emitter details for PPI scope
                emitter_positions = []
                for tx in res.active_transmissions:
                    aoa = 0.0
                    if tx.pdw and "aoa_deg" in tx.pdw:
                        aoa = tx.pdw["aoa_deg"]
                    elif "SURV" in tx.emitter_id:
                        aoa = 30.0
                    elif "AGILE" in tx.emitter_id:
                        aoa = 145.0
                    elif "DRONE" in tx.emitter_id:
                        aoa = 260.0
                    else:
                        aoa = (tx.band * 45.0) % 360.0

                    emitter_positions.append({
                        "id": tx.emitter_id,
                        "type": tx.emitter_type,
                        "threat": tx.threat_level,
                        "band": tx.band,
                        "aoa_deg": aoa,
                        "is_mainlobe": tx.is_mainlobe,
                        "pwr_dbm": tx.tx_power_dbm
                    })

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
                    "active_emitters": emitter_positions,
                    "reward": round(res.reward, 2),
                    "cumulative_reward": fom.total_reward,
                    "scheduler_name": self.scheduler.name,
                    "scheduler_key": self.current_scheduler_key,
                    "pdw": res.measurement.pdw,
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


def run_unified_server(port: int):
    ui_dir = Path(__file__).parent.resolve()
    app = web.Application()

    async def index_handler(request):
        dashboard_path = ui_dir / "dashboard.html"
        return web.FileResponse(dashboard_path)

    async def health_handler(request):
        return web.json_response({
            "status": "online",
            "system": "DRDO SENTINEL-EW Tactical C2",
            "scheduler": sim_server.current_scheduler_key,
            "connected_clients": len(sim_server.clients)
        })

    async def aiohttp_ws_handler(request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        sim_server.clients.add(ws)
        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    await sim_server.handle_client_message(msg.data)
                elif msg.type == web.WSMsgType.ERROR:
                    break
        finally:
            sim_server.clients.discard(ws)
        return ws

    async def start_background_sim(app_instance):
        app_instance["sim_task"] = asyncio.create_task(sim_server.run_simulation_loop())

    async def cleanup_background_sim(app_instance):
        if "sim_task" in app_instance:
            app_instance["sim_task"].cancel()
            try:
                await app_instance["sim_task"]
            except asyncio.CancelledError:
                pass

    app.router.add_get("/", index_handler)
    app.router.add_get("/dashboard.html", index_handler)
    app.router.add_get("/health", health_handler)
    app.router.add_get("/ws", aiohttp_ws_handler)

    app.on_startup.append(start_background_sim)
    app.on_cleanup.append(cleanup_background_sim)

    print("=" * 65)
    print("  SENTINEL-EW // Cognitive Tactical Radar C2 System Online")
    print(f"  HTTP Dashboard : http://0.0.0.0:{port}/")
    print(f"  WebSocket Feed : ws://0.0.0.0:{port}/ws")
    print(f"  Health Check   : http://0.0.0.0:{port}/health")
    print("=" * 65)
    web.run_app(app, host="0.0.0.0", port=port, print=None)


def run_dual_port_server():
    threading.Thread(target=run_http_server, daemon=True).start()
    async def legacy_main():
        async with websockets.serve(ws_handler, "0.0.0.0", WS_PORT):
            print(f"[WEBSOCKET] Telemetry server listening on ws://localhost:{WS_PORT}")
            await sim_server.run_simulation_loop()
    try:
        asyncio.run(legacy_main())
    except KeyboardInterrupt:
        print("\n[SERVER] Stopped.")


def main():
    if HAS_AIOHTTP and not os.environ.get("EW_FORCE_DUAL_PORT"):
        run_unified_server(PORT)
    else:
        run_dual_port_server()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[SERVER] Stopped.")
