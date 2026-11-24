// node tools/sim_jsonl.mjs N OUT.jsonl -> first N seconds of data/sim_raw.f32 through web/bands.js (the live path, no faults)
import fs from "fs"; globalThis.window = globalThis; eval(fs.readFileSync("web/bands.js", "utf8"));
const raw = new Float32Array(fs.readFileSync("data/sim_raw.f32").buffer.slice(0)); const N = +process.argv[2]; const o = [];
for (let s = 0; s < N; s++) { const ch = [0,1,2,3].map(c => { const a = new Float32Array(256); for (let i = 0; i < 256; i++) a[i] = raw[(s * 256 + i) * 4 + c]; return a; }); o.push(JSON.stringify({ t: s, bands: EEGBands.bandPowers(ch, 256).bands })); }
fs.writeFileSync(process.argv[3], o.join("\n") + "\n");
