// node tools/engine_parity.mjs PARAMS DATA [chunk]  -> incremental engine vs batch reference geometry, at several lengths
import fs from "fs"; globalThis.window = globalThis;
for (const f of ["tapestry.js", "engine.js"]) eval(fs.readFileSync(new URL("../web/" + f, import.meta.url), "utf8"));
const [pf, df, ch = "1"] = process.argv.slice(2); const o = JSON.parse(fs.readFileSync(pf, "utf8"));
const pts = fs.readFileSync(df, "utf8").trim().split("\n").map(JSON.parse); const chunk = +ch;
const E = TapestryEngine.Engine(o); let worst = 0, checks = 0, pushMs = [], i = 0;
const at = [250, 300, 301, 359, 360, 1000, 1799, 1800, 1801, 4321, pts.length];
while (i < pts.length) { const k = Math.min(chunk, pts.length - i); const t = performance.now(); E.push(pts.slice(i, i + k)); pushMs.push(performance.now() - t); i += k;
  if (at.some(a => a > i - k && a <= i)) { const g = Tapestry.geometry(pts.slice(0, i), o); let mx = 0, cnt = 0, cntE = 0;
    g.bands.forEach((a, b) => { cnt += a.length / 4; for (let j = 0; j < a.length; j += 4) { const idx = a[j]; mx = Math.max(mx, Math.abs(E.R[idx * 8 + b] - a[j + 3])); } for (let j = 0; j < i; j++) if (E.R[j * 8 + b] >= 0.3) cntE++; });
    const gr = E.giantRings(); const same = gr.length === g.giants.length && gr.every((v, j) => Math.abs(v - g.giants[j]) < 1e-3);
    console.log(`n=${i} maxAbsRadiusDiff=${mx.toExponential(2)} drawn ${cntE}/${cnt} giants ${gr.length / 5}/${g.giants.length / 5} ${same ? "same" : "DIFF"}`); worst = Math.max(worst, same ? mx : 1, cntE === cnt ? 0 : 1); checks++; } }
pushMs.sort((a, b) => a - b); const p = q => pushMs[Math.floor(q * (pushMs.length - 1))].toFixed(3);
console.log(`checks ${checks} worst ${worst.toExponential(2)} | push(${chunk}) ms p50 ${p(.5)} p99 ${p(.99)} max ${p(1)}`);
process.exit(worst < 1e-3 ? 0 : 1);
