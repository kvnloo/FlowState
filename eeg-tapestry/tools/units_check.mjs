// compare browser bands.js vs python day.jsonl band profile on the same subjects (EEGMAT S00-S04)
import fs from "fs"; import vm from "vm";
const ctx = { window: {}, globalThis: {} }; ctx.globalThis = ctx; vm.createContext(ctx); vm.runInContext(fs.readFileSync("web/bands.js", "utf8"), ctx);
const EB = ctx.window.EEGBands || ctx.EEGBands; const raw = new Float32Array(fs.readFileSync("data/sim_raw.f32").buffer.slice(0)); const N = raw.length / 4;
const B = ["delta","theta","low_alpha","high_alpha","low_beta","high_beta","low_gamma","high_gamma"]; const acc = Object.fromEntries(B.map(b => [b, []]));
for (let s = 0; s < 900; s++) { const ch = [0,1,2,3].map(c => { const a = new Float32Array(256); for (let i = 0; i < 256; i++) a[i] = raw[(s * 256 + i) * 4 + c]; return a; }); const { bands } = EB.bandPowers(ch, 256); for (const b of B) acc[b].push(bands[b]); }
const med = a => a.slice().sort((x, y) => x - y)[a.length >> 1];
const js = Object.fromEntries(B.map(b => [b, med(acc[b])]));
const pyAll = JSON.parse(fs.readFileSync(process.argv[2], "utf8")); const py = Object.fromEntries(B.map(b => [b, med(pyAll.map(p => p[b]))]));
let worst = 0; for (let s = 0; s < 900; s++) for (const b of B) worst = Math.max(worst, Math.abs(acc[b][s] / pyAll[s][b] - 1)); console.log("max per-second relative error js vs scipy:", worst.toExponential(2));
for (const b of B) console.log(b.padEnd(11), (js[b] / js.delta).toExponential(2).padStart(10), (py[b] / py.delta).toExponential(2).padStart(10), "ratio js/py", ((js[b] / js.delta) / (py[b] / py.delta)).toFixed(2));
