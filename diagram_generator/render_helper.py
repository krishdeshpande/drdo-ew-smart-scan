import sys
import subprocess
import time
from pathlib import Path

def render_html_to_png(html_path, output_png_path, width, height):
    html_path = Path(html_path).resolve()
    output_png_path = Path(output_png_path).resolve()
    
    edge_paths = [
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
    ]
    
    browser = None
    for p in edge_paths:
        if Path(p).exists():
            browser = p
            break
            
    if not browser:
        raise RuntimeError('No browser found for rendering')
        
    cmd = [
        browser,
        '--headless',
        '--disable-gpu',
        '--hide-scrollbars',
        f'--window-size={width},{height}',
        f'--screenshot={output_png_path}',
        html_path.as_uri()
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    time.sleep(1)
    if not output_png_path.exists():
        print('Render stderr:', res.stderr)
        raise RuntimeError(f'Failed to generate {output_png_path}')
    print(f'Rendered {output_png_path.name} ({output_png_path.stat().st_size} bytes)')

if __name__ == '__main__':
    if len(sys.argv) >= 5:
        render_html_to_png(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
