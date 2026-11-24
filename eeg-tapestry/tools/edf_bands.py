#!/usr/bin/env python3
"""EDF -> per-second NeuroSky-style band powers (JSON lines).

Usage: edf_bands.py PSG.edf HYPNO.edf OUT.jsonl [--channel "EEG Fpz-Cz"] [--start-stage W] [--hours 3]
Minimal EDF/EDF+ reader (no deps besides numpy/scipy).
"""
import argparse, json, numpy as np
from scipy.signal import welch

BANDS = {  # NeuroSky eSense band edges (Hz)
    "delta": (0.5, 2.75), "theta": (3.5, 6.75), "low_alpha": (7.5, 9.25), "high_alpha": (10, 11.75),
    "low_beta": (13, 16.75), "high_beta": (18, 29.75), "low_gamma": (31, 39.75), "high_gamma": (41, 49.75),
}

def read_edf(path):
    f = open(path, "rb"); h = f.read(256)
    nrec, dur, ns = int(h[236:244]), float(h[244:252]), int(h[252:256])
    sh = f.read(256 * ns)
    fld = lambda off, w: [sh[off + i * w: off + (i + 1) * w].decode("latin1").strip() for i in range(ns)]
    o = 0
    labels = fld(o, 16); o += 16 * ns
    o += 80 * ns + 8 * ns  # transducer, phys dim
    pmin = list(map(float, fld(o, 8))); o += 8 * ns
    pmax = list(map(float, fld(o, 8))); o += 8 * ns
    dmin = list(map(float, fld(o, 8))); o += 8 * ns
    dmax = list(map(float, fld(o, 8))); o += 8 * ns
    o += 80 * ns
    nsamp = list(map(int, fld(o, 8)))
    raw = f.read()
    return labels, nsamp, dur, nrec, pmin, pmax, dmin, dmax, raw

def channel(path, name):
    labels, nsamp, dur, nrec, pmin, pmax, dmin, dmax, raw = read_edf(path)
    i = labels.index(name); rec = sum(nsamp)
    a = np.frombuffer(raw[: rec * nrec * 2], dtype="<i2").reshape(nrec, rec)
    off = sum(nsamp[:i]); x = a[:, off: off + nsamp[i]].reshape(-1).astype(np.float64)
    g = (pmax[i] - pmin[i]) / (dmax[i] - dmin[i]); x = (x - dmin[i]) * g + pmin[i]
    return x, nsamp[i] / dur

def hypnogram(path):
    labels, nsamp, dur, nrec, *_ , raw = read_edf(path)
    txt = raw.decode("latin1"); out = []
    for tal in txt.split("\x00"):
        parts = tal.split("\x14")
        if len(parts) >= 3 and "\x15" in parts[0] and parts[1].startswith("Sleep stage"):
            on, d = parts[0].split("\x15"); out.append((float(on), float(d), parts[1].replace("Sleep stage ", "")))
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("psg"); ap.add_argument("hyp"); ap.add_argument("out")
    ap.add_argument("--channel", default="EEG Fpz-Cz"); ap.add_argument("--hours", type=float, default=3)
    ap.add_argument("--lead-min", type=float, default=10, help="minutes of wake before first sleep")
    ap.add_argument("--win", type=float, default=2.0, help="analysis window seconds (1 = independent per-second values)")
    a = ap.parse_args()
    x, fs = channel(a.psg, a.channel); stages = hypnogram(a.hyp)
    first_sleep = next(on for on, d, s in stages if s not in ("W", "?", "Movement time"))
    t0 = max(0, first_sleep - a.lead_min * 60); n = int(a.hours * 3600)
    def stage_at(t):
        for on, d, s in stages:
            if on <= t < on + d: return s
        return "?"
    win = int(a.win * fs)
    with open(a.out, "w") as fo:
        for k in range(n):
            s = int((t0 + k) * fs); seg = x[s: s + win] if a.win <= 1 else x[s - win // 2: s + win // 2]
            if len(seg) < win: break
            f, p = welch(seg, fs=fs, nperseg=win)
            b = {nm: float(np.trapezoid(p[(f >= lo) & (f <= hi)], f[(f >= lo) & (f <= hi)]) or 1e-9) for nm, (lo, hi) in BANDS.items()}
            fo.write(json.dumps({"t": round(t0 + k, 1), "stage": stage_at(t0 + k), "bands": b}) + "\n")
    print(f"fs={fs} t0={t0} first_sleep={first_sleep} wrote {k+1} s -> {a.out}")

if __name__ == "__main__":
    main()
