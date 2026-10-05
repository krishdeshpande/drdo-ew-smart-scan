"""Hugging Face Turing Synthetic Radar Dataset Loader."""
import os, requests, numpy as np
from typing import Optional, List
from .turing_dataset import PulseDescriptorWord

try:
    import h5py
except ImportError:
    h5py = None

class HuggingFaceTuringLoader:
    HF_BASE_URL = "https://huggingface.co/datasets/alan-turing-institute/turing-synthetic-radar-dataset/resolve/main"

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("HF_TOKEN")

    def download_sample(self, filename: str = "archive/test/test_0.h5", dest_dir: str = "data") -> str:
        os.makedirs(dest_dir, exist_ok=True)
        local_path = os.path.join(dest_dir, os.path.basename(filename))
        if os.path.exists(local_path) and os.path.getsize(local_path) > 1000:
            print(f"[HF LOADER] Found cached file: {local_path}")
            return local_path

        headers = {"User-Agent": "DRDO-EW/1.0"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        else:
            print("[HF LOADER] Note: Dataset is gated on Hugging Face. Supply token via --token.")

        url = f"{self.HF_BASE_URL}/{filename}"
        print(f"[HF LOADER] Fetching: {url} ...")
        resp = requests.get(url, headers=headers, stream=True, timeout=30)
        if resp.status_code == 401:
            raise PermissionError("Hugging Face returned 401 Unauthorized. Accept terms on HF and pass --token.")
        elif resp.status_code != 200:
            raise RuntimeError(f"Download failed: HTTP {resp.status_code}")

        with open(local_path, "wb") as f:
            for c in resp.iter_content(65536):
                if c: f.write(c)
        print(f"[HF LOADER] Downloaded: {local_path}")
        return local_path

    def load_h5_file(self, h5_filepath: str, max_pulses: int = 20000, num_bands: int = 8) -> List[PulseDescriptorWord]:
        if h5py is None:
            raise ImportError("h5py is required. Run: pip install h5py")
        pdws = []
        with h5py.File(h5_filepath, "r") as hf:
            keys = list(hf.keys())
            data = hf["pulses"][:] if "pulses" in hf else hf[keys[0]][:]
            labels = hf["labels"][:] if "labels" in hf else None
            n = min(len(data), max_pulses)
            min_f = float(np.min(data[:n, 1]))
            max_f = float(np.max(data[:n, 1]))
            span = max(1.0, max_f - min_f)
            for i in range(n):
                row = data[i]
                toa = float(row[0]) / 1e6 if row[0] > 1000 else float(row[0])
                freq = float(row[1])
                pw = float(row[2]) / 1e6 if row[2] > 0.001 else float(row[2])
                aoa = float(row[3]) % 360.0
                amp = float(row[4])
                snr = max(2.0, amp - (-95.0))
                b = int(min(num_bands - 1, max(0, int(((freq - min_f) / span) * num_bands))))
                lbl = f"TURING_EMITTER_{int(labels[i])}" if labels is not None else f"EMITTER_B{b}"
                pdws.append(PulseDescriptorWord(i+1, lbl, "SURV" if b==2 else "AGILE", toa, pw, freq, b, 0.001, amp, snr, aoa, "CIRCULAR", "PULSED_LFM"))
        print(f"[HF LOADER] Loaded {len(pdws)} pulses from {h5_filepath}")
        return pdws
