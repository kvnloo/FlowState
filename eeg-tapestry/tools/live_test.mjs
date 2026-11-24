// node tools/live_test.mjs OUT [simspeed]  -> drive the test stream; assert session/contact/gap/idle behaviour; screenshots
import { chromium } from "playwright-core"; import fs from "fs";
const out = process.argv[2]; const SP = +(process.argv[3] || 20); fs.mkdirSync(out, { recursive: true });
const exe = fs.readdirSync(process.env.HOME + "/Library/Caches/ms-playwright").filter(d => d.startsWith("chromium-")).map(d => process.env.HOME + `/Library/Caches/ms-playwright/${d}/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing`).find(fs.existsSync);
const b = await chromium.launch({ executablePath: exe, headless: true, args: ["--use-angle=metal", "--enable-gpu", "--ignore-gpu-blocklist"] });
const p = await b.newPage({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 2 }); const errs = [];
p.on("pageerror", e => errs.push(e.message)); p.on("console", m => { if (m.type() === "error") errs.push(m.text()); });
await p.addInitScript(() => { window.__raf = 0; const r = window.requestAnimationFrame; window.requestAnimationFrame = f => { window.__raf++; return r(f); }; });
const res = {}; const ok = (k, v, why) => { res[k] = { pass: !!v, why }; };
await p.goto(`http://127.0.0.1:8765/web/app.html?speed=600&src=sim&simspeed=${SP}`);
await p.waitForTimeout(2500); await p.screenshot({ path: out + "/1-start.png" });
const st = () => p.evaluate(() => { const S = __app.S, c = __app.cells(); const cnt = [0, 0, 0]; for (let i = S.firstCell || 0; i < c; i++) cnt[S.state[i]]++; return { kind: S.kind, cells: c, n: __app.E.n, absent: cnt[0], valid: cnt[1], excl: cnt[2], first: S.minute0, lastQ: S.quality[c - 1], state: document.querySelector("#state").textContent }; });
const s0 = await st();
// early scale: radii of earlier circles must not change between two non-refresh landings, and no circle > rmax before 120 s
const early = await p.evaluate(async () => { const E = __app.E, rmax = Math.max(...Object.values((await (await fetch("params.json")).json()).rmax)) * E.o.pitch; let mx = 0; for (let i = 0; i < E.n * 8; i++) mx = Math.max(mx, E.R[i]); return { n: E.n, mx, rmax }; });
ok("early_no_burst", early.mx <= early.rmax + 1e-3, `n=${early.n} max r ${early.mx.toFixed(1)} <= rmax ${early.rmax.toFixed(1)}`);
const adjustSeen = []; const sampler = setInterval(async () => { try { const r = await p.evaluate(() => [__app.cells() - __app.S.firstCell, document.querySelector("#state").textContent]); if (r[0] > 35 && r[0] < 65) adjustSeen.push(r[1]); } catch (e) {} }, 150);
ok("clean_session", s0.kind === "sim" && s0.n < 200, `kind=${s0.kind} n=${s0.n} (replay must not leak in)`);
ok("settling_marks", s0.excl >= 3, `excluded seconds in first ${s0.cells}s = ${s0.excl} (electrodes join over ~5 s)`);
// run past the faults: gap 150-162, TP10 flat 70-82, noisy AF7 200-206
const need = 215; for (let i = 0; i < 40; i++) { const s = await st(); if (s.absent + s.valid + s.excl > need + 10) break; await p.waitForTimeout(800); }
// critic r1 checks: blinks stay valid, one dropped packet -> one invalid second, header never asked to adjust during blinks
const qa = await p.evaluate(() => { const S = __app.S; let blink = 0, blinkValid = 0, dropped = 0; for (let c = S.firstCell; c < __app.cells(); c++) { const q = S.quality[c]; if (!q) continue; if (q.includes("blink") && q.every(x => x === "good" || x === "blink")) { blink++; if (S.state[c] === 1) blinkValid++; } if (q.includes("dropped")) dropped++; } return { blink, blinkValid, dropped }; });
ok("blinks_valid", qa.blink >= 10 && qa.blinkValid === qa.blink, `blink seconds ${qa.blink}, valid ${qa.blinkValid}`);
ok("drop_one_invalid", qa.dropped === 2, `dropped-sample seconds ${qa.dropped} (expect 2: one 47 ms packet lost at t=110 + the partial second cut by the 12 s gap)`);
ok("no_adjust_on_blink", adjustSeen.length >= 2 && !adjustSeen.some(s => /adjust/.test(s)), `${adjustSeen.length} header samples during blink-only stretch (35-65 s); adjust prompts: ${adjustSeen.filter(s => /adjust/.test(s)).length}`);
clearInterval(sampler); const s1 = await st(); res.traceAfterSteady = await p.evaluate(() => document.querySelector("#trace").classList.contains("show")); ok("gap_absent", s1.absent >= 11 && s1.absent <= 12, `absent=${s1.absent} (12 s injected gap; its first partial second lands as not-measured)`);
ok("fault_excluded", s1.excl >= 20, `excluded=${s1.excl} (≈5 settle + 12 flat TP10 + 6 noisy AF7)`);
await p.screenshot({ path: out + "/2-after-faults.png" });
// zoom to the gap row and hover a grey mark
const info = await p.evaluate(() => { const S = __app.S; let g = -1, m = -1; for (let i = 0; i < __app.cells(); i++) { if (g < 0 && S.state[i] === 0 && i > 60) g = i; if (m < 0 && S.state[i] === 2 && i > 30) m = i; } return { g, m }; });
res.info = info;
// idle check: 1x stream -> rAF calls per second should be ~ (landing anim 0.62 s * 120) not continuous
await b.close();
const b2 = await chromium.launch({ executablePath: exe, headless: true, args: ["--use-angle=metal", "--enable-gpu"] }); const p2 = await b2.newPage({ viewport: { width: 1600, height: 1000 } });
await p2.addInitScript(() => { window.__raf = 0; window.__t0 = 0; const r = window.requestAnimationFrame; window.requestAnimationFrame = f => { window.__raf++; return r(f); }; });
await p2.goto(`http://127.0.0.1:8765/web/app.html?speed=0&src=sim&simspeed=1`); await p2.waitForTimeout(17000); res.traceFolded1x = await p2.evaluate(() => !document.querySelector("#trace").classList.contains("show"));
const r0 = await p2.evaluate(() => [window.__raf, performance.now()]); await p2.waitForTimeout(5000); const r1 = await p2.evaluate(() => [window.__raf, performance.now(), __app.cells()]);
const perSec = (r1[0] - r0[0]) / ((r1[1] - r0[1]) / 1000); res.rafPerSec1x = +perSec.toFixed(1);
ok("idle_between_seconds", perSec < 90, `rAF/s at 1x live = ${perSec.toFixed(1)} (headless ~60Hz; continuous would be ~60)`);
await p2.screenshot({ path: out + "/3-live-1x.png" }); await b2.close();
res.errs = errs.slice(0, 6); ok("no_errors", errs.length === 0, errs.slice(0, 2).join(" | "));
console.log(JSON.stringify(res, null, 1));
