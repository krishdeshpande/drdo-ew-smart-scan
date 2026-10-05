# Assets generator
import subprocess
import time
from pathlib import Path

def render_edge(html_path, out_png, w, h):
    browser = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    cmd = [
        browser, '--headless', '--disable-gpu', '--hide-scrollbars',
        f'--window-size={w},{h}', f'--screenshot={out_png}',
        Path(html_path).resolve().as_uri()
    ]
    subprocess.run(cmd, capture_output=True)
    time.sleep(0.8)
    print(f'Rendered {Path(out_png).name} ({Path(out_png).stat().st_size} bytes)')

print('make_assets.py base initialized')
