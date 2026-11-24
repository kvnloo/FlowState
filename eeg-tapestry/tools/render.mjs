// node tools/render.mjs OUT.png '<json opts>' [data.jsonl]  -> renders web/tapestry.js with Skia canvas
import { createCanvas } from "@napi-rs/canvas"; import fs from "fs"; import path from "path"; import url from "url";
const B = path.resolve(path.dirname(url.fileURLToPath(import.meta.url)), "..");
globalThis.window = globalThis; eval(fs.readFileSync(B + "/web/tapestry.js", "utf8"));
const [out, optsJ = "{}", dataF = B + "/data/sleep3h.jsonl"] = process.argv.slice(2);
const pts = fs.readFileSync(dataF, "utf8").trim().split("\n").map(JSON.parse);
const c = createCanvas(10, 10); c.style = {};
const t0 = performance.now(); const r = Tapestry.render(c, pts, JSON.parse(optsJ));
fs.writeFileSync(out, c.toBuffer("image/png")); console.log(out, r.W + "x" + r.H, Math.round(performance.now() - t0) + "ms");
