#!/usr/bin/env python3
"""metrics.py TARGET.png CAND.png OUTDIR [--label NAME]
Writes compare.jpg (target | candidate, full + native crops) and metrics.json.
Metrics are distributional (the data differ, so pixel alignment is meaningless):
  white_frac  fraction of near-white paper visible
  palette     share of pixels nearest each of 10 reference colors (8 bands + mixed orange + red-dark)
  sizes       radius histogram proxy: edge density per scale (texture energy at 3 blur scales)
  lowfreq     mean color of 8x8 block grid (large-scale cloud structure) distance (only distributional: sorted)
"""
import sys, json, os, numpy as np
from PIL import Image, ImageDraw, ImageFilter

REF = {"paper": (255, 255, 255), "pink": (245, 190, 190), "red": (215, 40, 25), "orange": (245, 120, 20), "yellow": (250, 200, 20),
       "green": (130, 200, 40), "cyan": (40, 180, 210), "blue": (30, 60, 170), "purple": (120, 90, 160), "magenta": (220, 30, 170)}

def palette(a):
    px = a.reshape(-1, 3)[::7].astype(float); ref = np.array(list(REF.values()), float)
    d = ((px[:, None, :] - ref[None]) ** 2).sum(2); idx = d.argmin(1)
    return {k: round(float((idx == i).mean()), 4) for i, k in enumerate(REF)}

def texture(img):
    g = np.asarray(img.convert("L"), float); out = {}
    for s in (1, 3, 8):
        b = np.asarray(img.convert("L").filter(ImageFilter.GaussianBlur(s)), float)
        b2 = np.asarray(img.convert("L").filter(ImageFilter.GaussianBlur(s * 2)), float)
        out[f"dog{s}"] = round(float(np.abs(b - b2).mean()), 3)
    return out

def lowfreq(img):
    s = img.resize((8, 24), Image.BILINEAR); a = np.asarray(s, float).reshape(-1, 3)
    return a

def main():
    t, c, od = sys.argv[1:4]; os.makedirs(od, exist_ok=True)
    T = Image.open(t).convert("RGB"); C = Image.open(c).convert("RGB")
    h = min(T.height, C.height); T = T.crop((0, 0, T.width, h)); C = C.resize((T.width, int(C.height * T.width / C.width))).crop((0, 0, T.width, h))
    ta, ca = np.asarray(T), np.asarray(C)
    m = {"target": {"palette": palette(ta), "texture": texture(T)}, "cand": {"palette": palette(ca), "texture": texture(C)}}
    pd = sum(abs(m["target"]["palette"][k] - m["cand"]["palette"][k]) for k in REF) / 2
    td = sum(abs(m["target"]["texture"][k] - m["cand"]["texture"][k]) / max(m["target"]["texture"][k], 1e-6) for k in m["target"]["texture"]) / 3
    lt, lc = lowfreq(T), lowfreq(C)
    # distributional large-scale match: compare sorted luminance + mean color of blocks
    lum = lambda a: np.sort(a @ np.array([.299, .587, .114]))
    ld = float(np.abs(lum(lt) - lum(lc)).mean() / 255)
    m["score"] = {"palette_tv": round(pd, 4), "texture_rel": round(td, 4), "lowfreq_lum": round(ld, 4), "total": round(pd + 0.5 * td + ld, 4)}
    json.dump(m, open(od + "/metrics.json", "w"), indent=1)
    # compare sheet: full frames scaled to 600 tall + 2 native 300px crops each
    sc = 1100 / h; ft, fc = T.resize((int(T.width * sc), 1100)), C.resize((int(T.width * sc), 1100))
    crops = [(60, 300), (int(T.width * .45), int(h * .55))]
    W = ft.width * 2 + 30 + 2 * (300 * 2 + 10) + 40; S = Image.new("RGB", (W, 1140), "white"); d = ImageDraw.Draw(S)
    S.paste(ft, (0, 30)); S.paste(fc, (ft.width + 30, 30)); d.text((4, 8), "TARGET (inspo)", fill="black"); d.text((ft.width + 34, 8), sys.argv[5] if len(sys.argv) > 5 else "CANDIDATE", fill="black")
    x = ft.width * 2 + 70
    for j, (cx, cy) in enumerate(crops):
        S.paste(T.crop((cx, cy, cx + 300, cy + 300)), (x, 30 + j * 330)); S.paste(C.crop((cx, cy, cx + 300, cy + 300)), (x + 310, 30 + j * 330))
        d.text((x, 14 + j * 330), "target native crop", fill="black"); d.text((x + 310, 14 + j * 330), "candidate native crop", fill="black")
    S.save(od + "/compare.jpg", quality=88)
    print(json.dumps(m["score"]), json.dumps(m["cand"]["palette"]))

if __name__ == "__main__":
    main()
