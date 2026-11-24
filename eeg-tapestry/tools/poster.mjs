// node tools/poster.mjs OUT.png OPTS.json DATA.jsonl [TAGS.json] [--title "Recording during the day"] [--start 15:38:01]
// Full poster like measurement_large3: field (left) + notes column (right) + footer.
import { createCanvas } from "@napi-rs/canvas"; import fs from "fs"; import path from "path"; import url from "url";
const B = path.resolve(path.dirname(url.fileURLToPath(import.meta.url)), "..");
globalThis.window = globalThis; eval(fs.readFileSync(B + "/web/tapestry.js", "utf8"));
const args = process.argv.slice(2); const flag = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const [out, optsF, dataF, tagsF] = args.filter((a, i) => !a.startsWith("--") && !(i > 0 && args[i - 1].startsWith("--")));
const opts = JSON.parse(fs.readFileSync(optsF, "utf8")); const pts = fs.readFileSync(dataF, "utf8").trim().split("\n").map(JSON.parse);
const tags = tagsF && fs.existsSync(tagsF) ? JSON.parse(fs.readFileSync(tagsF, "utf8")) : [];
const start = flag("--start", "15:38:01").split(":").map(Number), s0 = start[0] * 3600 + start[1] * 60 + start[2];
const fmt = i => { const t = (s0 + i) % 86400; return [Math.floor(t / 3600), Math.floor(t / 60) % 60, t % 60].map(v => String(v).padStart(2, "0")).join(":"); };
const field = createCanvas(10, 10); field.style = {}; const r = Tapestry.render(field, pts, opts);
const notesW = 360, pad = 40, footer = 70, W = r.W + notesW + pad * 2, H = r.H + pad + footer;
const c = createCanvas(W, H), ctx = c.getContext("2d"); ctx.fillStyle = "#fff"; ctx.fillRect(0, 0, W, H);
ctx.drawImage(field, pad, pad);
ctx.save(); ctx.translate(pad, pad); Tapestry.drawNotes(ctx, Tapestry.annotate(pts, opts, tags), pts, opts, r.W + 24, notesW - 24, fmt); ctx.restore();
ctx.fillStyle = "#222"; ctx.font = "bold 13px Helvetica, Arial, sans-serif"; ctx.fillText(`${flag("--title", "Recording during the day")}  ${fmt(0)} – ${fmt(pts.length)}`, pad, r.H + pad + 26);
ctx.font = "11px Helvetica, Arial, sans-serif"; ctx.fillStyle = "#666"; ctx.fillText("1 point = 1 s = 8 circles · 1 row = 60 s · circle size = band power vs this session", pad, r.H + pad + 46);
fs.writeFileSync(out, c.toBuffer("image/png")); console.log(out, W + "x" + H, Tapestry.annotate(pts, opts, tags).length, "notes");
