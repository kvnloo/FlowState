// EEG tapestry app: incremental engine -> WebGL2 instanced renderer, one rAF scheduler that sleeps when idle,
// compositor-only DOM for the live write head / hover ring / card, a 2D overlay redrawn only on camera change.
(async function () {
  const T = Tapestry, BANDS = T.BANDS, NB = 8, $ = s => document.querySelector(s);
  const Q = new URLSearchParams(location.search), BENCH = Q.has("bench");
  const NAMES = { delta: "delta", theta: "theta", low_alpha: "low alpha", high_alpha: "high alpha", low_beta: "low beta", high_beta: "high beta", low_gamma: "low gamma", high_gamma: "high gamma" };
  const HEX = b => `rgb(${T.COLOR[b].join(",")})`;
  const opts = await fetch("params.json").then(r => r.json());
  let E = TapestryEngine.Engine(opts); const o = E.o;
  const stage = $("#stage"), glc = $("#gl"), ov = $("#ov"), octx = ov.getContext("2d");
  const ARM = Q.get("arm") || "gl";
  let R = null, c2 = null;
  if (ARM === "c2d" || ARM === "none") { glc.style.display = "none"; c2 = document.createElement("canvas"); c2.style.cssText = "position:absolute;inset:0;width:100%;height:100%"; stage.prepend(c2); }
  if (ARM === "gl") R = TapestryGL.Renderer(glc, E);
  const START = (Q.get("start") || "15:38:01").split(":").map(Number), S0 = START[0] * 3600 + START[1] * 60 + START[2];
  // ---------------- session: time-keyed cells (one per wall-clock second; gaps stay empty) ----------------
  // state per cell: 0 absent (no samples), 1 valid (in engine), 2 excluded (bad contact; out of baseline/notes/giants)
  let S = null, points = [];
  function newSession(kind, label) {
    const id = kind === "replay" ? "replay:eegmat" : `${kind}:${new Date().toISOString().slice(0, 19)}`;
    S = { id, kind, label, epoch: kind !== "replay", minute0: null, state: new Uint8Array(1 << 14), quality: [], cellOf: new Int32Array(1 << 14), pointOf: new Int32Array(1 << 14).fill(-1), marks: [], lastCell: -1, absent: 0 };
    points = []; E = TapestryEngine.Engine(kind === "replay" ? opts : Object.assign({}, opts, { liveSettle: true })); if (R) { R.setEngine(E); R.reset(); }
    tags = (JSON.parse(localStorage.getItem("eeg-tags-v3") || "{}"))[id] || [];
    for (const el of noteEls.values()) el.remove(); noteEls.clear(); notesEl.innerHTML = `<p style="color:var(--mute)">Notes appear after 10 minutes, compared with your previous 10 minutes.</p>`;
    $("#src").textContent = label; $("#speed").style.display = kind === "replay" ? "" : "none"; hoverI = pinned = -1; cardFor = -2; updateCard(); setTarget(fitWidth(), true); follow = true; invalidate(true); }
  const growU8 = (a, n, fill) => { if (n < a.length) return a; const b = new a.constructor(Math.max(n + 1, a.length * 2)); if (fill !== undefined) b.fill(fill); b.set(a); return b; };
  // seconds: [{t (s; epoch for live, day-seconds for replay), bands, quality, valid}]
  function addSeconds(list, birth) { const validBatch = []; const from = E.n; const newMarks = [];
    for (const p of list) { if (S.minute0 === null) { S.minute0 = Math.floor(p.t / 60) * 60; S.firstCell = Math.round(p.t) - S.minute0; }
      const cell = Math.round(p.t) - S.minute0; if (cell <= S.lastCell) continue;
      S.state = growU8(S.state, cell); S.pointOf = growU8(S.pointOf, cell, -1); S.cellOf = growU8(S.cellOf, E.n + validBatch.length);
      S.quality[cell] = p.quality || null;
      if (p.valid === false) { S.state[cell] = 2; const m = { cell, birth }; S.marks.push(m); newMarks.push(m); }
      else { S.state[cell] = 1; const idx = E.n + validBatch.length; S.cellOf[idx] = cell; S.pointOf[cell] = idx; validBatch.push(p); points.push(p); }
      if (S.lastCell >= (S.firstCell ?? 0) && cell > S.lastCell + 1 && S.state[S.lastCell + 1] === 0) S.absent += cell - S.lastCell - 1;   // resumed after a gap: count the hole
      S.lastCell = cell; lastSecond = p; }
    if (validBatch.length) E.push(validBatch);
    if (R) R.sync(Math.min(from, E.n), birth, S.cellOf, S.marks);
    glDirty = ovDirty = hoverDirty = true; land(list[list.length - 1], list.length); onData(list[list.length - 1]); invalidate(); }
  function markAbsent(t) { if (S.minute0 === null) return; const cell = Math.round(t) - S.minute0; if (cell <= S.lastCell) return; S.state = growU8(S.state, cell); S.lastCell = cell; S.absent++; ovDirty = true; invalidate(); }
  let tags = [], lastSecond = null;
  const dur = s => s >= 60 ? `${Math.floor(s / 60)} min${s % 60 ? " " + (s % 60) + " s" : ""}` : `${s} s`;
  function saveTags() { const all = JSON.parse(localStorage.getItem("eeg-tags-v3") || "{}"); all[S.id] = tags; localStorage.setItem("eeg-tags-v3", JSON.stringify(all)); }
  const pad2 = v => String(v).padStart(2, "0");
  const clock = c => { if (!S || S.minute0 === null) return "--:--:--"; const t = S.minute0 + c;
    if (S.epoch) return new Date(t * 1000).toTimeString().slice(0, 8); const s = ((t % 86400) + 86400) % 86400; return [s / 3600 | 0, (s / 60 | 0) % 60, s % 60].map(pad2).join(":"); };
  const cells = () => S ? S.lastCell + 1 : 0;

  // ---------------- camera (device px) ----------------
  let dpr = Math.min(devicePixelRatio || 1, +(Q.get("dpr") || 2)), cssW = 1, cssH = 1;
  const cam = { s: 1, tx: 0, ty: 0 }, tgt = { s: 1, tx: 0, ty: 0 }; let anchor = null, follow = true, camMoved = true;
  const WW = o.cols * o.pitch, rowsOf = n => Math.max(1, Math.ceil(n / o.cols)), sheetH = () => rowsOf(cells() + 1) * o.pitch;
  function resize() { cssW = stage.clientWidth; cssH = stage.clientHeight; for (const c of [glc, ov, c2].filter(Boolean)) { c.width = Math.round(cssW * dpr); c.height = Math.round(cssH * dpr); } invalidate(true); }
  function fitWidth() { const s = Math.min((cssW - 140) / WW, 3) * dpr; return { s, tx: (cssW * dpr - WW * s) / 2, ty: 86 * dpr }; }
  function fitAll() { const f = fitWidth(); const s = Math.min(f.s, (cssH - 130) * dpr / Math.max(sheetH(), 1)); return { s, tx: (cssW * dpr - WW * s) / 2, ty: 86 * dpr }; }
  function setTarget(c, smooth = true) { Object.assign(tgt, c); anchor = null; if (!smooth) Object.assign(cam, c); invalidate(true); }
  function zoomAt(f, sx, sy, smooth) { liveZoom = false; const ns = Math.min(Math.max(tgt.s * f, fitAll().s * 0.6), dpr * 18);
    const wx = (sx - tgt.tx) / tgt.s, wy = (sy - tgt.ty) / tgt.s; tgt.s = ns; tgt.tx = sx - wx * ns; tgt.ty = sy - wy * ns;
    if (!smooth) { Object.assign(cam, tgt); anchor = null; } else anchor = { sx, sy, wx, wy }; setFollow(false); invalidate(true); }
  function clampT(c) { const W = WW * c.s, H = sheetH() * c.s, m = 120 * dpr; c.tx = Math.min(Math.max(c.tx, cssW * dpr - W - m * 4), m * 4); c.ty = Math.min(Math.max(c.ty, cssH * dpr - H - m * 4), m * 4); }
  function stepCamera(dt) { const k = 1 - Math.exp(-dt * 14);
    const ls = Math.log(cam.s), lt = Math.log(tgt.s); cam.s = Math.exp(ls + (lt - ls) * k);
    if (anchor) { cam.tx = anchor.sx - anchor.wx * cam.s; cam.ty = anchor.sy - anchor.wy * cam.s; if (Math.abs(lt - Math.log(cam.s)) < 1e-4) { cam.s = tgt.s; anchor = null; } }
    else { cam.tx += (tgt.tx - cam.tx) * k; cam.ty += (tgt.ty - cam.ty) * k; }
    const moving = Math.abs(cam.s - tgt.s) > 1e-4 * tgt.s || Math.abs(cam.tx - tgt.tx) > 0.3 || Math.abs(cam.ty - tgt.ty) > 0.3;
    if (!moving) Object.assign(cam, tgt); return moving; }

  // ---------------- scheduler ----------------
  let raf = 0, last = performance.now(), glDirty = true, ovDirty = true, hoverDirty = false;
  function invalidate(cam) { glDirty = true; if (cam) { ovDirty = true; camMoved = true; } if (!raf && !BENCH) raf = requestAnimationFrame(frame); }
  const now = () => performance.now() / 1000;
  function frame(t) { raf = 0; const dt = Math.min(0.05, (t - last) / 1000); last = t;
    let again = false;
    moving = stepCamera(dt) || !!drag; if (moving) { again = true; glDirty = ovDirty = camMoved = true; }
    pump(dt); if ((holdC0 !== null || openRange()) && cells() - 1 !== lastHoldEnd) { lastHoldEnd = cells() - 1; ovDirty = true; }
    const animEnd = R ? R.animatingUntil() + 0.62 : -1; if (now() < animEnd) { glDirty = true; again = true; wasAnim = true; } else if (wasAnim) { wasAnim = false; glDirty = true; }
    if (dimAnim()) { glDirty = true; again = true; }
    if (glDirty) { glDirty = false; render(); if (tilesPending) again = true; }
    if (ovDirty) { drawOverlay(); ovDirty = false; }
    if (camMoved || hoverDirty) { placeFx(); camMoved = hoverDirty = false; }
    if (again || replayActive()) raf = requestAnimationFrame(frame); else if (!idleT) idleT = setTimeout(idlePrefetch, 120); }
  function sheetRect(c) { return [c.tx, c.ty, WW * c.s, sheetH() * c.s]; }
  const SPLIT = (Q.get("mode") || "split") === "split", TILED = !SPLIT && (Q.get("tiles") ?? "1") !== "0";
  let baseScale = 0, lastTiles = null;
  function render() { if (ARM === "none") return; if (!R) return drawC2D();
    const iso = dims.some(d => d < 0.999);
    if (Q.get("split") !== "0" && (Q.get("tiles") === "0" || iso || SPLIT)) { const settled = !moving && !(now() < (R.animatingUntil() + 0.62)) && !BENCH;
      if (settled && Q.get("exact") !== "0") { R.draw(cam, { sheet: sheetRect(cam), time: now(), dur: 0.45, cull: true, shadow: 22 * dpr }); lastTiles = null; return; }
      R.drawSplit(cam, { sheet: sheetRect(cam), time: now(), dur: 0.45, cull: true, lowScale: +(Q.get("low") || (moving ? 0.35 : 0.5)), lowBands: +(Q.get("lb") || (moving ? 3 : 2)), shadow: 22 * dpr }); lastTiles = null; return; }
    if (!TILED || iso) { R.draw(cam, { sheet: sheetRect(cam), time: now(), dur: 0.45, cull: Q.get("cull") !== "0", shadow: Q.get("glshadow") === "0" ? 0 : 22 * dpr }); lastTiles = null; return; }
    if (!baseScale) baseScale = Math.pow(2, Math.floor(Math.log2(fitAll().s)));
    lastTiles = R.drawTiled(cam, { levelMode: Q.get("level") || "round", settled: !moving, base: baseScale, sheetWorld: [0, 0, WW, sheetH()], time: now(), dur: 0.45, budget: +(Q.get("budget") || 4), probe: benchProbe, shadow: Q.get("glshadow") === "0" ? 0 : 22 * dpr });
    if (lastTiles.pending > 0) glDirty = true, tilesPending = true; else tilesPending = false; }
  let lastHoldEnd = -1, tilesPending = false, benchProbe = null, moving = false, idleT = 0, wasAnim = false;
  // idle prefetch: when nothing moves, warm the cache around the view (current, next and previous zoom level)
  function idlePrefetch() { idleT = 0; if (!R || !TILED || moving || BENCH || !baseScale) return; const t0 = performance.now();
    const made = R.prefetch(cam, { base: baseScale, sheetWorld: [0, 0, WW, sheetH()], time: now(), dur: 0.45 }, 3); if (made) idleT = setTimeout(idlePrefetch, 40); }
  function drawC2D() { const x = c2.getContext("2d"); x.setTransform(1, 0, 0, 1, 0, 0); x.clearRect(0, 0, c2.width, c2.height); const [sx, sy, sw, sh] = sheetRect(cam);
    x.save(); x.beginPath(); x.rect(sx, sy, sw, sh); x.clip(); x.fillStyle = "#fff"; x.fillRect(sx, sy, sw, sh); x.setTransform(cam.s, 0, 0, cam.s, cam.tx, cam.ty);
    const wy0 = -cam.ty / cam.s, wy1 = (c2.height - cam.ty) / cam.s, Rr = E.R, n = E.n;
    BANDS.forEach((b, k) => { const [r, g, bl] = T.COLOR[b]; x.fillStyle = `rgba(${r},${g},${bl},${(T.ALPHA[b] ?? .5) * dims[k]})`; const m = o.rmax[b] * o.pitch * 14;
      const i0 = Math.max(0, Math.floor((wy0 - m) / o.pitch) * 60), i1 = Math.min(n, (Math.ceil((wy1 + m) / o.pitch) + 1) * 60);
      for (let i = i0; i < i1; i++) { const rr = Rr[i * NB + k]; if (rr < 0.3) continue; x.beginPath(); x.arc((i % 60) * o.pitch + o.pitch / 2, ((i / 60) | 0) * o.pitch + o.pitch / 2, rr, 0, 6.2832); x.fill(); } });
    x.restore(); }

  // ---------------- band isolate (animated dims) ----------------
  const dims = new Float32Array(NB).fill(1), dimT = new Float32Array(NB).fill(1); let lockBand = -1, hoverBand = -1;
  function setIso() { const k = hoverBand >= 0 ? hoverBand : lockBand, f = E.settling ? 0.7 : 1; for (let b = 0; b < NB; b++) dimT[b] = (k < 0 || k === b ? 1 : 0.1) * f; invalidate(); }
  let wasSettling = false;
  function dimAnim() { let m = false; for (let b = 0; b < NB; b++) { const d = dimT[b] - dims[b]; if (Math.abs(d) > 0.004) { dims[b] += d * 0.22; m = true; } else dims[b] = dimT[b]; }
    if (R) { R.dim.set(dims); const k = hoverBand >= 0 ? hoverBand : lockBand; R.setGiantDim(k < 0 ? 1 : 0.25); } return m; }

  // ---------------- data sources ----------------
  let queue = [], qi = 0, speed = +(Q.get("speed") || 60), acc = 0, paused = false, live = null;
  const replayActive = () => !live && qi < queue.length && !paused;
  const streaming = () => replayActive() || !!live;
  function pump(dt) { if (!replayActive()) return; if (speed === 0) acc = queue.length - qi; else acc += dt * speed; const k = Math.min(queue.length - qi, Math.floor(acc)); setRing(speed <= 10 ? acc % 1 : -1); if (!k) return; acc -= k;
    const list = []; for (let j = 0; j < k; j++, qi++) list.push({ t: S0 + qi, bands: queue[qi].bands, quality: null, valid: true, stage: queue[qi].stage }); addSeconds(list, k > 400 ? -1 : now()); }
  // live/sim handlers -> session
  let qState = [null, null, null, null], goodRun = 0, pendQ = null, pendN = 0;
  let away = null; // {idx, cell} first point recorded while hidden
  document.addEventListener("visibilitychange", () => { if (!live || !S) return;
    if (document.hidden) { away = { idx: E.n, cell: cells(), t: Date.now() }; return; }
    if (!away) return; const a0 = away; away = null; const n0 = E.n - a0.idx; if (n0 < 30 || !R) return;
    const rows0 = (S.cellOf[a0.idx] / 60) | 0, rows = Math.max(1, ((cells() - 1) / 60 | 0) - rows0 + 1), span = Math.min(3, 0.15 * rows + 0.6), t0 = now();
    R.restamp(a0.idx, i => t0 + (((S.cellOf[i] / 60) | 0) - rows0) / rows * span + (S.cellOf[i] % 60) * 0.002);
    const span0 = cells() - a0.cell, mins = Math.round(span0 / 60), lab = $("#away"); lab.textContent = `while you were away · ${clock(a0.cell)}–${clock(cells() - 1)} · ${mins >= 1 ? mins + " min" : span0 + " s"} in ${span.toFixed(1)} s`;
    lab.classList.add("show"); setTimeout(() => lab.classList.remove("show"), (span + 2.5) * 1000); setFollow(true); followHead(true); invalidate(true); });
  const liveHandlers = { second: s => { addSeconds([s], document.hidden ? -1 : now()); const q = s.quality; goodRun = q.every(x => x === "good" || x === "blink") ? goodRun + 1 : 0;
      const key = q.map(x => x === "blink" ? "good" : x).join();
      if (key !== qState.join()) { if (key === pendQ) pendN++; else { pendQ = key; pendN = 1; } if (pendN >= 3 || qState[0] === null) { qState = key.split(","); pendQ = null; pendN = 0; contactChanged(); } } else { pendQ = null; pendN = 0; }
      // fold the trace after 10 consecutive all-good seconds of data (reopens on any contact change)
      if (goodRun >= 10 && trace.classList.contains("show")) { trace.classList.remove("show"); document.body.classList.remove("settling"); stateEl.textContent = `${live.label} · recording · contact good`; } 
      if (liveZoom && S.firstCell !== undefined && cells() - S.firstCell >= 60 && (cells() % 60) === 1) glideHome(); },   // first full row done: glide to the whole sheet once
    absent: t => markAbsent(t), progress: f => setRing(f), raw: (ch, s) => traceRaw(ch, s) };
  async function loadReplay() { const t = await fetch(Q.get("data") || "../data/day.jsonl").then(r => r.text()); return t.trim().split("\n").map(JSON.parse); }

  // ---------------- overlay (2D, camera-dependent only) ----------------
  let hoverNote = null;
  let ovRects = null;
  function drawOverlay() { const c = octx, W = ov.width, H = ov.height; c.setTransform(1, 0, 0, 1, 0, 0);
    if (!ovRects || Q.get("ovclear") === "full" || Q.get("glshadow") === "0") c.clearRect(0, 0, W, H); else for (const r of ovRects) { const x = Math.floor(r[0]) - 2, y = Math.floor(r[1]) - 2; c.clearRect(x, y, Math.ceil(r[0] + r[2]) + 2 - x, Math.ceil(r[1] + r[3]) + 2 - y); }
    ovRects = [];
    const [sx, sy, sw, sh] = sheetRect(cam);
    if (Q.get("glshadow") === "0") { c.save(); c.shadowColor = "rgba(60,40,20,.16)"; c.shadowBlur = 28 * dpr; c.shadowOffsetY = 8 * dpr; c.fillStyle = "#fff";
    c.beginPath(); c.rect(0, 0, W, H); c.rect(sx, sy, sw, sh); c.clip("evenodd"); c.fillRect(sx, sy, sw, sh); c.restore(); }
    // corner brackets (HUD accent)
    c.strokeStyle = "rgba(30,28,25,.5)"; c.lineWidth = dpr; const L = 14 * dpr, g = 8 * dpr; const pad = 4 * dpr;
    for (const [x, y] of [[sx - g, sy - g], [sx + sw + g, sy - g], [sx - g, sy + sh + g], [sx + sw + g, sy + sh + g]]) ovRects.push([x - L - pad, y - L - pad, 2 * (L + pad), 2 * (L + pad)]);
    ovRects.push([sx - 76 * dpr, 0, 76 * dpr, H]);
    for (const [x, y, dx, dy] of [[sx - g, sy - g, 1, 1], [sx + sw + g, sy - g, -1, 1], [sx - g, sy + sh + g, 1, -1], [sx + sw + g, sy + sh + g, -1, -1]]) { c.beginPath(); c.moveTo(x + dx * L, y); c.lineTo(x, y); c.lineTo(x, y + dy * L); c.stroke(); }
    // minute ruler
    const rowPx = o.pitch * cam.s, r0 = Math.max(0, Math.floor(-cam.ty / rowPx)), r1 = Math.min(rowsOf(cells() + 1), Math.ceil((H - cam.ty) / rowPx) + 1);
    const every = rowPx > 26 * dpr ? 1 : rowPx > 8 * dpr ? 5 : rowPx > 3 * dpr ? 10 : 30;
    c.fillStyle = "rgba(30,28,25,.55)"; c.font = `${10 * dpr}px ui-monospace, SF Mono, Menlo, monospace`; c.textAlign = "right"; c.textBaseline = "middle";
    for (let r = r0; r < r1; r++) { const y = cam.ty + (r + .5) * rowPx; const major = r % every === 0;
      c.fillRect(sx - (major ? 12 : 6) * dpr, y - .5 * dpr, (major ? 8 : 3) * dpr, dpr); if (major) c.fillText(clock(r * 60).slice(0, 5), sx - 16 * dpr, y); }
    // before the session started: paper over row 0's leading cells so haze from later seconds can't look recorded
    if (S && S.firstCell > 0 && r0 === 0) { const y = cam.ty, h = rowPx, x1 = cam.tx + S.firstCell * o.pitch * cam.s; c.fillStyle = "#fbfaf7"; c.fillRect(sx, y, x1 - sx, h);
      c.fillStyle = "rgba(30,28,25,.45)"; c.fillRect(x1 - dpr, y + h * .2, dpr, h * .6); if (rowPx > 12 * dpr && x1 - sx > 90 * dpr) { c.textAlign = "right"; c.fillText(`started ${clock(S.firstCell)}`, x1 - 6 * dpr, y + h / 2); c.textAlign = "left"; } ovRects.push([sx, y, x1 - sx + 2, h]); }
    // gaps: hairline + label over runs of absent seconds (live sessions)
    if (S && S.kind !== "replay") { c.strokeStyle = "rgba(30,28,25,.35)"; c.lineWidth = dpr; c.setLineDash([2 * dpr, 3 * dpr]); c.fillStyle = "rgba(30,28,25,.55)"; c.textAlign = "left";
      let run = -1; for (let cc = Math.max(S.firstCell || 0, r0 * 60); cc <= Math.min(cells(), r1 * 60); cc++) { const absent = cc < cells() && S.state[cc] === 0;
        if (absent && run < 0) run = cc; if ((!absent || cc === cells()) && run >= 0) { const y = cam.ty + (((run / 60) | 0) + .5) * rowPx, x0 = cam.tx + (run % 60) * o.pitch * cam.s, x1 = cam.tx + ((cc - 1) % 60 + 1) * o.pitch * cam.s;
          c.beginPath(); c.moveTo(x0, y); c.lineTo(((cc - 1) / 60 | 0) === (run / 60 | 0) ? x1 : sx + sw, y); c.stroke(); if (rowPx > 9 * dpr) { const txt = `no signal ${clock(run)}–${clock(cc - 1)} · ${cc - run} s`, tw = c.measureText(txt).width; c.fillStyle = "rgba(255,255,255,.92)"; c.fillRect(x0, y - 13 * dpr, tw + 8 * dpr, 13 * dpr); c.fillStyle = "#1e1c19"; c.fillText(txt, x0 + 4 * dpr, y - 6 * dpr); } ovRects.push([sx, y - 18 * dpr, sw, 22 * dpr]); run = -1; } }
      c.setLineDash([]); }
    // your tag ranges + the range being held: left gutter bar
    if (S) { const bar = (c0, c1, col, w) => { const y0 = cam.ty + ((c0 / 60) | 0) * rowPx, y1 = cam.ty + (((c1 / 60) | 0) + 1) * rowPx; const x = sx - 4 * dpr - w; c.fillStyle = col; c.fillRect(x, y0, w, Math.max(2 * dpr, y1 - y0)); };
      for (const tg of tags) { if (tg.c1 === null) bar(tg.c0, Math.max(tg.c0, cells() - 1), "#e50cbc", 3 * dpr); else if (tg.c1 > tg.c0) bar(tg.c0, tg.c1, "rgba(30,28,25,.55)", 2.5 * dpr); }
      if (holdC0 !== null && !openRange()) bar(holdC0, Math.max(holdC0, cells() - 1), "#e50cbc", 3 * dpr); }
    // hovered note bracket
    if (hoverNote) { const y0 = cam.ty + Math.floor(hoverNote.i0 / 60) * rowPx, y1 = cam.ty + (Math.floor(Math.max(hoverNote.i0, hoverNote.i1 - 1) / 60) + 1) * rowPx, x = sx + sw + 14 * dpr;
      c.strokeStyle = "#1e1c19"; c.lineWidth = 1.5 * dpr; c.beginPath(); c.moveTo(x - 6 * dpr, y0); c.lineTo(x, y0); c.lineTo(x, y1); c.lineTo(x - 6 * dpr, y1); c.stroke();
      c.fillStyle = "rgba(30,28,25,.06)"; c.fillRect(sx, y0, sw, y1 - y0); ovRects.push([sx - 2, y0 - 2, sw + 30 * dpr, y1 - y0 + 4]); } }

  // ---------------- compositor-only fx: write head, hover ring, card ----------------
  const head = $("#head"), hov = $("#hover"), hovI = hov.firstElementChild, card = $("#card"), ringArc = $("#ringArc"), contactEls = [...document.querySelectorAll("#contact i")];
  let ringShown = -2;
  function setRing(f) { const v = f < 0 ? -1 : Math.round(f * 50) / 50; if (v === ringShown) return; ringShown = v; head.classList.toggle("noring", v < 0); if (v >= 0) ringArc.style.strokeDashoffset = String(62.83 * (1 - v)); }
  function land(p, batch) { if (batch > 1 || (!live && speed > 10) || speed === 0) { setRing(-1); return; } head.classList.remove("land"); void head.offsetWidth; head.classList.add("land"); setRing(0); liveDot.classList.remove("flash"); void liveDot.offsetWidth; liveDot.classList.add("flash");
    if (p && p.quality) p.quality.forEach((s, i) => contactEls[i].className = s); }
  let mouse = null, hoverI = -1, pinned = -1;
  const toCss = (i) => [((i % 60) * o.pitch + o.pitch / 2) * cam.s / dpr + cam.tx / dpr, (((i / 60) | 0) * o.pitch + o.pitch / 2) * cam.s / dpr + cam.ty / dpr];
  function placeFx() { const [hx, hy] = toCss(cells()); head.style.transform = `translate3d(${hx}px,${hy}px,0) scale(${Math.min(1.6, Math.max(.7, cam.s / dpr))})`; head.style.opacity = streaming() ? 1 : 0;
    head.classList.toggle("haslive", !!live); placeTrace(hx, hy);
    const i = pinned >= 0 ? pinned : hoverI;
    if (i >= 0 && i < cells()) { const [x, y] = toCss(i), r = Math.max(5, o.pitch * cam.s / dpr * .62); hovI.style.cssText = `left:${-r}px;top:${-r}px;width:${2 * r}px;height:${2 * r}px`; hov.style.transform = `translate3d(${x}px,${y}px,0)`; hov.style.opacity = 1; }
    else hov.style.opacity = 0;
    if (i >= 0 && i < cells() && mouse) { const x = Math.min(mouse.x + 18, innerWidth - 360 - 240), y = Math.min(mouse.y + 16, innerHeight - 250); card.style.transform = `translate3d(${x}px,${y}px,0)`; } }
  let cardFor = -2;
  const CHN = ["TP9 left ear", "AF7 left brow", "AF8 right brow", "TP10 right ear"];
  function updateCard() { const c = pinned >= 0 ? pinned : hoverI; if (c === cardFor) return; cardFor = c; if (!S || c < 0 || c >= cells()) { card.classList.remove("show"); return; }
    const st0 = S.state[c]; if (c < (S.firstCell || 0)) { card.classList.remove("show"); return; }
    if (st0 !== 1) { const q = S.quality[c]; const bad = q ? q.map((s, k) => s !== "good" && s !== "blink" ? `${CHN[k]}: ${s}` : "").filter(Boolean).join("<br>") : "";
      card.innerHTML = `<div class="mono">${st0 === 2 ? "not measured · bad contact" : "no signal"}</div><h4>${clock(c)}</h4><p style="margin:6px 0 0;color:#5b564f">${st0 === 2 ? bad + "<br>Left out of the scale, notes and bursts." : "No samples arrived for this second (Bluetooth gap or not recording)."}</p>`;
      card.classList.add("show"); return; }
    const i = S.pointOf[c], p = points[i], st = p.stage ? ` · ${p.stage}` : "";
    card.innerHTML = `<div class="mono">${S.kind === "replay" ? "replay" : S.kind === "sim" ? "simulated" : "live"}${st}</div><h4>${clock(c)}</h4><div class="bars">${BANDS.map((b, k) => { const u = E.U[i * NB + k]; return `<span>${NAMES[b]}</span><span class="bar"><i style="width:${Math.min(100, u * 50)}%;background:${HEX(b)}"></i></span><span class="mono" style="text-transform:none">${u.toFixed(2)}</span>`; }).join("")}</div><div class="mono" style="margin-top:8px;text-transform:none">${E.settling ? `scale settling · sized against ${Math.floor(E.scaleBasis / 60)}:${String(E.scaleBasis % 60).padStart(2, "0")} so far · faint until 5:00` : "bar = power vs this session (1.0 = 95th pct)"}</div>`;
    card.classList.add("show"); }
  function pick(cx, cy) { const wx = (cx * dpr - cam.tx) / cam.s, wy = (cy * dpr - cam.ty) / cam.s; if (wx < 0 || wy < 0 || wx >= WW) return -1; const i = Math.floor(wy / o.pitch) * 60 + Math.floor(wx / o.pitch); return i < cells() ? i : -1; }

  // ---------------- input ----------------
  let drag = null, vel = { x: 0, y: 0 };
  stage.addEventListener("pointerdown", e => { stage.setPointerCapture(e.pointerId); drag = { x: e.clientX, y: e.clientY, t: performance.now(), moved: false }; vel = { x: 0, y: 0 }; stage.classList.add("drag"); });
  stage.addEventListener("pointermove", e => { const r = stage.getBoundingClientRect(); mouse = { x: e.clientX, y: e.clientY, sx: e.clientX - r.left, sy: e.clientY - r.top };
    if (drag) { const dx = (e.clientX - drag.x) * dpr, dy = (e.clientY - drag.y) * dpr, t = performance.now(); if (Math.abs(dx) + Math.abs(dy) > 3) drag.moved = true;
      cam.tx += dx; cam.ty += dy; tgt.tx = cam.tx; tgt.ty = cam.ty; anchor = null; vel = { x: dx / Math.max(1, t - drag.t), y: dy / Math.max(1, t - drag.t) }; drag.x = e.clientX; drag.y = e.clientY; drag.t = t; setFollow(false); invalidate(true); }
    const i = pick(mouse.sx, mouse.sy); if (i !== hoverI) { hoverI = i; updateCard(); } hoverDirty = true; invalidate(); });
  stage.addEventListener("pointerup", e => { stage.classList.remove("drag"); if (drag && !drag.moved) { pinned = pinned === hoverI ? -1 : hoverI; updateCard(); }
    else if (drag) { tgt.tx += vel.x * 160; tgt.ty += vel.y * 160; clampT(tgt); } drag = null; invalidate(true); });
  stage.addEventListener("pointerleave", () => { hoverI = -1; if (pinned < 0) updateCard(); hoverDirty = true; invalidate(); });
  stage.addEventListener("wheel", e => { e.preventDefault(); const r = stage.getBoundingClientRect(), sx = (e.clientX - r.left) * dpr, sy = (e.clientY - r.top) * dpr;
    const dy = e.deltaMode === 1 ? e.deltaY * 16 : e.deltaY;
    if (e.ctrlKey || e.metaKey) { const notch = Math.abs(dy) >= 50 && !e.ctrlKey; zoomAt(Math.exp(-dy * (e.ctrlKey ? 0.012 : 0.0022)), sx, sy, notch); }
    else { cam.tx -= e.deltaX * dpr; cam.ty -= dy * dpr; clampT(cam); Object.assign(tgt, cam); anchor = null; setFollow(false); invalidate(true); } }, { passive: false });
  stage.addEventListener("dblclick", e => { const r = stage.getBoundingClientRect(); zoomAt(e.shiftKey ? 0.5 : 2.2, (e.clientX - r.left) * dpr, (e.clientY - r.top) * dpr, true); });
  const centre = () => [cssW * dpr / 2, cssH * dpr / 2];
  $("#zin").onclick = () => zoomAt(1.8, ...centre(), true); $("#zout").onclick = () => zoomAt(1 / 1.8, ...centre(), true); $("#zfit").onclick = () => setTarget(fitAll());
  function setFollow(v) { follow = v; $("#follow").classList.toggle("show", !v && streaming()); }
  $("#follow").onclick = () => { setFollow(true); followHead(true); };
  function liveCam() { const s = 64 * dpr / o.pitch; const c = Math.max(0, cells() - 1), wx = (c % 60 + .5) * o.pitch, wy = (((c / 60) | 0) + .5) * o.pitch;
    setFollow(true); liveZoom = true; setTarget({ s, tx: cssW * dpr * 0.35 - wx * s, ty: Math.min(fitWidth().ty, cssH * dpr * 0.35 - wy * s) }); }
  function glideHome() { if (!liveZoom) return; liveZoom = false; setTarget(fitWidth()); setTimeout(() => followHead(false), 700); }
  let liveZoom = false;
  function followHead(force) { if (liveZoom && follow) { const c = cells(), s = tgt.s, x = ((c % 60) + .5) * o.pitch * s + tgt.tx, W = cssW * dpr; if (x > W * 0.7 || x < W * 0.3) { tgt.tx -= x - W * 0.35; if (c % 60 < 3) tgt.tx = Math.min(tgt.tx, 60 * dpr); anchor = null; invalidate(true); } } const y = (((cells() / 60) | 0) * o.pitch + o.pitch) * tgt.s + tgt.ty, H = cssH * dpr;
    if (force || y > H * 0.82 || y < H * 0.15) { tgt.ty -= y - H * 0.7; tgt.ty = Math.min(tgt.ty, fitWidth().ty); anchor = null; invalidate(true); } }
  // T: tap = tag this moment. Hold 420 ms (ring arms around the pen) = open a range from now; the tag box opens at once,
  // the range stays open while you work, and the next T closes it (so an 18-minute "coffee" doesn't need an 18-minute hold).
  let holdC0 = null, holdAt = 0, holdTimer = 0;
  const openRange = () => tags.find(t => t.c1 === null);
  addEventListener("keyup", e => { if ((e.key === "t" || e.key === "T") && holdAt) { holdAt = 0; head.classList.remove("holding");
      if (holdTimer) { clearTimeout(holdTimer); holdTimer = 0; holdC0 = null; ovDirty = true; invalidate(true); openTag(); } } });
  addEventListener("keydown", e => { if (e.target.tagName === "INPUT") return;
    if (e.key === "t" || e.key === "T") { e.preventDefault(); if (e.repeat || holdAt) return; const op = openRange();
      if (op) { op.c1 = Math.max(op.c0, cells() - 1); op.text = dur(op.c1 - op.c0 + 1); saveTags(); ovDirty = true; scheduleNotes(); invalidate(true); stateEl.textContent = `closed “${op.title}” · ${op.text}`; return; }
      holdAt = performance.now(); holdC0 = Math.max(0, cells() - 1); head.classList.add("holding");
      holdTimer = setTimeout(() => { holdTimer = 0; head.classList.remove("holding"); ovDirty = true; invalidate(true); openTag(["open", holdC0]); }, 420); } else if (e.key === "0") setTarget(fitAll()); else if (e.key === "+" || e.key === "=") zoomAt(1.8, ...centre(), true); else if (e.key === "-") zoomAt(1 / 1.8, ...centre(), true);
    else if (e.key === "Escape") { pinned = -1; lockBand = -1; updateLegend(); setIso(); updateCard(); hoverDirty = true; } else if (e.key === " ") { e.preventDefault(); paused = !paused; onData(); invalidate(); } else if (e.key === "f") { setFollow(true); followHead(true); } });
  new ResizeObserver(resize).observe(stage);

  // ---------------- side panel ----------------
  const leg = $("#legend");
  leg.innerHTML = BANDS.map((b, k) => `<button data-k="${k}"><i style="background:rgba(${T.COLOR[b]},${T.ALPHA[b] ?? .5});box-shadow:inset 0 0 0 1.5px ${HEX(b)}"></i>${NAMES[b]}</button>`).join("");
  leg.querySelectorAll("button").forEach(btn => { const k = +btn.dataset.k; btn.onmouseenter = () => { hoverBand = k; setIso(); }; btn.onmouseleave = () => { hoverBand = -1; setIso(); }; btn.onclick = () => { lockBand = lockBand === k ? -1 : k; updateLegend(); setIso(); }; });
  function updateLegend() { leg.querySelectorAll("button").forEach(b => b.classList.toggle("on", +b.dataset.k === lockBand)); }
  const gctx = $("#glyph").getContext("2d"), gs = 200; $("#glyph").width = gs * dpr; $("#glyph").height = gs * dpr; $("#glyph").style.width = gs + "px"; gctx.scale(dpr, dpr);
  const shownU = new Float32Array(NB);
  function drawGlyph() { const n = E.n; if (!n) return false; if (S && S.state[S.lastCell] === 2) { gctx.clearRect(0, 0, gs, gs); gctx.strokeStyle = "#bbb"; gctx.lineWidth = 2; gctx.beginPath(); gctx.arc(gs / 2, gs / 2, 18, 0, 7); gctx.stroke(); return false; } let m = false; gctx.clearRect(0, 0, gs, gs);
    for (let k = 0; k < NB; k++) { const t = Math.min(2, E.U[(n - 1) * NB + k]); const d = t - shownU[k]; if (Math.abs(d) > 0.002) { shownU[k] += d * 0.18; m = true; } }
    BANDS.forEach((b, k) => { const r = (gs / 2 - 4) * (1 - k / 9) * (0.25 + 0.375 * Math.min(2, shownU[k])); gctx.fillStyle = `rgba(${T.COLOR[b]},${T.ALPHA[b] ?? .5})`; gctx.beginPath(); gctx.arc(gs / 2, gs / 2, Math.max(1, Math.min(gs / 2 - 2, r)), 0, 7); gctx.fill(); });
    return m; }
  let glyphRaf = 0; function glyphLoop() { glyphRaf = drawGlyph() ? requestAnimationFrame(glyphLoop) : 0; }
  const notesEl = $("#notes"), noteEls = new Map(); let notesPending = false, notesAt = 0;
  function scheduleNotes() { if (notesPending || BENCH) return; notesPending = true; const run = () => { notesPending = false; notesAt = performance.now();
      const gl = E.giants().map(([i, k]) => [i, BANDS[k]]);
      const P = c => { let lo = 0, hi = E.n; while (lo < hi) { const m = (lo + hi) >> 1; if (S.cellOf[m] < c) lo = m + 1; else hi = m; } return Math.min(lo, Math.max(0, E.n - 1)); };
      const ptags = tags.map(tg => { const c1 = tg.c1 === null ? Math.max(tg.c0, cells() - 1) : (tg.c1 ?? tg.c0); return { i: P(tg.c0), i1: P(c1), title: tg.title, text: tg.text, c0: tg.c0, c1 }; });
      const list = T.annotate(points, opts, ptags, gl).map(n => n.tag ? Object.assign(n, { i0: ptags.find(p => p.title === n.title && p.i === n.i0)?.c0 ?? S.cellOf[n.i0], i1: ptags.find(p => p.title === n.title && p.i === n.i0)?.c1 ?? S.cellOf[n.i1] })
        : Object.assign(n, { i0: S.cellOf[Math.min(n.i0, E.n - 1)], i1: n.i1 >= E.n ? cells() : S.cellOf[n.i1] })).reverse(); if (!list.length) return;
      if (noteEls.size === 0) notesEl.innerHTML = "";
      const keys = new Set(); for (const a of list) { const key = `${a.title}|${a.i0}`; keys.add(key); let el = noteEls.get(key);
        const basis = a.tag ? (S.kind === "replay" ? "tag" : "your tag") : a.glyph !== undefined ? "detected · one second" : "band statistics · vs previous 10 min";
        const html = `<time>${clock(a.i0)}${a.i1 > a.i0 + 1 ? " – " + clock(a.i1) : ""}</time><b>${a.title}</b><p>${colorWords(S.kind === "replay" ? (a.text || "").replace(/your previous/g, "the previous").replace(/ on your head/g, "") : (a.text || ""))}</p><small>${basis}</small>`;
        if (!el) { el = document.createElement("div"); el.className = "note" + (a.tag ? " tag" : ""); el.style.setProperty("--c", a.title.includes("Alpha reducing") || a.title.includes("gamma") ? "#6f5ba3" : a.title.includes("Alpha growing") ? "#fcea01" : a.title.includes("Theta") ? "#ff8500" : a.title.includes("burst") ? "#e50cbc" : "#1e1c19");
          el.onmouseenter = () => { hoverNote = el._a; ovDirty = true; invalidate(); }; el.onmouseleave = () => { hoverNote = null; ovDirty = true; invalidate(); };
          el.onclick = () => flyTo(el._a); noteEls.set(key, el); }
        el._a = a; if (el._html !== html) { el.innerHTML = html; el._html = html; } }
      for (const [k, el] of noteEls) if (!keys.has(k)) { el.remove(); noteEls.delete(k); }
      list.forEach((a, j) => { const el = noteEls.get(`${a.title}|${a.i0}`); if (notesEl.children[j] !== el) notesEl.insertBefore(el, notesEl.children[j] || null); }); };
    const wait = Math.max(0, 700 - (performance.now() - notesAt)); setTimeout(() => (window.requestIdleCallback || setTimeout)(run), wait); }
  const CW = { red: "#dd0a0a", orange: "#ff8500", yellow: "#c9b800", green: "#3fae0c", cyan: "#0fa5c8", blue: "#022aba", purple: "#6f5ba3", magenta: "#e50cbc" };
  const colorWords = s => s.replace(/\b(red|orange|yellow|green|cyan|blue|purple|magenta)\b/g, w => `<span style="color:${CW[w]};font-weight:600">${w}</span>`);
  function flyTo(a) { const rows = Math.max(1, Math.floor((a.i1 - a.i0) / 60) + 1), s = Math.min(dpr * 8, Math.max(fitWidth().s, (cssH * dpr * 0.42) / (rows * o.pitch)));
    const wy = (Math.floor(a.i0 / 60) + rows / 2) * o.pitch; setFollow(false); setTarget({ s, tx: (cssW * dpr - WW * s) / 2, ty: cssH * dpr / 2 - wy * s }); }
  // tagging
  const tagbox = $("#tagbox"), tagin = $("#tagin");
  let tagRange = null;
  function openTag(range) { tagRange = range || null; const [x, y] = toCss(Math.max(0, cells() - 1)); $("#tagrange").textContent = range ? (range[0] === "open" ? `from ${clock(range[1])} · T again to close` : `${clock(range[0])} – ${clock(range[1])}`) : clock(Math.max(0, cells() - 1)); const r = stage.getBoundingClientRect(); tagbox.style.left = Math.min(innerWidth - 320, Math.max(10, r.left + x - 20)) + "px"; tagbox.style.top = (trace.classList.contains("show") ? Math.max(70, r.top + y - 64) : Math.min(innerHeight - 60, r.top + y + 20)) + "px"; tagbox.classList.add("show"); tagin.value = ""; tagin.focus(); }
  function addTag() { const title = tagin.value.trim(); tagbox.classList.remove("show"); tagin.blur(); if (!title) { holdC0 = null; ovDirty = true; invalidate(true); return; } const nowC = Math.max(0, cells() - 1), r = tagRange || [nowC, nowC]; const isOpen = r[0] === "open";
    tags.push(isOpen ? { c0: r[1], c1: null, title, text: "open · press T to close" } : { c0: r[0], c1: r[1], title, text: r[1] > r[0] ? dur(r[1] - r[0] + 1) : "this moment" }); saveTags(); if (!isOpen) holdC0 = null; ovDirty = true; scheduleNotes(); invalidate(true); }
  $("#tagok").onclick = addTag; tagin.onkeydown = e => { if (e.key === "Enter") addTag(); if (e.key === "Escape") { tagbox.classList.remove("show"); tagin.blur(); holdC0 = null; tagRange = null; ovDirty = true; invalidate(true); } }; $("#tag").onclick = () => openTag();
  // header
  const stateEl = $("#state"), liveDot = $("#live");
  function onData(p) { if (E.settling !== wasSettling) { wasSettling = E.settling; setIso(); } const n = S && S.firstCell ? cells() - S.firstCell : cells(); $("#count").textContent = n >= 3600 ? `${(n / 3600).toFixed(2)} h` : `${Math.floor(n / 60)} min ${n % 60} s`; $("#clock").textContent = n ? clock(cells() - 1) : "--:--:--"; if (S && S.absent) $("#count").textContent += ` · ${S.absent} s no signal`;
    if (!live) stateEl.textContent = S && S.kind !== "replay" ? `stopped · ${n >= 60 ? Math.floor(n / 60) + " min" : n + " s"} recorded` : paused ? "paused · space to resume" : streaming() ? `replaying ${speed ? speed + "×" : ""}` : `${rowsOf(n)} rows · done`;
    liveDot.classList.toggle("live", streaming());
    if (follow) followHead(false); if (!glyphRaf) glyphRaf = requestAnimationFrame(glyphLoop); scheduleNotes(); if (hoverI >= 0) { cardFor = -2; updateCard(); } setFollow(follow); }
  $("#speed").querySelectorAll("button").forEach(b => b.classList.toggle("on", +b.dataset.s === speed));
  $("#speed").querySelectorAll("button").forEach(b => b.onclick = () => { if (live) return; speed = +b.dataset.s; $("#speed").querySelectorAll("button").forEach(x => x.classList.toggle("on", x === b)); paused = false; onData(); invalidate(); });
  // ---------------- live sources ----------------
  const FIX = ["TP9 isn't touching: move the band down behind your left ear", "AF7 isn't touching: press the band flat on your left forehead", "AF8 isn't touching: press the band flat on your right forehead", "TP10 isn't touching: move the band down behind your right ear"];
  let fixLine = "", holdMsgUntil = 0;
  function contactChanged() { const q = qState; const bad = q.map((s, k) => s !== "good" ? CHN[k] : null).filter(Boolean); const k0 = q.findIndex(s => s !== "good"); fixLine = k0 >= 0 ? FIX[k0] + (q[k0] === "noisy" ? " (or stop moving for a moment)" : "") : "";
    if (now() >= holdMsgUntil) stateEl.textContent = !bad.length ? `${live.label} · all 4 electrodes good` : `${live.label} · adjust: ${bad.join(", ")}`;
    if (bad.length) { document.body.classList.add("settling"); trace.classList.add("show"); } }
  function stopLive() { if (live) live.stop(); live = null; contactEls.forEach(el => el.className = ""); setRing(-1); head.classList.remove("haslive"); $("#connect").textContent = "Connect Muse"; $("#sim").textContent = "Test stream"; trace.classList.remove("show"); document.body.classList.remove("settling"); }
  let absentTimer = 0;
  async function startLive(kind) { paused = false;
    try { stateEl.textContent = kind === "muse" ? "choose your Muse in the browser dialog…" : "starting test stream…";
      const src = kind === "muse" ? EEGSources.MuseSource(liveHandlers) : EEGSources.SimSource(liveHandlers, { speed: +(Q.get("simspeed") || 1) });   // requestDevice runs synchronously in the click
      const got = await src;   // only now replace the sheet: a cancelled chooser keeps whatever was there (and keeps it streaming)
      if (live) stopLive();
      const resume = S && S.kind === kind && S.minute0 !== null && (Date.now() / 1000 - (S.minute0 + S.lastCell)) < 1800;
      if (!resume) newSession(kind, kind === "muse" ? "muse s" : "simulated Muse · test data");
      queue = []; qi = 0; acc = 0; clearTimeout(absentTimer);   // a live session never shares data with the replay
      live = got; live.kind = kind; qState = [null, null, null, null]; goodRun = 0; pendQ = null; pendN = 0; trace.classList.add("show"); document.body.classList.add("settling");
      stateEl.textContent = resume ? `${live.label} · reconnected · the gap is marked “no signal”` : `${live.label} · waiting for contact`; $(kind === "muse" ? "#connect" : "#sim").textContent = "Stop";
      if (!resume) liveCam(); else { setFollow(true); followHead(true); }
      if (kind === "muse") live.ondisconnect = () => { stopLive(); stateEl.textContent = "Muse disconnected · reconnect to continue this sheet";
        const tick = () => { markAbsent(Math.floor(Date.now() / 1000) - 1); absentTimer = setTimeout(tick, 1000); }; tick(); };
      onData(); invalidate(true);
    } catch (e) { holdMsgUntil = now() + 4; const msg = /cancel|chosen|NotFound/i.test(e.message || e.name) ? "No Muse chosen" : (kind === "muse" ? "Muse: " : "test stream: ") + e.message; stateEl.textContent = msg; } }
  $("#connect").onclick = () => live && live.kind === "muse" ? (stopLive(), onData()) : startLive("muse");
  $("#sim").onclick = () => live && live.kind === "sim" ? (stopLive(), onData()) : startLive("sim");
  // live trace: last 4 s of each electrode, drawn on a small 2D canvas beside the pen while contact settles
  const trace = $("#trace"), tctx = trace.getContext("2d"), TR = 4 * 256, tbuf = [0, 1, 2, 3].map(() => new Float32Array(TR)), tpos = [0, 0, 0, 0]; let traceRaf = 0;
  function traceRaw(ch, s) { if (ch > 3 || !trace.classList.contains("show")) return; for (const v of s) { tbuf[ch][tpos[ch]] = v; tpos[ch] = (tpos[ch] + 1) % TR; } if (!traceRaf) traceRaf = requestAnimationFrame(drawTrace); }
  function drawTrace() { traceRaf = 0; const d = dpr, W = 260 * d, H = 164 * d; if (trace.width !== W) { trace.width = W; trace.height = H; trace.style.width = "260px"; trace.style.height = "164px"; }
    tctx.clearRect(0, 0, W, H); const top = 4 * d, laneH = 26 * d, PX = 230 * d, scale = laneH * 0.45 / 100;   // 100 µV = 45% of a lane
    tctx.font = `${10 * d}px ui-monospace, Menlo, monospace`; tctx.textBaseline = "top";
    for (let ch = 0; ch < 4; ch++) { const q = qState[ch], y0 = top + laneH * (ch + .5) + 6 * d; let m = 0; for (let i = 0; i < TR; i++) m += tbuf[ch][i]; m /= TR;   // remove each lane's 4 s mean (dry-electrode DC offset)
      tctx.strokeStyle = q === "good" ? "#1e1c19" : "#b9b3aa"; tctx.lineWidth = 1.2 * d; tctx.beginPath();
      for (let x = 0; x < 230; x++) { const v = tbuf[ch][(tpos[ch] + Math.floor(x / 230 * TR)) % TR] - m; const y = y0 - Math.max(-laneH * .5, Math.min(laneH * .5, v * scale)); x ? tctx.lineTo(x * d + 6 * d, y) : tctx.moveTo(6 * d, y); } tctx.stroke();
      tctx.fillStyle = q === "good" ? "#1e1c19" : "#9a948b"; tctx.fillText(EEGSources.CH[ch] + (q && q !== "good" ? " · " + q : ""), 8 * d, y0 - laneH * .5 - 4 * d); }
    tctx.fillStyle = "#e50cbc"; tctx.fillRect(PX + 6 * d, top + 4 * d, 1.5 * d, laneH * 4 + 4 * d);   // now-line
    tctx.fillStyle = "#1e1c19"; tctx.fillRect(W - 10 * d, top + laneH * .5 + 6 * d - 100 * scale / 2, 1.5 * d, 100 * scale); tctx.textAlign = "right"; tctx.fillText("100µV", W - 13 * d, top + 2 * d); tctx.textAlign = "left";
    const st = live && live.stats ? live.stats : {}; tctx.fillStyle = "#5b564f";
    tctx.fillText(`256 Hz · ${st.dropped || 0} dropped · lands ${Math.round(st.lateMs || 0)} ms after`, 8 * d, top + laneH * 4 + 12 * d);
    if (fixLine) { tctx.fillStyle = "#b4442a"; const words = fixLine.split(" "); let line = "", ly = top + laneH * 4 + 26 * d;
      for (const w of words) { const tl = line ? line + " " + w : w; if (tctx.measureText(tl).width > W - 16 * d && line) { tctx.fillText(line, 8 * d, ly); ly += 12 * d; line = w; } else line = tl; } if (line) tctx.fillText(line, 8 * d, ly); } }
  // dock under the sheet's bottom edge, centred on the pen, so it never covers data; if the sheet bottom is off-screen, pin to the stage bottom
  function placeTrace(hx, hy) { if (!trace.classList.contains("show")) return; const r = stage.getBoundingClientRect(); const bottom = (cam.ty + sheetH() * cam.s) / dpr;
    const x = Math.max(12, Math.min(r.width - 272, hx - 130)), y = Math.min(r.height - 174, bottom + 14); trace.style.transform = `translate3d(${x}px,${y}px,0)`; }
  $("#save").onclick = () => { if (!R || !E.n) return; stateEl.textContent = "exporting poster…"; setTimeout(() => { const img = R.renderPoster(2, WW, sheetH()); const f = document.createElement("canvas"); f.width = img.width; f.height = img.height; f.getContext("2d").putImageData(img, 0, 0);
      if (S.firstCell > 0) { const fx = f.getContext("2d"); fx.fillStyle = "#fff"; fx.fillRect(0, 0, S.firstCell * o.pitch * 2, o.pitch * 2); }   // before the session started: paper, not haze
      const P = c => { let lo = 0, hi = E.n; while (lo < hi) { const m = (lo + hi) >> 1; if (S.cellOf[m] < c) lo = m + 1; else hi = m; } return Math.min(lo, E.n - 1); };
      const notes = [...noteEls.values()].map(el => el._a).sort((p, q) => p.i0 - q.i0); const NW = 360, Wp = WW, Hp = sheetH(), c = document.createElement("canvas"); c.width = (Wp + NW + 80) * 2; c.height = (Hp + 140) * 2; const x = c.getContext("2d"); x.scale(2, 2);
      x.fillStyle = "#fff"; x.fillRect(0, 0, c.width, c.height); x.drawImage(f, 40, 40, Wp, Hp); x.save(); x.translate(40, 40); T.drawNotes(x, notes, null, opts, Wp + 24, NW - 24, clock); x.restore();
      x.fillStyle = "#222"; x.font = "bold 13px Helvetica"; x.fillText(`Recording ${clock(S.firstCell || 0)} – ${clock(cells())}${S.kind === "sim" ? " · simulated test data" : ""}`, 40, Hp + 74);
      const a = document.createElement("a"); a.download = `eeg-tapestry-${new Date().toISOString().slice(0, 16)}.png`; a.href = c.toDataURL("image/png"); a.click(); onData(); }, 30); };
  // ---------------- boot ----------------
  resize(); setTarget(fitWidth(), false);
  const data = await loadReplay();
  if (BENCH) return bench(data);
  newSession("replay", "replay · EEGMAT (36 people)"); queue = data; qi = 0; onData(); invalidate(true);
  if (Q.get("src") === "sim") startLive("sim");
  window.__cellToClient = c => { const [x, y] = toCss(c); const r = stage.getBoundingClientRect(); return [r.left + x, r.top + y]; };
  window.__app = { get S() { return S; }, get E() { return E; }, get live() { return live; }, cells, get raf() { return raf; }, tags: () => tags, clock };

  // ---------------- bench: deterministic camera journey, per-frame work ----------------
  async function bench(data) {
    newSession("replay", "bench"); addSeconds(data.map((p, j) => ({ t: S0 + j, bands: p.bands, valid: true })), -1); const frames = +(Q.get("frames") || 480), fin = Q.get("finish") !== "0"; const fa = fitAll(), fw = fitWidth();
    const wait = () => new Promise(r => requestAnimationFrame(r));
    const deep0 = fw.s * 9, H0 = sheetH();
    function journeyCam(t) { let s, cy; if (t < .3) { const u = t / .3; s = fa.s * Math.pow(deep0 / fa.s, u); cy = H0 * .2; } else if (t < .7) { const u = (t - .3) / .4; s = deep0; cy = H0 * (.2 + .6 * u); } else { const u = (t - .7) / .3; s = deep0 * Math.pow(fa.s / deep0, u); cy = H0 * (.8 - .3 * u); }
      cam.s = s; cam.tx = (cssW * dpr) / 2 - (WW * .5 + Math.sin(t * 6.28) * WW * .25) * s; cam.ty = (cssH * dpr) / 2 - cy * s; moving = true; } for (let i = 0; i < 10; i++) { render(); if (R && fin) R.finish(); await wait(); }
    if (Q.has("shot")) { journeyCam(+Q.get("shot")); moving = false; for (let i = 0; i < 3; i++) { render(); drawOverlay(); await wait(); } document.title = "SHOT"; window.__bench = { shot: true }; return; }
    if (Q.get("warm") === "1") for (let f = 0; f < frames; f++) { const t = f / (frames - 1); journeyCam(t); render(); await wait(); }
    if (R && Q.get("drain") !== "0") { for (let i = 0; i < 3; i++) { journeyCam(0); render(); R.gl.readPixels(0, 0, 1, 1, R.gl.RGBA, R.gl.UNSIGNED_BYTE, new Uint8Array(4)); await wait(); } } // drain queued GPU work so frame 1 doesn't pay for warm-up
    const work = [], rafs = [], ovs = [], tilesT = [], phases = []; let fb = 0, made = 0, prev = performance.now(); const deep = fw.s * 9, H = sheetH();
    for (let f = 0; f < frames; f++) { const t = f / (frames - 1);
      // fit-all -> zoom 9x into upper third -> pan down the sheet -> zoom back out
      journeyCam(t);
      await wait(); const t0 = performance.now(); rafs.push(t0 - prev); prev = t0; benchProbe = {};
      let tOv = 0, ph = [0, 0, 0, 0]; if (ARM !== "none") { render(); const t1 = performance.now(); ph[0] = t1 - t0; drawOverlay(); const t2 = performance.now(); if (Q.get("ovsync") === "1") octx.getImageData(0, 0, 1, 1); /* bench-only readback: first call costs ~14 ms (canvas demoted to CPU); the app never reads back */ const t3 = performance.now(); ph[1] = t2 - t1; ph[2] = t3 - t2; tOv = t3 - t1; placeFx(); }
      ovs.push(tOv); if (benchProbe.tiles) tilesT.push(benchProbe.tiles - t0);
      const t4 = performance.now(); if (R && fin) { const px = new Uint8Array(4); R.gl.readPixels(0, 0, 1, 1, R.gl.RGBA, R.gl.UNSIGNED_BYTE, px); } else if (c2 && fin) c2.getContext("2d").getImageData(0, 0, 1, 1); ph[3] = performance.now() - t4;
      if (f < 4) phases.push(ph.map(v => +v.toFixed(2)));
      work.push(performance.now() - t0); if (lastTiles) { fb += lastTiles.fallback > 0 ? 1 : 0; made += lastTiles.rendered; } }
    const pct = (a, q) => { const b = a.slice().sort((x, y) => x - y); return b[Math.min(b.length - 1, Math.floor(q * (b.length - 1)))]; };
    window.__bench = { arm: ARM, cull: Q.get("cull") !== "0", dpr, size: [glc.width || c2.width, glc.height || c2.height], n: E.n, renderer: R ? R.info.renderer : "canvas2d",
      overlay: { p50: pct(ovs, .5), p95: pct(ovs, .95) }, tilePhase: tilesT.length ? { p50: pct(tilesT, .5), p95: pct(tilesT, .95) } : null, tiled: TILED, fallbackFrames: fb, tilesRendered: made, work: { p50: pct(work, .5), p95: pct(work, .95), max: Math.max(...work), top: work.map((w, i) => [i, +w.toFixed(1)]).sort((x, y) => y[1] - x[1]).slice(0, 4) }, raf: { p50: pct(rafs, .5), p95: pct(rafs, .95) }, phases };
    document.title = "BENCH DONE"; }
})();
