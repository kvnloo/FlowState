# EEG tapestry

A live EEG visualization: a large canvas of overlapping translucent concentric circles, one point per second and
one row per minute, drawn from 8 brainwave bands (delta, theta, low/high alpha, low/high beta, low/high gamma).
It renders recorded EEG (EDF), a simulated source, or a live Muse headband over Web Bluetooth.

## Run
The replay view reads `data/day.jsonl`, which is generated, not committed. Build it from the public
[PhysioNet EEGMAT](https://physionet.org/content/eegmat/1.0.0/) recordings listed in `data/eegmat/RECORDS`
(check them against `data/eegmat/SHA256SUMS`):
```
python3 tools/eegmat_bands.py data/eegmat data/day.jsonl     # needs numpy + scipy
python3 -m http.server 8765                                  # from this folder; any static server works
open http://127.0.0.1:8765/web/app.html     # replay of data/day.jsonl, or the simulated Muse source
open http://127.0.0.1:8765/web/live.html    # live Muse S (Chrome/Edge, Web Bluetooth)
```
`data/sim_raw.f32` is the simulated Muse source (real EEGMAT EEG resampled to Muse rate, built by
`tools/make_sim_raw.py`). `tools/edf_bands.py` converts any EDF recording into per-second band powers.
`npm install` is only needed for the screenshot and benchmark tools in `tools/*.mjs`.

## Earlier attempts in this repo, and why they missed the look
`forensics/harness/` re-renders the 2024-2025 attempts (this repo's commits 81712ead..52fc8109, a0fee7b6, 6eaa16a0,
e5ee0908, plus early prototypes). What they got wrong:
1. Radius capped at about one cell, so the large delta/theta clouds (5-20+ cells wide) could never form.
2. Size transfer flattened the natural 1/f ratio between bands (clamps, per-band normalisation, random sizes).
3. Opacity and blend drift (opaque circles, `screen`, which is invisible on white). The look is plain source-over at
   20/40/50% on white; colour comes from how many discs stack.
4. A painted gradient background instead of one that emerges from many 20% delta discs.
5. Band order broken (inverted, sorted by value, rotated palettes).
6. Fake or flat data with no minutes-long slow-wave structure.
7. Per-point layering covering earlier halos; per-band passes (all delta, then theta, ...) keep clouds continuous.
8. Specs written from prose instead of measured from the reference image, with no side-by-side check.
