import os
import sys
import time
import subprocess
from pathlib import Path

BASE_DIR = Path(r"C:\Users\krish\.gemini\antigravity\scratch\drdo_ew_smart_scan")
DIAG_DIR = BASE_DIR / "diagram_generator"
DIAG_DIR.mkdir(exist_ok=True)

BROWSER = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not Path(BROWSER).exists():
    BROWSER = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

def render_edge(html_path, out_png_path, width, height):
    html_abs = Path(html_path).resolve()
    out_abs = Path(out_png_path).resolve()
    cmd = [
        BROWSER,
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--window-size={width},{height}",
        f"--screenshot={out_abs}",
        html_abs.as_uri()
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    time.sleep(0.8)
    if out_abs.exists():
        print(f"[OK] Rendered {out_abs.name} ({out_abs.stat().st_size} bytes)")
    else:
        print(f"[ERROR] Failed to render {out_abs.name}: {res.stderr}")

# ==========================================
# 1. Slide 2: Workflow Diagram
# ==========================================
def make_s2_workflow():
    html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
  body { width: 1972px; height: 1150px; background: #ffffff; padding: 20px; }
  .box { width: 100%; height: 100%; border: 3px solid #1e293b; border-radius: 28px; background: #ffffff; padding: 24px 36px; display: flex; flex-direction: column; justify-content: space-between; position: relative; }
  .title { font-family: 'Georgia', serif; font-size: 44px; font-weight: bold; text-align: center; color: #0f172a; }
  .subtitle { font-size: 25px; font-weight: 500; text-align: center; color: #334155; margin-top: 4px; }
  .alert { position: absolute; right: 28px; top: 16px; background: #f3e8ff; border: 2px dashed #9333ea; border-radius: 16px; padding: 10px 18px; font-size: 16px; color: #581c87; font-weight: 600; display: flex; align-items: center; gap: 10px; }
  .top-flow { display: flex; align-items: center; justify-content: space-between; margin-top: 10px; }
  .badge-pink { background: #fce7f3; border: 2.5px solid #db2777; border-radius: 40px; padding: 12px 30px; font-size: 26px; font-weight: bold; color: #9d174d; display: flex; align-items: center; gap: 10px; }
  .badge-purple { background: #e0e7ff; border: 1.5px solid #6366f1; color: #4338ca; font-size: 18px; font-weight: 700; padding: 4px 16px; border-radius: 14px; margin-bottom: 8px; display: inline-block; }
  .yellow-card { background: #fef9c3; border: 2.5px solid #1e293b; border-radius: 18px; padding: 12px 18px; display: flex; align-items: flex-start; gap: 14px; box-shadow: 0 4px 10px rgba(0,0,0,0.04); }
  .yellow-card h4 { font-size: 20px; color: #0f172a; font-weight: 700; margin-bottom: 3px; }
  .yellow-card p { font-size: 15px; color: #334155; line-height: 1.35; }
  .engine-card { width: 380px; background: #fef9c3; border: 2.5px solid #1e293b; border-radius: 22px; padding: 22px; text-align: left; }
  .engine-card h3 { font-size: 22px; color: #0f172a; font-weight: 700; text-align: center; margin-bottom: 12px; }
  .engine-card ul { list-style: disc; margin-left: 22px; font-size: 17px; color: #334155; line-height: 1.5; }
  .diamond { width: 210px; height: 210px; background: #0284c7; transform: rotate(45deg); display: flex; align-items: center; justify-content: center; box-shadow: 0 6px 18px rgba(2,132,199,0.25); margin: 0 35px; }
  .diamond-in { transform: rotate(-45deg); text-align: center; color: #fff; padding: 8px; }
  .decision-box { background: #fef9c3; border: 2.5px solid #1e293b; border-radius: 16px; padding: 12px 18px; font-size: 18px; font-weight: bold; color: #0f172a; text-align: center; }
  .bottom-flow { display: flex; align-items: center; justify-content: space-between; padding-top: 14px; border-top: 2.5px dashed #cbd5e1; gap: 16px; }
  .btm-card { flex: 1; background: #fef9c3; border: 2.5px solid #1e293b; border-radius: 18px; padding: 14px 18px; display: flex; align-items: center; gap: 14px; }
  .btm-card h4 { font-size: 19px; color: #0f172a; font-weight: 700; margin-bottom: 3px; }
  .btm-card p { font-size: 15px; color: #475569; line-height: 1.35; }
</style>
</head>
<body>
<div class="box">
  <div>
    <div class="title">SENTINEL-EW &mdash; End-to-End Workflow</div>
    <div class="subtitle">Cognitive ES Receiver Strategy for Wideband Multi-Threat Spectrum Surveillance</div>
  </div>
  <div class="alert">
    <svg width="28" height="28" viewBox="0 0 24 24" fill="#ef4444"><path d="M12 2L1 21h22L12 2zm0 3.5L19.5 19h-15L12 5.5zM11 10v4h2v-4h-2zm0 6v2h2v-2h-2z"/></svg>
    <span><strong>Live Tactical C2 Telemetry</strong><br>Pd vs Pfa &bull; 38ms Lookahead &bull; Waterfall Scope</span>
  </div>
  <div class="top-flow">
    <div style="display:flex; flex-direction:column; align-items:center; gap:12px;">
      <div class="badge-pink"><svg width="22" height="22" viewBox="0 0 24 24" fill="#db2777"><path d="M8 5v14l11-7z"/></svg>Start</div>
      <div style="font-size:32px; font-weight:bold; color:#1e293b;">&darr;</div>
    </div>
    <div style="display:flex; flex-direction:column; gap:12px; width:440px;">
      <div class="badge-purple">RF Spectrum & Telemetry Inputs</div>
      <div class="yellow-card">
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#1e293b" stroke-width="2"><path d="M4.9 19.1C2 16.2 2 11.5 4.9 8.6M19.1 19.1C22 16.2 22 11.5 19.1 8.6M12 12m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0M12 14v8"/></svg>
        <div><h4>Hostile Radar Emitters</h4><p>Pulsed Radars, Agile Hoppers, Staggered PRF, Jammers</p></div>
      </div>
      <div class="yellow-card">
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#1e293b" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 3l-4 4-4-4"/></svg>
        <div><h4>Wideband ES Receiver</h4><p>Tunable Local Osc, Narrow IBW Filter, FFT Detector</p></div>
      </div>
      <div class="yellow-card">
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#1e293b" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
        <div><h4>Dwell & Intercept History</h4><p>Band Dwell Duration, Hit/Miss Counter, Revisit Gap</p></div>
      </div>
    </div>
    <div style="font-size:32px; font-weight:bold; color:#1e293b;">&rarr;</div>
    <div class="engine-card">
      <h3>Cognitive EW Dwell Engine</h3>
      <ul>
        <li>D-UCB Non-Stationary Bandit</li>
        <li>Deep Q-Network RL Scheduler</li>
        <li>Beam-Arrival Synchronizer</li>
        <li>Anti-Stroboscopic Sweeper</li>
        <li>DRDO FoM Real-Time Scoring</li>
      </ul>
    </div>
    <div style="font-size:32px; font-weight:bold; color:#1e293b;">&rarr;</div>
    <div style="display:flex; flex-direction:column; align-items:center;">
      <div class="badge-purple" style="margin-bottom:18px;">AI Decision Layer</div>
      <div class="diamond">
        <div class="diamond-in">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 2v4m0 12v4M2 12h4m12 0h4"/></svg>
          <h4 style="font-size:19px; font-weight:bold;">Threat Intercept</h4>
          <p style="font-size:13px;">Priority Scoring<br>Agile Lock-On</p>
        </div>
      </div>
    </div>
    <div style="font-size:32px; font-weight:bold; color:#1e293b;">&rarr;</div>
    <div style="display:flex; flex-direction:column; gap:18px; width:330px;">
      <div style="display:flex; align-items:center; gap:10px;">
        <span style="font-size:17px; font-weight:bold; color:#475569;">No:</span>
        <div class="decision-box" style="flex:1;">Continue Wideband Sweep</div>
      </div>
      <div style="display:flex; align-items:center; gap:10px;">
        <span style="font-size:17px; font-weight:bold; color:#0284c7;">Yes:</span>
        <div class="decision-box" style="flex:1; background:#e0f2fe; border-color:#0284c7;">Lock On & Rapid Dwell</div>
      </div>
    </div>
  </div>
  <div class="bottom-flow">
    <div class="btm-card">
      <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#0284c7" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 3v9l6 6"/></svg>
      <div><h4>Figures of Merit (FoM)</h4><p>Pd >95% &bull; MDS -95dBm &bull; Low False Alarms</p></div>
    </div>
    <div class="btm-card">
      <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
      <div><h4>Intercept Reliability</h4><p>97.3% Sustained Rate &bull; 38ms Lookahead</p></div>
    </div>
    <div class="btm-card">
      <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#9333ea" stroke-width="2"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><line x1="12" y1="3" x2="12" y2="21"/></svg>
      <div><h4>Tactical Recommendation</h4><p>Threat EOB &bull; Jamming Warning &bull; Audio Cues</p></div>
    </div>
    <div class="badge-pink">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#db2777" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>End
    </div>
  </div>
</div>
</body>
</html>"""
    p = DIAG_DIR / "s2_workflow.html"
    p.write_text(html, encoding="utf-8")
    render_edge(p, DIAG_DIR / "s2_workflow.png", 1972, 1150)

# ==========================================
# 2. Slide 2: Innovation and Uniqueness
# ==========================================
def make_s2_innovation():
    html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, sans-serif; }
  body { width: 2280px; height: 994px; background: transparent; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; padding-top: 15px; }
  .cloud {
    background: #3f5e3b; color: #ffffff; font-family: 'Georgia', serif; font-size: 50px; font-weight: bold;
    padding: 22px 80px; border-radius: 60px; box-shadow: 0 8px 24px rgba(0,0,0,0.15); text-align: center; line-height: 1.15;
  }
  .svg-lines { width: 2160px; height: 85px; margin-top: -15px; margin-bottom: 5px; }
  .cards-row { width: 2160px; display: flex; justify-content: space-between; gap: 32px; }
  .card { flex: 1; height: 720px; border-radius: 36px; padding: 18px; box-shadow: 0 10px 25px rgba(0,0,0,0.12); display: flex; flex-direction: column; }
  .card-inner { border: 3px dashed rgba(255,255,255,0.75); border-radius: 26px; height: 100%; padding: 30px 22px; display: flex; flex-direction: column; align-items: center; text-align: center; }
  .card-title { color: #ffffff; font-size: 31px; font-weight: 700; line-height: 1.25; min-height: 80px; display: flex; align-items: center; justify-content: center; }
  .sep { width: 80%; height: 2px; background: rgba(255,255,255,0.6); margin: 16px 0 22px 0; }
  .card-desc { color: #ffffff; font-size: 23px; line-height: 1.45; font-weight: 400; flex: 1; }
  .card-icon { width: 120px; height: 120px; margin-top: 12px; }
  .c1 { background: #b45309; }
  .c2 { background: #991b1b; }
  .c3 { background: #854d0e; }
  .c4 { background: #c2410c; }
  .c5 { background: #475569; }
</style>
</head>
<body>
  <div class="cloud">Innovation<br>and Uniqueness</div>
  <svg class="svg-lines" viewBox="0 0 2160 85" fill="none">
    <path d="M1080 0 C 1080 40, 216 10, 216 75" stroke="#2b2b2b" stroke-width="4" fill="none"/>
    <path d="M1080 0 C 1080 40, 648 20, 648 75" stroke="#2b2b2b" stroke-width="4" fill="none"/>
    <path d="M1080 0 L 1080 75" stroke="#2b2b2b" stroke-width="4" fill="none"/>
    <path d="M1080 0 C 1080 40, 1512 20, 1512 75" stroke="#2b2b2b" stroke-width="4" fill="none"/>
    <path d="M1080 0 C 1080 40, 1944 10, 1944 75" stroke="#2b2b2b" stroke-width="4" fill="none"/>
  </svg>
  <div class="cards-row">
    <div class="card c1"><div class="card-inner">
      <div class="card-title">Non-Stationary<br>Bandit Tuning</div><div class="sep"></div>
      <div class="card-desc">Combines D-UCB and EXP3 algorithms to dynamically learn emitter presence without requiring pre-mission intelligence databases.</div>
      <svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.5"><path d="M4.9 19.1C2 16.2 2 11.5 4.9 8.6M19.1 19.1C22 16.2 22 11.5 19.1 8.6M7.8 16.2C6 14.4 6 11.6 7.8 9.8M16.2 16.2C18 14.4 18 11.6 16.2 9.8M12 12m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0M12 14v8"/></svg>
    </div></div>
    <div class="card c2"><div class="card-inner">
      <div class="card-title">Deep Q-Network<br>RL Policy</div><div class="sep"></div>
      <div class="card-desc">Trained on 100,000+ radar pulse bursts to optimize dwell-time allocation, achieving +32.36 reward (vs +10.20 baseline).</div>
      <svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.5"><circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="6" r="3"/><circle cx="18" cy="18" r="3"/><circle cx="12" cy="12" r="3"/><line x1="8.5" y1="7.5" x2="10" y2="10.5"/><line x1="8.5" y1="16.5" x2="10" y2="13.5"/><line x1="15.5" y1="7.5" x2="14" y2="10.5"/><line x1="15.5" y1="16.5" x2="14" y2="13.5"/></svg>
    </div></div>
    <div class="card c3"><div class="card-inner">
      <div class="card-title">Predictive Beam<br>Intercept</div><div class="sep"></div>
      <div class="card-desc">Synchronizes receiver dwells with hostile rotating radar scan intervals, cutting lookahead intercept error down to 38.0 ms.</div>
      <svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.5"><circle cx="12" cy="12" r="9"/><path d="M12 3v9l6 6"/><path d="M12 7a5 5 0 0 1 5 5"/></svg>
    </div></div>
    <div class="card c4"><div class="card-inner">
      <div class="card-title">Anti-Stroboscopic<br>Sweeper</div><div class="sep"></div>
      <div class="card-desc">Employs prime-staggered non-harmonic dwell patterns, eliminating periodic blind spots and defeating threat evasion.</div>
      <svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.5"><path d="M2 12h3l2-6 3 12 3-8 2 5 2-3h5"/><path d="M2 20h20" stroke-dasharray="2 2"/></svg>
    </div></div>
    <div class="card c5"><div class="card-inner">
      <div class="card-title">Tactical 360°<br>PPI Scope</div><div class="sep"></div>
      <div class="card-desc">Full tactical C2 dashboard with 360° PPI radar scope, real-time waterfall display, and live audio threat alarms via WebSockets.</div>
      <svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.5"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/><line x1="12" y1="3" x2="12" y2="21"/><line x1="3" y1="12" x2="21" y2="12"/></svg>
    </div></div>
  </div>
</body>
</html>"""
    p = DIAG_DIR / "s2_innovation.html"
    p.write_text(html, encoding="utf-8")
    render_edge(p, DIAG_DIR / "s2_innovation.png", 2280, 994)

# ==========================================
# 3. Slide 3: 4 Zones Architecture
# ==========================================
def make_s3_zones():
    html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
  body { width: 2998px; height: 1702px; background: #ffffff; padding: 24px; display: flex; gap: 28px; }
  .zone-col {
    flex: 1; border-radius: 28px; padding: 24px 20px; display: flex; flex-direction: column;
    border: 3px solid; position: relative;
  }
  .zone-title {
    text-align: center; font-size: 38px; font-weight: 800; margin-bottom: 20px;
    padding-bottom: 12px; border-bottom: 2px solid rgba(0,0,0,0.1);
  }
  .sub-box {
    background: #ffffff; border-radius: 20px; padding: 22px; margin-bottom: 20px;
    border: 2px solid; box-shadow: 0 4px 12px rgba(0,0,0,0.04);
  }
  .sub-box h4 { font-size: 26px; font-weight: 700; margin-bottom: 10px; display: flex; align-items: center; gap: 12px; }
  .sub-box ul { list-style: square; margin-left: 28px; font-size: 21px; line-height: 1.55; color: #334155; }
  
  .z1 { background: #f0f9ff; border-color: #38bdf8; }
  .z1 .zone-title { color: #0369a1; }
  .z1 .sub-box { border-color: #bae6fd; }
  .z1 h4 { color: #0284c7; }

  .z2 { background: #f0fdf4; border-color: #22c55e; }
  .z2 .zone-title { color: #15803d; }
  .z2 .sub-box { border-color: #bbf7d0; }
  .z2 h4 { color: #16a34a; }

  .z3 { background: #faf5ff; border-color: #a855f7; }
  .z3 .zone-title { color: #7e22ce; }
  .z3 .sub-box { border-color: #e9d5ff; }
  .z3 h4 { color: #9333ea; }

  .z4 { background: #ecfeff; border-color: #06b6d4; }
  .z4 .zone-title { color: #0e7490; }
  .z4 .sub-box { border-color: #a5f3fc; }
  .z4 h4 { color: #0891b2; }

  .operator-box {
    margin-top: auto; background: #ffffff; border-radius: 20px; padding: 20px;
    border: 2px dashed #0284c7; display: flex; align-items: center; gap: 18px;
  }
  .operator-box h5 { font-size: 22px; color: #0f172a; }
  .operator-box p { font-size: 17px; color: #64748b; }
</style>
</head>
<body>
  <!-- Zone 1 -->
  <div class="zone-col z1">
    <div class="zone-title">Zone 1<br><span style="font-size:26px; font-weight:600;">RF Emitters & Threat Sources</span></div>
    <div class="sub-box">
      <h4><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#0284c7" stroke-width="2"><path d="M4.9 19.1C2 16.2 2 11.5 4.9 8.6M19.1 19.1C22 16.2 22 11.5 19.1 8.6M12 12m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0M12 14v8"/></svg>Active Threat Emitters</h4>
      <ul>
        <li>Rotating Radar G(&theta;, t) (Search / Track)</li>
        <li>Frequency-Agile Fast Hoppers</li>
        <li>Staggered / Jittered PRF Radars</li>
        <li>Broadband Barrage / Spot Jammers</li>
      </ul>
    </div>
    <div class="sub-box">
      <h4><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#0284c7" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 3v9l6 6"/></svg>Radiation Dynamics</h4>
      <ul>
        <li>Antenna Sidelobes & Mainbeam scan</li>
        <li>Pulse Width: 0.2 &mu;s &ndash; 100 &mu;s</li>
        <li>Multi-band RF span (0.5 &ndash; 18 GHz)</li>
      </ul>
    </div>
    <div class="operator-box">
      <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="#0284c7" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
      <div>
        <h5>ESM Operator / EW Specialist</h5>
        <p>Interactive Control & Live Tactical C2 Cues</p>
      </div>
    </div>
  </div>

  <!-- Zone 2 -->
  <div class="zone-col z2">
    <div class="zone-title">Zone 2<br><span style="font-size:26px; font-weight:600;">Tunable ES Receiver Engine</span></div>
    <div class="sub-box">
      <h4><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 3l-4 4-4-4"/></svg>Heterodyne Front-End</h4>
      <ul>
        <li>Agile Tunable Local Oscillator (LO)</li>
        <li>Narrow IBW Filter (1 of N sub-bands)</li>
        <li>Dwell Settling Timer (&tau;_settle < 50 &mu;s)</li>
        <li>Fast FFT Energy Detector & CFAR</li>
      </ul>
    </div>
    <div class="sub-box">
      <h4><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>Pulse Measurement Unit</h4>
      <ul>
        <li>Time-of-Arrival (TOA) & Pulse Width</li>
        <li>Frequency & Band Index Extraction</li>
        <li>Pulse Amplitude & SNR Estimator</li>
      </ul>
    </div>
    <div class="sub-box" style="margin-top:auto;">
      <h4><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>Receiver Calibration</h4>
      <ul>
        <li>MDS Sensitivity: &minus;95 dBm</li>
        <li>Hardware Sweep Delay Modeling</li>
        <li>Empirical Tuning Rate Verification</li>
      </ul>
    </div>
  </div>

  <!-- Zone 3 -->
  <div class="zone-col z3">
    <div class="zone-title">Zone 3<br><span style="font-size:26px; font-weight:600;">Edge Schedulers & Relay</span></div>
    <div class="sub-box">
      <h4><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#9333ea" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 2v4m0 12v4M2 12h4m12 0h4"/></svg>Cognitive Schedulers</h4>
      <ul>
        <li>Discounted UCB Bandit (&gamma; = 0.92)</li>
        <li>EXP3 Adversarial Bandit Policy</li>
        <li>Deep Q-Network (PyTorch RL Agent)</li>
        <li>Lookahead Beam Arrival Predictor</li>
      </ul>
    </div>
    <div class="sub-box">
      <h4><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#9333ea" stroke-width="2"><path d="M18 20V10M12 20V4M6 20v-6"/></svg>DRDO Figures of Merit</h4>
      <ul>
        <li>Probability of Intercept (Pd) Engine</li>
        <li>Revisit Latency & Miss Rate Evaluator</li>
        <li>Average Reward & Band Utilization</li>
      </ul>
    </div>
    <div class="sub-box" style="margin-top:auto;">
      <h4><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#9333ea" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M2 12h20"/></svg>WebSocket Telemetry Relay</h4>
      <ul>
        <li>Sub-millisecond JSON Telemetry Push</li>
        <li>Remote Mode & Parameter Control</li>
        <li>Bidirectional C2 State Sync</li>
      </ul>
    </div>
  </div>

  <!-- Zone 4 -->
  <div class="zone-col z4">
    <div class="zone-title">Zone 4<br><span style="font-size:26px; font-weight:600;">Tactical Intelligence & C2 Layer</span></div>
    <div class="sub-box">
      <h4><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#0891b2" stroke-width="2"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><line x1="12" y1="3" x2="12" y2="21"/></svg>Tactical C2 Radar Console</h4>
      <ul>
        <li>360&deg; PPI Radar Scope Display</li>
        <li>Real-Time Waterfall Spectrogram</li>
        <li>Live Pulse Descriptor Word (PDW) Log</li>
        <li>Multi-Frequency Energy Heatmap</li>
      </ul>
    </div>
    <div class="sub-box">
      <h4><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#0891b2" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>Electronic Order of Battle (EOB)</h4>
      <ul>
        <li>Hostile Radar Threat Classification</li>
        <li>Angle-of-Arrival (AoA) & Bearing Track</li>
        <li>Audio Tactical Strobe & Alarm Cues</li>
      </ul>
    </div>
    <div class="sub-box" style="margin-top:auto;">
      <h4><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#0891b2" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>Evidence & Audit Store</h4>
      <ul>
        <li>100,000+ Pulse Intercept Traces</li>
        <li>DRDO Operational Compliance Logs</li>
        <li>Full Mission Telemetry Replay</li>
      </ul>
    </div>
  </div>
</body>
</html>"""
    p = DIAG_DIR / "s3_zones.html"
    p.write_text(html, encoding="utf-8")
    render_edge(p, DIAG_DIR / "s3_zones.png", 2998, 1702)

# ==========================================
# 4. Slide 3: Technology Stack
# ==========================================
def make_s3_techstack():
    html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
  body { width: 3042px; height: 1014px; background: transparent; display: flex; align-items: center; justify-content: center; padding: 20px; }
  .pill-container {
    width: 2980px; height: 480px; background: #ffffff; border: 3px solid #cbd5e1; border-radius: 60px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.06); display: flex; align-items: center; padding: 30px 50px;
  }
  .left-header {
    width: 480px; display: flex; align-items: center; gap: 24px; padding-right: 40px;
    border-right: 3px solid #cbd5e1;
  }
  .bulb-icon { width: 84px; height: 84px; color: #1d4ed8; flex-shrink: 0; }
  .header-text { font-size: 38px; font-weight: 800; color: #1e3a8a; line-height: 1.25; }
  
  .tech-row {
    flex: 1; display: flex; justify-content: space-around; align-items: center; padding-left: 30px;
  }
  .tech-item { display: flex; flex-direction: column; align-items: center; text-align: center; width: 280px; }
  .tech-logo { width: 100px; height: 100px; margin-bottom: 16px; object-fit: contain; }
  .tech-name { font-size: 28px; font-weight: 800; color: #0f172a; margin-bottom: 6px; }
  .tech-role { font-size: 20px; color: #64748b; font-weight: 500; line-height: 1.25; }
</style>
</head>
<body>
<div class="pill-container">
  <div class="left-header">
    <svg class="bulb-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6m-4 4h2M12 2a7 7 0 0 0-7 7c0 2.38 1.19 4.47 3 5.74V17a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1v-2.26c1.81-1.27 3-3.36 3-5.74a7 7 0 0 0-7-7z"/></svg>
    <div class="header-text">Components /<br>Technology<br>stack to be used</div>
  </div>
  <div class="tech-row">
    <div class="tech-item">
      <svg class="tech-logo" viewBox="0 0 24 24" fill="#3776ab"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9v-2h2v2zm0-4H9V7h2v5zm4 4h-2v-2h2v2zm0-4h-2V7h2v5z"/></svg>
      <div class="tech-name">Python 3.8+</div>
      <div class="tech-role">(Core EW Simulation & Schedulers)</div>
    </div>
    <div class="tech-item">
      <svg class="tech-logo" viewBox="0 0 24 24" fill="#ee4c2c"><path d="M12 2l10 18H2L12 2zm0 4L5 18h14L12 6z"/></svg>
      <div class="tech-name">PyTorch</div>
      <div class="tech-role">(Deep Q-Network RL Training)</div>
    </div>
    <div class="tech-item">
      <svg class="tech-logo" viewBox="0 0 24 24" fill="#013243"><circle cx="12" cy="12" r="10" stroke="#4dabf7" stroke-width="2" fill="none"/><path d="M8 8h8v8H8z" fill="#4dabf7"/></svg>
      <div class="tech-name">NumPy / SciPy</div>
      <div class="tech-role">(RF Signal & FFT Math Engine)</div>
    </div>
    <div class="tech-item">
      <svg class="tech-logo" viewBox="0 0 24 24" fill="#059669"><rect x="3" y="3" width="18" height="18" rx="4" fill="#10b981"/><path d="M8 12h8M12 8v8" stroke="white" stroke-width="2"/></svg>
      <div class="tech-name">Gymnasium</div>
      <div class="tech-role">(RL Environment Framework)</div>
    </div>
    <div class="tech-item">
      <svg class="tech-logo" viewBox="0 0 24 24" fill="#009688"><polygon points="12,2 2,22 22,22" fill="#059669"/><text x="12" y="19" font-size="9" fill="white" font-weight="bold" text-anchor="middle">API</text></svg>
      <div class="tech-name">FastAPI</div>
      <div class="tech-role">(High-Speed Telemetry REST)</div>
    </div>
    <div class="tech-item">
      <svg class="tech-logo" viewBox="0 0 24 24" fill="#0284c7"><path d="M4 12a8 8 0 0 1 16 0M7 12a5 5 0 0 1 10 0M10 12a2 2 0 0 1 4 0" stroke="#0284c7" stroke-width="2" fill="none"/></svg>
      <div class="tech-name">WebSockets</div>
      <div class="tech-role">(Sub-ms C2 Stream Protocol)</div>
    </div>
    <div class="tech-item">
      <svg class="tech-logo" viewBox="0 0 24 24" fill="#000000"><polygon points="12,2 22,20 2,20" stroke="black" stroke-width="2" fill="none"/><line x1="12" y1="2" x2="12" y2="20" stroke="black"/><line x1="2" y1="20" x2="17" y2="11" stroke="black"/></svg>
      <div class="tech-name">Three.js / HTML5</div>
      <div class="tech-role">(Tactical 360&deg; PPI Radar Scope)</div>
    </div>
    <div class="tech-item">
      <svg class="tech-logo" viewBox="0 0 24 24" fill="#f59e0b"><circle cx="12" cy="12" r="9" fill="#fbbf24"/><path d="M9 9h6v6H9z" fill="#78350f"/></svg>
      <div class="tech-name">Turing Radar DB</div>
      <div class="tech-role">(JC Wise 2024 Benchmark Dataset)</div>
    </div>
  </div>
</div>
</body>
</html>"""
    p = DIAG_DIR / "s3_techstack.html"
    p.write_text(html, encoding="utf-8")
    render_edge(p, DIAG_DIR / "s3_techstack.png", 3042, 1014)

# ==========================================
# 5. Slide 3: Implementation Process
# ==========================================
def make_s3_process():
    html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
  body { width: 1434px; height: 2150px; background: #ffffff; padding: 24px; }
  .container {
    width: 100%; height: 100%; border: 4px solid #1e293b; border-radius: 40px; background: #ffffff;
    padding: 40px 48px; display: flex; flex-direction: column; position: relative;
  }
  .header {
    display: flex; align-items: center; gap: 20px; border-bottom: 3px solid #e2e8f0; padding-bottom: 24px; margin-bottom: 36px;
  }
  .header h2 { font-size: 50px; font-weight: 900; color: #0f172a; letter-spacing: 1px; }
  
  .timeline { flex: 1; display: flex; flex-direction: column; justify-content: space-between; position: relative; padding: 10px 0; }
  
  /* S-curve SVG line behind the badges */
  .curve-bg { position: absolute; top: 40px; bottom: 40px; left: 0; width: 100%; height: calc(100% - 80px); z-index: 1; pointer-events: none; }
  
  .step-row { display: flex; align-items: center; position: relative; z-index: 2; gap: 32px; }
  .step-row.left { flex-direction: row; }
  .step-row.right { flex-direction: row-reverse; }
  
  .circle-badge {
    width: 160px; height: 160px; border-radius: 50%; display: flex; flex-direction: column;
    align-items: center; justify-content: center; color: #ffffff; box-shadow: 0 10px 25px rgba(0,0,0,0.18);
    flex-shrink: 0; border: 6px solid #ffffff;
  }
  .badge-num { font-size: 52px; font-weight: 900; line-height: 1; }
  
  .step-card {
    flex: 1; background: #f8fafc; border: 2.5px solid #cbd5e1; border-radius: 26px; padding: 24px 30px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.04);
  }
  .step-card h3 { font-size: 34px; font-weight: 800; margin-bottom: 8px; }
  .step-card p { font-size: 23px; line-height: 1.45; color: #475569; }
  
  .b1 { background: #0a2540; } .t1 { color: #0a2540; }
  .b2 { background: #0284c7; } .t2 { color: #0284c7; }
  .b3 { background: #16a34a; } .t3 { color: #16a34a; }
  .b4 { background: #d97706; } .t4 { color: #d97706; }
  .b5 { background: #ea580c; } .t5 { color: #ea580c; }
  .b6 { background: #7c3aed; } .t6 { color: #7c3aed; }
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="#0f172a" stroke-width="2.5"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
    <h2>IMPLEMENTATION PROCESS</h2>
  </div>

  <div class="timeline">
    <!-- Step 1 -->
    <div class="step-row left">
      <div class="circle-badge b1"><span class="badge-num">1</span></div>
      <div class="step-card">
        <h3 class="t1">Model RF Spectrum & Emitters</h3>
        <p>Synthesize dynamic multi-band RF world with agile frequency-hopping radars, staggered PRF, rotating antennas, and noise jammers.</p>
      </div>
    </div>

    <!-- Step 2 -->
    <div class="step-row right">
      <div class="circle-badge b2"><span class="badge-num">2</span></div>
      <div class="step-card">
        <h3 class="t2">Emulate Tunable ES Receiver</h3>
        <p>Build superheterodyne receiver model constrained by narrow IBW, LO tuning delay, dwell settling intervals, and thermal noise floor.</p>
      </div>
    </div>

    <!-- Step 3 -->
    <div class="step-row left">
      <div class="circle-badge b3"><span class="badge-num">3</span></div>
      <div class="step-card">
        <h3 class="t3">Deploy Cognitive Schedulers</h3>
        <p>Train Deep Q-Network and D-UCB bandit agents to dynamically optimize dwell scheduling from live hit/miss feedback.</p>
      </div>
    </div>

    <!-- Step 4 -->
    <div class="step-row right">
      <div class="circle-badge b4"><span class="badge-num">4</span></div>
      <div class="step-card">
        <h3 class="t4">Evaluate DRDO Figures of Merit</h3>
        <p>Continuously benchmark Probability of Intercept (Pd), False Alarm Rate (Pfa), MDS sensitivity, and lookahead timing error.</p>
      </div>
    </div>

    <!-- Step 5 -->
    <div class="step-row left">
      <div class="circle-badge b5"><span class="badge-num">5</span></div>
      <div class="step-card">
        <h3 class="t5">Validate in Closed Loop</h3>
        <p>Verify adaptive scheduler against sequential and periodic open-loop sweeps across 100,000+ synthetic radar pulse bursts.</p>
      </div>
    </div>

    <!-- Step 6 -->
    <div class="step-row right">
      <div class="circle-badge b6"><span class="badge-num">6</span></div>
      <div class="step-card">
        <h3 class="t6">Tactical C2 PPI Deployment</h3>
        <p>Stream real-time telemetry over WebSockets to 360&deg; PPI radar scope and waterfall display for tactical ESM operators.</p>
      </div>
    </div>
  </div>
</div>
</body>
</html>"""
    p = DIAG_DIR / "s3_process.html"
    p.write_text(html, encoding="utf-8")
    render_edge(p, DIAG_DIR / "s3_process.png", 1434, 2150)

# ==========================================
# 6. Slide 4: Feasibility / Viability / Implementation
# ==========================================
def make_s4_feasibility():
    html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
  body { width: 3040px; height: 1014px; background: transparent; display: flex; align-items: center; justify-content: center; padding: 20px; }
  .cards-row { width: 2980px; height: 950px; display: flex; justify-content: space-between; gap: 40px; }
  .card {
    flex: 1; background: #ffffff; border: 3px solid #1e293b; border-radius: 36px; padding: 44px 38px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.06); display: flex; flex-direction: column;
  }
  .card-header { font-family: 'Georgia', serif; font-size: 46px; font-weight: bold; color: #0033cc; margin-bottom: 24px; padding-bottom: 12px; border-bottom: 2px solid #e2e8f0; }
  .card ul { list-style: disc; margin-left: 32px; font-size: 26px; line-height: 1.6; color: #1e293b; flex: 1; display: flex; flex-direction: column; justify-content: space-around; }
  .card ul li { margin-bottom: 14px; }
</style>
</head>
<body>
<div class="cards-row">
  <div class="card">
    <div class="card-header">Feasibility</div>
    <ul>
      <li><strong>Working prototype integrates 8 scan schedulers</strong> (DQN, D-UCB, EXP3, Predictive, Periodic, Sequential, Random, Priority) with an agile RF simulation engine.</li>
      <li><strong>Calibrated using the Alan Turing Institute Radar Emitter Dataset</strong> (JC Wise 2024) and DRDO Electronic Support Measures operational benchmarks.</li>
      <li><strong>Lightweight Python/PyTorch inference</strong> executes in &lt;1ms per dwell step, fully compatible with embedded tactical DSPs and FPGA microcontrollers.</li>
    </ul>
  </div>

  <div class="card">
    <div class="card-header">Viability</div>
    <ul>
      <li><strong>Closed-loop cognitive scheduling delivers +217% higher cumulative reward</strong> (+32.36 vs +10.20) and 97.3% sustained threat interception compared to static sweeps.</li>
      <li><strong>Pure software upgrade</strong> integrates seamlessly into existing heterodyne receiver architectures without requiring expensive RF hardware replacement.</li>
      <li><strong>Modular plugin design</strong> allows new emitter classes, antenna radiation patterns, and operational frequency bands to be incorporated instantly.</li>
    </ul>
  </div>

  <div class="card">
    <div class="card-header">Practical Implementation</div>
    <ul>
      <li><strong>Deployable immediately</strong> as a simulation-backed tactical decision-support system and cognitive scheduler add-on for ESM suites.</li>
      <li><strong>High-speed WebSocket telemetry server</strong> feeds a live browser-based C2 console featuring a 360&deg; PPI radar scope, spectrum waterfall, and audio threat alarms.</li>
      <li><strong>Phased hardware-in-the-loop roadmap</strong> supports direct integration with SDR receivers (HackRF One, USRP) and DRDO DLRL receiver frontends.</li>
    </ul>
  </div>
</div>
</body>
</html>"""
    p = DIAG_DIR / "s4_feasibility.html"
    p.write_text(html, encoding="utf-8")
    render_edge(p, DIAG_DIR / "s4_feasibility.png", 3040, 1014)

# ==========================================
# 7. Slide 4: Challenges & Strategies
# ==========================================
def make_s4_challenges():
    html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
  body {
    width: 2480px; height: 1244px; background: #ffffff; padding: 30px;
    background-image: radial-gradient(#e2e8f0 1.5px, transparent 1.5px);
    background-size: 24px 24px; display: flex; align-items: center; justify-content: space-between; position: relative;
  }
  .center-divider {
    position: absolute; left: 50%; top: 40px; bottom: 40px; width: 2px;
    border-left: 2px dashed #94a3b8;
  }
  
  .half { width: 48%; height: 100%; display: flex; align-items: center; position: relative; }
  
  .hub {
    width: 280px; height: 280px; border-radius: 50%; display: flex; flex-direction: column;
    align-items: center; justify-content: center; text-align: center; padding: 24px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.12); z-index: 5; flex-shrink: 0;
  }
  .hub-title { font-size: 28px; font-weight: 800; line-height: 1.25; margin-top: 10px; }
  
  .hub-red { background: #e0f2fe; border: 4px solid #0284c7; color: #0f172a; }
  .hub-green { background: #dcfce7; border: 4px solid #16a34a; color: #0f172a; }
  
  .items-col { flex: 1; display: flex; flex-direction: column; justify-content: space-between; height: 100%; padding: 20px 0; }
  
  .item-row { display: flex; align-items: center; gap: 20px; }
  .badge-red {
    background: #ef4444; color: white; width: 64px; height: 64px; border-radius: 50%;
    font-size: 28px; font-weight: 900; display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; box-shadow: 0 4px 10px rgba(239,68,68,0.3);
  }
  .badge-green {
    background: #16a34a; color: white; width: 64px; height: 64px; border-radius: 50%;
    font-size: 28px; font-weight: 900; display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; box-shadow: 0 4px 10px rgba(22,163,74,0.3);
  }
  
  .item-text { font-size: 22px; line-height: 1.45; color: #1e293b; }
  .item-text strong { font-size: 23px; color: #0f172a; }
</style>
</head>
<body>
  <div class="center-divider"></div>

  <!-- Left: Challenges -->
  <div class="half" style="padding-right: 30px; gap: 30px;">
    <div class="hub hub-red">
      <svg width="70" height="70" viewBox="0 0 24 24" fill="none" stroke="#0284c7" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
      <div class="hub-title">Potential Challenges<br>and Risks</div>
    </div>
    <div class="items-col">
      <div class="item-row">
        <div class="badge-red">01</div>
        <div class="item-text"><strong>Non-Stationary Hopping:</strong> Fast frequency agility causes threats to depart before receiver dwell completes.</div>
      </div>
      <div class="item-row">
        <div class="badge-red">02</div>
        <div class="item-text"><strong>IBW Hardware Bottleneck:</strong> Instantaneous bandwidth is an order of magnitude narrower than overall spectrum.</div>
      </div>
      <div class="item-row">
        <div class="badge-red">03</div>
        <div class="item-text"><strong>Stroboscopic Blind Spots:</strong> Periodic sweeping synchronizes with radar rotation, causing persistent dropouts.</div>
      </div>
      <div class="item-row">
        <div class="badge-red">04</div>
        <div class="item-text"><strong>Noise & Jamming Interference:</strong> Thermal noise bursts and intentional jamming trigger false alarms.</div>
      </div>
      <div class="item-row">
        <div class="badge-red">05</div>
        <div class="item-text"><strong>Real-Time Edge Latency:</strong> Scheduling decisions must execute in &lt;1ms intervals on tactical DSP processors.</div>
      </div>
    </div>
  </div>

  <!-- Right: Strategies -->
  <div class="half" style="padding-left: 30px; gap: 30px; flex-direction: row-reverse;">
    <div class="hub hub-green">
      <svg width="70" height="70" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>
      <div class="hub-title">Strategies For<br>Overcoming<br>Challenges</div>
    </div>
    <div class="items-col">
      <div class="item-row">
        <div class="badge-green">01</div>
        <div class="item-text"><strong>Discounted Bandits (D-UCB):</strong> Exponential discounting (&gamma;=0.92) rapidly adapts to non-stationary agility.</div>
      </div>
      <div class="item-row">
        <div class="badge-green">02</div>
        <div class="item-text"><strong>Reinforcement Learning Policy:</strong> DQN dynamically allocates narrow IBW to high-priority threat bands.</div>
      </div>
      <div class="item-row">
        <div class="badge-green">03</div>
        <div class="item-text"><strong>Prime-Staggered Scanning:</strong> Anti-stroboscopic non-harmonic dwell patterns break periodic synchronization.</div>
      </div>
      <div class="item-row">
        <div class="badge-green">04</div>
        <div class="item-text"><strong>Adaptive CFAR & MDS Filter:</strong> Constant False Alarm Rate detector & MDS thresholds reject noise floor.</div>
      </div>
      <div class="item-row">
        <div class="badge-green">05</div>
        <div class="item-text"><strong>Optimized Vectorized Policy:</strong> Pre-compiled neural weights and tensor math guarantee &lt;1ms step latency.</div>
      </div>
    </div>
  </div>
</body>
</html>"""
    p = DIAG_DIR / "s4_challenges.html"
    p.write_text(html, encoding="utf-8")
    render_edge(p, DIAG_DIR / "s4_challenges.png", 2480, 1244)

# ==========================================
# 8. Slide 5: Stakeholders Hub-and-Spoke
# ==========================================
def make_s5_stakeholders():
    html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
  body { width: 2392px; height: 1684px; background: #ffffff; padding: 40px; display: flex; align-items: center; justify-content: center; position: relative; }
  
  .hub-center {
    width: 440px; height: 440px; border-radius: 50%; background: #ffffff;
    box-shadow: 0 16px 40px rgba(0,0,0,0.15); display: flex; flex-direction: column;
    align-items: center; justify-content: center; text-align: center; padding: 36px;
    position: relative; z-index: 10; border: 8px solid transparent;
    background-image: linear-gradient(white, white), conic-gradient(#0284c7 0% 25%, #16a34a 25% 50%, #ea580c 50% 75%, #9333ea 75% 100%);
    background-origin: border-box; background-clip: padding-box, border-box;
  }
  .hub-center h2 { font-family: 'Georgia', serif; font-size: 42px; font-weight: bold; color: #0f172a; line-height: 1.2; margin-top: 12px; }
  
  .svg-spokes { position: absolute; width: 100%; height: 100%; top: 0; left: 0; pointer-events: none; z-index: 2; }
  
  .node-card {
    position: absolute; background: #f8fafc; border: 2.5px solid #cbd5e1; border-radius: 24px;
    padding: 24px 30px; box-shadow: 0 8px 24px rgba(0,0,0,0.06); width: 620px; z-index: 5;
    display: flex; gap: 20px; align-items: flex-start;
  }
  .node-icon { width: 64px; height: 64px; flex-shrink: 0; border-radius: 16px; display: flex; align-items: center; justify-content: center; }
  .node-title { font-size: 28px; font-weight: 800; margin-bottom: 6px; }
  .node-desc { font-size: 21px; line-height: 1.45; color: #475569; }
  
  .node-top { top: 60px; left: 50%; transform: translateX(-50%); }
  .node-right { right: 60px; top: 50%; transform: translateY(-50%); }
  .node-left { left: 60px; top: 50%; transform: translateY(-50%); }
  .node-bottom { bottom: 60px; left: 50%; transform: translateX(-50%); }
  
  .i-blue { background: #e0f2fe; color: #0284c7; }
  .i-green { background: #dcfce7; color: #16a34a; }
  .i-orange { background: #ffedd5; color: #ea580c; }
  .i-purple { background: #f3e8ff; color: #9333ea; }
</style>
</head>
<body>
  <svg class="svg-spokes" viewBox="0 0 2392 1684" fill="none">
    <path d="M 1196 620 L 1196 280" stroke="#1e293b" stroke-width="5" stroke-dasharray="8 8"/>
    <circle cx="1196" cy="280" r="10" fill="#0284c7"/>
    <path d="M 1416 842 L 1700 842" stroke="#1e293b" stroke-width="5" stroke-dasharray="8 8"/>
    <circle cx="1700" cy="842" r="10" fill="#16a34a"/>
    <path d="M 976 842 L 690 842" stroke="#1e293b" stroke-width="5" stroke-dasharray="8 8"/>
    <circle cx="690" cy="842" r="10" fill="#ea580c"/>
    <path d="M 1196 1062 L 1196 1400" stroke="#1e293b" stroke-width="5" stroke-dasharray="8 8"/>
    <circle cx="1196" cy="1400" r="10" fill="#9333ea"/>
  </svg>

  <div class="hub-center">
    <svg width="70" height="70" viewBox="0 0 24 24" fill="none" stroke="#0284c7" stroke-width="2"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/><line x1="12" y1="3" x2="12" y2="21"/><line x1="3" y1="12" x2="21" y2="12"/></svg>
    <h2>Potential Impact on<br>Stakeholders</h2>
  </div>

  <!-- Top: ESM Operators -->
  <div class="node-card node-top">
    <div class="node-icon i-blue"><svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4.9 19.1C2 16.2 2 11.5 4.9 8.6M19.1 19.1C22 16.2 22 11.5 19.1 8.6M12 12m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0M12 14v8"/></svg></div>
    <div>
      <div class="node-title" style="color:#0284c7;">ESM Operators</div>
      <div class="node-desc">Automated cognitive sweeping eliminates manual tuning fatigue; real-time audio and visual alerts provide instant threat warning and lock-on cues.</div>
    </div>
  </div>

  <!-- Right: Mission Commanders -->
  <div class="node-card node-right">
    <div class="node-icon i-green"><svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 21h18M5 21V7l7-4 7 4v14M10 9h4m-4 4h4m-4 4h4"/></svg></div>
    <div>
      <div class="node-title" style="color:#16a34a;">Mission Commanders</div>
      <div class="node-desc">Live tactical 360&deg; PPI radar scope provides real-time Electronic Order of Battle (EOB), active radar bearings, and threat alert status.</div>
    </div>
  </div>

  <!-- Left: Defence R&D Teams -->
  <div class="node-card node-left">
    <div class="node-icon i-orange"><svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg></div>
    <div>
      <div class="node-title" style="color:#ea580c;">Defence R&D (DRDO / DLRL)</div>
      <div class="node-desc">Standardized, modular Python/PyTorch framework enables rapid algorithmic prototyping and seamless integration into existing EW suites.</div>
    </div>
  </div>

  <!-- Bottom: Defence Fleet Managers -->
  <div class="node-card node-bottom">
    <div class="node-icon i-purple"><svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></div>
    <div>
      <div class="node-title" style="color:#9333ea;">Defence Fleet Managers</div>
      <div class="node-desc">Software-only deployment brings cognitive capabilities to airborne (UAV/fighter), naval, and ground ESM platforms with minimal SWaP-C cost.</div>
    </div>
  </div>
</body>
</html>"""
    p = DIAG_DIR / "s5_stakeholders.html"
    p.write_text(html, encoding="utf-8")
    render_edge(p, DIAG_DIR / "s5_stakeholders.png", 2392, 1684)

# ==========================================
# 9. Slide 5: Benefits of the Solution
# ==========================================
def make_s5_benefits():
    html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
  body { width: 1604px; height: 1924px; background: #ffffff; padding: 30px; display: flex; flex-direction: column; justify-content: space-between; }
  
  .pill-banner {
    background: #005596; border-radius: 40px; padding: 20px 48px; display: flex; align-items: center;
    gap: 24px; color: white; box-shadow: 0 8px 24px rgba(0,85,150,0.25); margin-bottom: 20px;
  }
  .pill-banner h2 { font-family: 'Georgia', serif; font-size: 52px; font-weight: bold; }
  
  .quote-card {
    background: #ffffff; border: 3px solid #1e293b; border-radius: 36px; padding: 36px 44px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.06); display: flex; align-items: center; justify-content: space-between;
    gap: 36px; position: relative;
  }
  
  .quote-content { flex: 1; }
  .quote-marks { font-family: 'Georgia', serif; font-size: 72px; color: #64748b; line-height: 0.8; font-weight: bold; }
  .quote-text { font-size: 32px; line-height: 1.5; color: #1e293b; font-weight: 500; margin: 12px 0; }
  .quote-text strong { color: #005596; font-weight: 800; }
  
  .card-label-col {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    width: 280px; text-align: center; flex-shrink: 0; border-left: 2px solid #e2e8f0; padding-left: 28px;
  }
  .label-icon { width: 90px; height: 90px; margin-bottom: 12px; }
  .label-title { font-size: 30px; font-weight: 800; color: #0f172a; line-height: 1.2; }
</style>
</head>
<body>
  <div class="pill-banner">
    <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
    <h2>Benefits of the Solution</h2>
  </div>

  <!-- Card 1 -->
  <div class="quote-card">
    <div class="quote-content">
      <div class="quote-marks">&ldquo;</div>
      <div class="quote-text">Slashes threat detection latency to <strong>&lt;40ms</strong> by anticipating agile emitter beam arrivals, giving aircraft vital seconds to evade radar lock.</div>
      <div class="quote-marks" style="text-align:right;">&rdquo;</div>
    </div>
    <div class="card-label-col">
      <svg class="label-icon" viewBox="0 0 24 24" fill="none" stroke="#0284c7" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
      <div class="label-title">Threat Intercept Speed</div>
    </div>
  </div>

  <!-- Card 2 -->
  <div class="quote-card">
    <div class="quote-content">
      <div class="quote-marks">&ldquo;</div>
      <div class="quote-text"><strong>100% software-defined</strong> cognitive layer avoids multi-crore hardware overhauls by extracting maximum intelligence from existing narrow-IBW receivers.</div>
      <div class="quote-marks" style="text-align:right;">&rdquo;</div>
    </div>
    <div class="card-label-col">
      <svg class="label-icon" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
      <div class="label-title">Lifecycle Economy</div>
    </div>
  </div>

  <!-- Card 3 -->
  <div class="quote-card">
    <div class="quote-content">
      <div class="quote-marks">&ldquo;</div>
      <div class="quote-text">Autonomously discovers and tracks hostile emitters with <strong>zero prior intelligence</strong>, guaranteeing comprehensive baseline spectrum protection.</div>
      <div class="quote-marks" style="text-align:right;">&rdquo;</div>
    </div>
    <div class="card-label-col">
      <svg class="label-icon" viewBox="0 0 24 24" fill="none" stroke="#ea580c" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
      <div class="label-title">Operational Readiness</div>
    </div>
  </div>
</body>
</html>"""
    p = DIAG_DIR / "s5_benefits.html"
    p.write_text(html, encoding="utf-8")
    render_edge(p, DIAG_DIR / "s5_benefits.png", 1604, 1924)

if __name__ == "__main__":
    print("Generating all 9 visual components...")
    make_s2_workflow()
    make_s2_innovation()
    make_s3_zones()
    make_s3_techstack()
    make_s3_process()
    make_s4_feasibility()
    make_s4_challenges()
    make_s5_stakeholders()
    make_s5_benefits()
    print("All 9 components generated successfully!")

