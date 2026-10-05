# Full diagrams generator
import subprocess
import time
from pathlib import Path

def render(html_path, out_png, w, h):
    browser = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    html_abs = Path(html_path).resolve()
    out_abs = Path(out_png).resolve()
    cmd = [
        browser, '--headless', '--disable-gpu', '--hide-scrollbars',
        f'--window-size={w},{h}', f'--screenshot={out_abs}',
        html_abs.as_uri()
    ]
    subprocess.run(cmd, capture_output=True)
    time.sleep(0.8)
    if out_abs.exists():
        print(f'SUCCESS: {out_abs.name} ({out_abs.stat().st_size} bytes)')
    else:
        print(f'FAILED: {out_abs.name}')

print('Ready to write generators')
