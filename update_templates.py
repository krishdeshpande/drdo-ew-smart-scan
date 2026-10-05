from pathlib import Path
import subprocess

s3_tech = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
  body { width: 3000px; height: 360px; background: transparent; display: flex; align-items: center; justify-content: center; padding: 10px; }
  .pill-container {
    width: 2960px; height: 340px; background: #ffffff; border: 3px solid #cbd5e1; border-radius: 60px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.06); display: flex; align-items: center; padding: 15px 40px;
  }
  .left-header {
    width: 440px; display: flex; align-items: center; gap: 20px; padding-right: 30px;
    border-right: 3px solid #cbd5e1;
  }
  .bulb-icon { width: 75px; height: 75px; color: #1d4ed8; flex-shrink: 0; }
  .header-text { font-size: 34px; font-weight: 800; color: #1e3a8a; line-height: 1.25; }
  
  .tech-row {
    flex: 1; display: flex; justify-content: space-around; align-items: center; padding-left: 20px;
  }
  .tech-item { display: flex; flex-direction: column; align-items: center; text-align: center; width: 290px; }
  .tech-logo { width: 75px; height: 75px; margin-bottom: 10px; object-fit: contain; }
  .tech-name { font-size: 26px; font-weight: 800; color: #0f172a; margin-bottom: 4px; }
  .tech-role { font-size: 18px; color: #64748b; font-weight: 500; line-height: 1.2; }
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
      <div class="tech-role">(Core EW Sim & Schedulers)</div>
    </div>
    <div class="tech-item">
      <svg class="tech-logo" viewBox="0 0 24 24" fill="#ee4c2c"><path d="M12 2l10 18H2L12 2zm0 4L5 18h14L12 6z"/></svg>
      <div class="tech-name">PyTorch</div>
      <div class="tech-role">(DQN RL Policy Training)</div>
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
      <div class="tech-role">(Tactical 360° PPI Scope)</div>
    </div>
    <div class="tech-item">
      <svg class="tech-logo" viewBox="0 0 24 24" fill="#f59e0b"><circle cx="12" cy="12" r="9" fill="#fbbf24"/><path d="M9 9h6v6H9z" fill="#78350f"/></svg>
      <div class="tech-name">Turing Radar DB</div>
      <div class="tech-role">(Benchmark Dataset)</div>
    </div>
  </div>
</div>
</body>
</html>"""

s5_banner = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { width: 3000px; height: 160px; background: transparent; display: flex; align-items: center; justify-content: center; }
  .banner-container {
    width: 2960px; height: 140px; position: relative; display: flex; align-items: center; justify-content: center;
  }
  .banner-svg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
  .banner-text {
    position: relative; z-index: 2; font-family: 'Georgia', serif; font-size: 38px; font-weight: bold; font-style: italic;
    color: #0f172a; text-align: center; padding: 0 80px; letter-spacing: 0.5px;
  }
</style>
</head>
<body>
<div class="banner-container">
  <svg class="banner-svg" viewBox="0 0 2960 140" preserveAspectRatio="none">
    <polygon points="0,0 2960,0 2900,70 2960,140 0,140 60,70" fill="#e2e8f0" stroke="#0f172a" stroke-width="4"/>
  </svg>
  <div class="banner-text">
    “India’s next-generation cognitive electronic warfare intelligence—zero-prior adaptation, rapid threat intercepts, mission-ready dominance.”
  </div>
</div>
</body>
</html>"""

s5_stakeholders = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
  body { width: 2392px; height: 1684px; background: #ffffff; padding: 30px; display: flex; align-items: center; justify-content: center; position: relative; }
  
  .hub-center {
    width: 460px; height: 460px; border-radius: 50%; background: #ffffff;
    box-shadow: 0 16px 40px rgba(0,0,0,0.12); display: flex; flex-direction: column;
    align-items: center; justify-content: center; text-align: center; padding: 36px;
    position: relative; z-index: 10; border: 10px solid transparent;
    background-image: linear-gradient(white, white), conic-gradient(#0284c7 0% 25%, #16a34a 25% 50%, #ea580c 50% 75%, #9333ea 75% 100%);
    background-origin: border-box; background-clip: padding-box, border-box;
  }
  .hub-center h2 { font-family: 'Georgia', serif; font-size: 42px; font-weight: bold; color: #0f172a; line-height: 1.25; margin-top: 14px; }
  
  .svg-spokes { position: absolute; width: 100%; height: 100%; top: 0; left: 0; pointer-events: none; z-index: 2; }
  
  .node-card {
    position: absolute; background: #f8fafc; border: 2.5px solid #cbd5e1; border-radius: 24px;
    padding: 24px 30px; box-shadow: 0 8px 24px rgba(0,0,0,0.06); width: 640px; z-index: 5;
    display: flex; gap: 20px; align-items: flex-start;
  }
  .node-icon { width: 68px; height: 68px; flex-shrink: 0; border-radius: 16px; display: flex; align-items: center; justify-content: center; }
  .node-title { font-size: 28px; font-weight: 800; margin-bottom: 6px; }
  .node-desc { font-size: 20px; line-height: 1.45; color: #475569; }
  
  .node-top { top: 40px; left: 50%; transform: translateX(-50%); }
  .node-right { right: 40px; top: 50%; transform: translateY(-50%); }
  .node-left { left: 40px; top: 50%; transform: translateY(-50%); }
  .node-bottom { bottom: 40px; left: 50%; transform: translateX(-50%); }
  
  .i-blue { background: #e0f2fe; color: #0284c7; }
  .i-green { background: #dcfce7; color: #16a34a; }
  .i-orange { background: #ffedd5; color: #ea580c; }
  .i-purple { background: #f3e8ff; color: #9333ea; }
</style>
</head>
<body>
  <svg class="svg-spokes" viewBox="0 0 2392 1684" fill="none">
    <!-- Top connector -->
    <path d="M 1196 612 L 1196 260" stroke="#0284c7" stroke-width="6"/>
    <circle cx="1196" cy="260" r="12" fill="#0284c7"/>
    
    <!-- Right connector (elbow) -->
    <path d="M 1426 842 L 1712 842" stroke="#16a34a" stroke-width="6"/>
    <circle cx="1712" cy="842" r="12" fill="#16a34a"/>
    
    <!-- Left connector (elbow) -->
    <path d="M 966 842 L 680 842" stroke="#ea580c" stroke-width="6"/>
    <circle cx="680" cy="842" r="12" fill="#ea580c"/>
    
    <!-- Bottom connector -->
    <path d="M 1196 1072 L 1196 1420" stroke="#9333ea" stroke-width="6"/>
    <circle cx="1196" cy="1420" r="12" fill="#9333ea"/>
  </svg>

  <div class="hub-center">
    <svg width="74" height="74" viewBox="0 0 24 24" fill="none" stroke="#0284c7" stroke-width="2"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/><line x1="12" y1="3" x2="12" y2="21"/><line x1="3" y1="12" x2="21" y2="12"/></svg>
    <h2>Potential Impact on<br>Stakeholders</h2>
  </div>

  <!-- Top: ESM Operators -->
  <div class="node-card node-top">
    <div class="node-icon i-blue"><svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4.9 19.1C2 16.2 2 11.5 4.9 8.6M19.1 19.1C22 16.2 22 11.5 19.1 8.6M12 12m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0M12 14v8"/></svg></div>
    <div>
      <div class="node-title" style="color:#0284c7;">ESM Operators:</div>
      <div class="node-desc">Automated cognitive sweeping eliminates manual tuning fatigue; real-time audio and visual alerts provide instant threat warning and lock-on cues.</div>
    </div>
  </div>

  <!-- Right: Mission Commanders -->
  <div class="node-card node-right">
    <div class="node-icon i-green"><svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 21h18M3 7v1a3 3 0 0 0 6 0V7m0 1a3 3 0 0 0 6 0V7m0 1a3 3 0 0 0 6 0V7M4 21V4a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v17"/></svg></div>
    <div>
      <div class="node-title" style="color:#16a34a;">Mission Commanders:</div>
      <div class="node-desc">Live tactical 360° PPI radar scope provides real-time Electronic Order of Battle (EOB), active radar bearings, and threat alert status.</div>
    </div>
  </div>

  <!-- Left: Defence R&D -->
  <div class="node-card node-left">
    <div class="node-icon i-orange"><svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg></div>
    <div>
      <div class="node-title" style="color:#ea580c;">Defence R&D (DRDO / DLRL):</div>
      <div class="node-desc">Standardized, modular Python/PyTorch framework enables rapid algorithmic prototyping and seamless integration into existing EW suites.</div>
    </div>
  </div>

  <!-- Bottom: Fleet Managers -->
  <div class="node-card node-bottom">
    <div class="node-icon i-purple"><svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></div>
    <div>
      <div class="node-title" style="color:#9333ea;">Defence Fleet Managers:</div>
      <div class="node-desc">Software-only deployment brings cognitive capabilities to airborne (UAV/fighter), naval, and ground ESM platforms with minimal SWaP-C cost.</div>
    </div>
  </div>
</body>
</html>"""

Path("diagram_generator/s3_techstack.html").write_text(s3_tech, encoding="utf-8")
Path("diagram_generator/s5_banner.html").write_text(s5_banner, encoding="utf-8")
Path("diagram_generator/s5_stakeholders.html").write_text(s5_stakeholders, encoding="utf-8")
print("Templates updated.")

BROWSER = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not Path(BROWSER).exists():
    BROWSER = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

def render(html_name, png_name, w, h):
    html_abs = Path(f"diagram_generator/{html_name}").resolve()
    png_abs = Path(f"diagram_generator/{png_name}").resolve()
    cmd = [
        BROWSER,
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--window-size={w},{h}",
        f"--screenshot={png_abs}",
        html_abs.as_uri()
    ]
    subprocess.run(cmd, capture_output=True, text=True)
    print(f"Rendered {png_name}: {png_abs.exists()} ({png_abs.stat().st_size if png_abs.exists() else 0} bytes)")

render("s3_techstack.html", "s3_techstack.png", 3000, 360)
render("s5_banner.html", "s5_banner.png", 3000, 160)
render("s5_stakeholders.html", "s5_stakeholders.png", 2392, 1684)

