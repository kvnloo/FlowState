// node tools/notes_check.mjs OPTS DATA  -> how auto notes line up with ground-truth stages
import fs from "fs"; globalThis.window = globalThis; eval(fs.readFileSync(new URL("../web/tapestry.js", import.meta.url), "utf8"));
const [o, d] = process.argv.slice(2); const opts = JSON.parse(fs.readFileSync(o, "utf8")); const pts = fs.readFileSync(d, "utf8").trim().split("\n").map(JSON.parse);
const notes = Tapestry.annotate(pts, opts, []).filter(n => n.i1 > n.i0 + 1);
const byTitle = {}; for (const n of notes) { const st = {}; for (let i = n.i0; i < n.i1; i++) st[pts[i].stage] = (st[pts[i].stage] || 0) + 1; const t = byTitle[n.title] ||= { n: 0, secs: 0, arith: 0 }; t.n++; t.secs += n.i1 - n.i0; t.arith += st.arithmetic || 0; }
const base = pts.filter(p => p.stage === "arithmetic").length / pts.length;
for (const [k, v] of Object.entries(byTitle)) console.log(k.padEnd(30), "notes", v.n, "minutes", v.secs / 60, "share arithmetic", (v.arith / v.secs).toFixed(2), "(base rate", base.toFixed(2) + ")");
