import json, sys, numpy as np, os
from scipy.signal import welch
sys.path.insert(0, os.path.dirname(__file__)); from edf_bands import BANDS
a = np.fromfile("data/sim_raw.f32", dtype=np.float32).reshape(-1, 4); out = []
for s in range(900):
    b = {nm: 0.0 for nm in BANDS}
    for c in range(4):
        seg = a[s*256:(s+1)*256, c].astype(np.float64); f, p = welch(seg, fs=256, nperseg=256)
        for nm, (lo, hi) in BANDS.items():
            m = (f >= lo) & (f <= hi); b[nm] += float(np.trapezoid(p[m], f[m])) / 4
    out.append(b)
json.dump(out, open(sys.argv[1], "w"))
