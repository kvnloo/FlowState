#!/usr/bin/env python3
"""PhysioNet EEGMAT (rest 180 s + mental arithmetic 60 s per subject) -> per-second band powers, Muse-like montage.

Usage: eegmat_bands.py DATA_DIR OUT.jsonl [--subjects N] [--cycles K]
Muse S electrodes are TP9, AF7, AF8, TP10; the nearest 10-20 sites here are T5, F7, F8, T6 (averaged power).
Subjects are stitched rest/task/rest/task. Each subject's log band power is re-centred on its own rest median and
shifted to the pooled rest median, so the stitched recording behaves like one person (level jumps between
subjects removed, rest->task contrast kept). This is a disclosed transform, not raw data.
"""
import argparse, json, os, sys, numpy as np
from scipy.signal import welch
sys.path.insert(0, os.path.dirname(__file__))
from edf_bands import BANDS, channel

CH = ["EEG T5", "EEG F7", "EEG F8", "EEG T6"]

def per_second(path):
    xs = [channel(path, c) for c in CH]; fs = xs[0][1]; n = int(len(xs[0][0]) / fs); out = []
    for k in range(1, n - 1):  # drop first/last second (edge artefacts)
        b = {nm: 0.0 for nm in BANDS}
        for x, _ in xs:
            seg = x[int(k * fs): int((k + 1) * fs)]; f, p = welch(seg, fs=fs, nperseg=len(seg))
            for nm, (lo, hi) in BANDS.items():
                m = (f >= lo) & (f <= hi); b[nm] += float(np.trapezoid(p[m], f[m])) / len(xs)
        out.append(b)
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("dir"); ap.add_argument("out")
    ap.add_argument("--subjects", type=int, default=36); a = ap.parse_args()
    info = [l.split(",") for l in open(os.path.join(a.dir, "subject-info.csv")).read().strip().split("\n")[1:]]
    subs = []
    for row in info[: a.subjects]:
        s = row[0]; rest = per_second(os.path.join(a.dir, f"{s}_1.edf")); task = per_second(os.path.join(a.dir, f"{s}_2.edf"))
        subs.append((s, row, rest, task)); print(s, len(rest), len(task), "good counter" if row[5] == "1" else "bad counter", flush=True)
    L = lambda rows, nm: np.log10([max(r[nm], 1e-9) for r in rows])
    pooled = {nm: float(np.median(np.concatenate([L(r, nm) for _, _, r, _ in subs]))) for nm in BANDS}
    t = 0
    with open(a.out, "w") as fo:
        for s, row, rest, task in subs:
            off = {nm: pooled[nm] - float(np.median(L(rest, nm))) for nm in BANDS}
            for label, rows in (("rest", rest), ("arithmetic", task)):
                for r in rows:
                    bands = {nm: float(10 ** (np.log10(max(r[nm], 1e-9)) + off[nm])) for nm in BANDS}
                    fo.write(json.dumps({"t": t, "stage": label, "subject": s, "bands": bands}) + "\n"); t += 1
    print("wrote", t, "s =", round(t / 3600, 2), "h ->", a.out)

if __name__ == "__main__":
    main()
