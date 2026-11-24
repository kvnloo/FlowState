#!/usr/bin/env python3
"""Coordinate-descent hill climb over renderer params against metrics.py score.
climb.py START.json ROUNDDIR [--iters N]
Every evaluated candidate is kept (render + metrics) in ROUNDDIR/evals/NNN; ledger.jsonl records all.
"""
import json, subprocess, sys, os, copy, random
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = B + "/.venv313/bin/python"
TARGET = os.environ.get("TAPESTRY_TARGET", B + "/loop/target_field.png")
DATA = os.environ.get("TAPESTRY_DATA", B + "/data/sleep3h.jsonl")
BANDS = ["delta", "theta", "low_alpha", "high_alpha", "low_beta", "high_beta", "low_gamma", "high_gamma"]

def evaluate(opts, d):
    os.makedirs(d, exist_ok=True); json.dump(opts, open(d + "/opts.json", "w"))
    subprocess.run(["node", B + "/tools/render.mjs", d + "/cand.png", json.dumps(opts), DATA], check=True, capture_output=True)
    out = subprocess.run([PY, B + "/tools/metrics.py", TARGET, d + "/cand.png", d, "x", os.path.basename(d)], check=True, capture_output=True, text=True).stdout
    return json.load(open(d + "/metrics.json"))["score"]["total"]

def move_specs():
    # (name, fn(o)->new o). Applied to the CURRENT best each time (a kept move is never overwritten).
    for b in BANDS:
        for f in (0.75, 1.3):
            def m(o, b=b, f=f):
                n = copy.deepcopy(o); n["rmax"][b] = round(n["rmax"][b] * f, 3); return n
            yield f"rmax.{b}*{f}", m
        for dv in (-0.6, 0.6):
            def m(o, b=b, dv=dv):
                n = copy.deepcopy(o); gb = n.setdefault("gammaB", {}); gb[b] = round(max(0.6, gb.get(b, n.get("gamma", 1.6)) + dv), 2); return n
            yield f"gamma.{b}{dv:+}", m
    for b in ("low_beta", "high_beta", "low_gamma", "high_gamma"):
        for tau in (0, 4, 12):
            def m(o, b=b, tau=tau):
                n = copy.deepcopy(o); n.setdefault("smooth", {})[b] = tau; return n
            yield f"smooth.{b}={tau}", m
    for b in ("delta", "theta", "low_alpha"):
        for f in (0.5, 2.0, 4.0):
            def m(o, b=b, f=f):
                n = copy.deepcopy(o); n["floor"][b] = round(min(n["rmax"][b] * 0.8, n["floor"][b] * f), 3); return n
            yield f"floor.{b}*{f}", m
    for g in (8, 16, 24):
        def m(o, g=g):
            n = copy.deepcopy(o); n["giant"] = g; return n
        yield f"giant={g}", m
    for ga in (1.6, 2.2, 3.0):
        def m(o, ga=ga):
            n = copy.deepcopy(o); n["giantAt"] = ga; return n
        yield f"giantAt={ga}", m
    for b in ("low_beta", "high_beta", "low_gamma", "high_gamma"):
        for v in (1.0, 2.0):
            def m(o, b=b, v=v):
                n = copy.deepcopy(o); n.setdefault("burstB", {})[b] = v; return n
            yield f"burst.{b}={v}", m
    for k, vals in (("burst", (2.0, 4.0)), ("qhi", (0.98, 0.999)), ("qlo", (0.005, 0.1)), ("mix", (0.25, 0.5, 0.75))):
        for v in vals:
            def m(o, k=k, v=v):
                n = copy.deepcopy(o); n[k] = v; return n
            yield f"{k}={v}", m

def moves(o):
    raise RuntimeError("use move_specs")

def main():
    start, rd = sys.argv[1], sys.argv[2]; iters = int(sys.argv[sys.argv.index("--iters") + 1]) if "--iters" in sys.argv else 3
    o = json.load(open(start)); n = 0; led = open(rd + "/ledger.jsonl", "a")
    best = evaluate(o, f"{rd}/evals/{n:03d}"); led.write(json.dumps({"n": n, "move": "start", "score": best, "kept": True}) + "\n"); n += 1
    for it in range(iters):
        improved = False
        for name, fn in move_specs():
            cand = fn(o); s = evaluate(cand, f"{rd}/evals/{n:03d}"); kept = s < best - 0.003
            led.write(json.dumps({"n": n, "iter": it, "move": name, "score": s, "kept": kept}) + "\n"); led.flush(); n += 1
            if kept: o, best, improved = cand, s, True; print(f"[{n}] keep {name} -> {s:.4f}", flush=True)
        if not improved: break
    json.dump(o, open(rd + "/best.json", "w"), indent=1); print("best", best, json.dumps(o))

if __name__ == "__main__":
    main()
