#!/usr/bin/env python3
"""Build data/sim_raw.f32: real EEGMAT raw EEG (T5,F7,F8,T6 ~ Muse TP9,AF7,AF8,TP10) resampled 500->256 Hz,
interleaved float32 [t][4], plus data/sim_raw.json metadata. TEST SOURCE ONLY (labelled 'simulated Muse' in the app).
Faults are injected in the browser sim, not baked in here."""
import json, os, sys, numpy as np
from scipy.signal import resample_poly
sys.path.insert(0, os.path.dirname(__file__))
from edf_bands import channel
D = sys.argv[1] if len(sys.argv) > 1 else "data/eegmat"; OUT = sys.argv[2] if len(sys.argv) > 2 else "data/sim_raw"
CH = ["EEG T5", "EEG F7", "EEG F8", "EEG T6"]; segs = []
for s in ["Subject00", "Subject01", "Subject02", "Subject03", "Subject04"]:
    for k in (1, 2):
        xs = [channel(f"{D}/{s}_{k}.edf", c)[0] for c in CH]
        y = np.stack([resample_poly(x, 64, 125) for x in xs], 1)  # 500 * 64/125 = 256 Hz
        segs.append(y[256:-256])
a = np.concatenate(segs).astype(np.float32); a -= np.median(a, 0)
a.tofile(OUT + ".f32"); json.dump({"fs": 256, "channels": ["TP9", "AF7", "AF8", "TP10"], "seconds": len(a) // 256, "source": "PhysioNet EEGMAT subjects 00-04, T5/F7/F8/T6 resampled"}, open(OUT + ".json", "w"))
print(a.shape, len(a) // 256, "s", round(float(np.std(a)), 2), "uV std")
