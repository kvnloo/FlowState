// node tools/bench.mjs REPS "arm=gl&cull=1" "arm=gl&cull=0" ...   -> interleaved, rotated arms; per-frame work p50/p95/max
import { chromium } from "playwright-core"; import fs from "fs";
const [reps, ...arms] = process.argv.slice(2); const extra = process.env.BENCH_EXTRA || "";
const exe = fs.readdirSync(process.env.HOME + "/Library/Caches/ms-playwright").filter(d => d.startsWith("chromium-")).map(d => process.env.HOME + `/Library/Caches/ms-playwright/${d}/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing`).find(fs.existsSync);
// BENCH_UNCAPPED=1: unlock vsync + frame-rate limit so raf intervals measure real frame throughput (headless raf is otherwise throttled to ~15 Hz).
// This is GPU/CPU capacity on this host, not proof of 120 Hz on a physical display.
const UNCAP = process.env.BENCH_UNCAPPED === "1" ? ["--disable-gpu-vsync", "--disable-frame-rate-limit"] : [];
const browser = await chromium.launch({ executablePath: exe, headless: true, args: ["--use-angle=metal", "--enable-gpu", "--ignore-gpu-blocklist", "--enable-gpu-rasterization", ...UNCAP] });
const res = {}; const N = +reps;
for (let r = 0; r < N; r++) for (let k = 0; k < arms.length; k++) { const arm = arms[(k + r) % arms.length];
  const page = await browser.newPage({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 2 });
  page.on("pageerror", e => console.error("pageerror", arm, e.message));
  await page.goto(`http://127.0.0.1:8765/web/app.html?bench=1&${arm}${extra}`); await page.waitForFunction(() => window.__bench, null, { timeout: 180000 });
  const b = await page.evaluate(() => window.__bench); await page.close(); (res[arm] ||= []).push(b); if (b.phases) console.error("phases [render, overlay, ovSync, glFence] f0-3:", JSON.stringify(b.phases));
  console.error(`rep ${r} ${arm.padEnd(28)} work p50 ${b.work.p50.toFixed(2)} p95 ${b.work.p95.toFixed(2)} max ${b.work.max.toFixed(2)} top ${JSON.stringify(b.work.top)} | raf p50 ${b.raf.p50.toFixed(1)} | overlay p50 ${b.overlay.p50.toFixed(2)} p95 ${b.overlay.p95.toFixed(2)} | tiles-phase p95 ${b.tilePhase ? b.tilePhase.p95.toFixed(2) : "-"} | fallback frames ${b.fallbackFrames ?? "-"} tiles ${b.tilesRendered ?? "-"}`); }
await browser.close();
const med = a => { const s = a.slice().sort((x, y) => x - y); return s[s.length >> 1]; };
const out = {}; for (const [arm, bs] of Object.entries(res)) out[arm] = { renderer: bs[0].renderer, size: bs[0].size, n: bs[0].n, p50: med(bs.map(b => b.work.p50)), p95: med(bs.map(b => b.work.p95)), max: med(bs.map(b => b.work.max)), p95_all: bs.map(b => +b.work.p95.toFixed(2)), raf_p50: med(bs.map(b => b.raf.p50)), raf_p95: med(bs.map(b => b.raf.p95)), fps_p50: +(1000 / med(bs.map(b => b.raf.p50))).toFixed(1), fps_p05: +(1000 / med(bs.map(b => b.raf.p95))).toFixed(1), uncapped: UNCAP.length > 0, fallbackFrames: med(bs.map(b => b.fallbackFrames || 0)) };
console.log(JSON.stringify(out, null, 1));
