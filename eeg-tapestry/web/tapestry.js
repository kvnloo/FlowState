// EEG tapestry renderer. One point = 1 s = 8 nested circles; 60 points per row.
// Mechanism (from native inspo crops): white paper, normal alpha ("source-over"),
// hard edges, bands drawn GLOBALLY back-to-front (all delta, then all theta, ...),
// and slow-band radii many grid pitches wide so their overlap forms the cloud field.
(function (root) {
  const BANDS = ["delta", "theta", "low_alpha", "high_alpha", "low_beta", "high_beta", "low_gamma", "high_gamma"];
  const COLOR = { delta: [221, 10, 10], theta: [255, 133, 0], low_alpha: [252, 234, 1], high_alpha: [88, 237, 20],
    low_beta: [22, 202, 244], high_beta: [2, 42, 186], low_gamma: [111, 91, 163], high_gamma: [229, 12, 188] };
  const ALPHA = { delta: 0.2, theta: 0.4 }; // others 0.5 (colors.jpg)
  // Tunables (hill-climbed). rmax = radius in grid pitches at the band's p95; floor = radius at p5.
  const DEFAULTS = {
    cols: 60, pitch: 14.7, paper: "#ffffff",
    rmax: { delta: 4.2, theta: 2.6, low_alpha: 1.5, high_alpha: 1.1, low_beta: 0.55, high_beta: 0.42, low_gamma: 0.3, high_gamma: 0.22 },
    floor: { delta: 0.25, theta: 0.2, low_alpha: 0.12, high_alpha: 0.1, low_beta: 0.07, high_beta: 0.06, low_gamma: 0.05, high_gamma: 0.045 },
    gamma: 1.6,      // >1 = most circles small, few large (inspo size distribution)
    burst: 3.0,      // max multiple of rmax for outliers above p95 (sudden "much bigger" circles)
    window: 1800,    // seconds used for per-band normalization (rolling, session-relative)
  };

  // Optional causal smoothing of log power per band (EMA over ~smooth[b] seconds). Live-compatible: never looks ahead.
  function smoothPoints(points, o) {
    if (!o.smooth) return points; const st = {}, out = new Array(points.length);
    for (let i = 0; i < points.length; i++) { const p = points[i], nb = {};
      for (const b of BANDS) { const x = p.bands[b]; const L = Math.log10(x > 0 ? x : 1e-9); const tau = o.smooth[b] || 0;
        if (!tau) { nb[b] = x; continue; } const a = 1 / tau; st[b] = st[b] === undefined ? L : st[b] + a * (L - st[b]); nb[b] = Math.pow(10, st[b]); }
      out[i] = Object.assign({}, p, { bands: nb }); }
    return out;
  }
  function quantiles(vals, qs) { const v = vals.slice().sort((a, b) => a - b); return qs.map(q => v[Math.min(v.length - 1, Math.max(0, Math.floor(q * (v.length - 1))))]); }

  // Per-band log-power normalization -> u in [0, burst]; computed over a trailing window for each point.
  function normalizer(points, o) {
    // Giants are CAUSAL and sticky (same rule live and on the poster): a second can bloom only if its band is beyond the
    // session's rare-event quantile so far, after a baseline period, and at most once per giantSep seconds.
    const nf = normalizer0(points, o); const sep = o.giantSep ?? 1800, minN = o.giantMinN ?? 300, pick = new Map(); let last = -1e9;
    for (let i = minN; i < points.length; i++) { if (i - last < sep) continue; let best = -1, bk = -1;
      for (let k = 0; k < 8; k++) { const z = nf.gz(i, BANDS[k]); if (z > best) { best = z; bk = k; } }
      if (best > 0) { pick.set(i * 8 + bk, best); last = i; } }
    nf.giant = (i, b) => pick.has(i * 8 + BANDS.indexOf(b)) ? pick.get(i * 8 + BANDS.indexOf(b)) : -1; return nf;
  }
  function normalizer0(points, o) {
    const lo = {}, hi = {};
    const stats = (from, to) => { const r = {}; for (const b of BANDS) { const v = []; for (let i = from; i < to; i++) { const x = points[i].bands[b]; if (x > 0) v.push(Math.log10(x)); } const [a, c, gq] = v.length ? quantiles(v, [0.05, 0.95, o.giantQ ?? 0.9995]) : [0, 1, 9]; r[b] = [a, Math.max(c - a, 1e-6), gq]; } return r; };
    // recompute stats every 60 s over trailing window (live-compatible: never looks ahead)
    const cache = []; let gzf;
    // window > 0: trailing window (adapts, can flatten long state changes); window = 0: expanding session baseline
    for (let i = 0; i < points.length; i += 60) cache.push(stats(o.window > 0 ? Math.max(0, i + 60 - o.window) : 0, Math.min(points.length, Math.max(i + 60, 300))));
    gzf = (i, b) => { const s = cache[Math.floor(i / 60)][b]; const x = points[i].bands[b]; if (!(x > 0)) return -1; return (Math.log10(x) - s[2]) / s[1]; };
    if (o.norm === "hybrid" || o.norm === "shared") { // one log scale pooled over ALL bands: keeps the 1/f hierarchy (delta >> gamma) and state contrast
      const sh = [];
      for (let i = 0; i < points.length; i += 60) { const from = o.window > 0 ? Math.max(0, i + 60 - o.window) : 0, to = Math.min(points.length, Math.max(i + 60, 300)); const v = [];
        for (let k = from; k < to; k += 2) for (const b of BANDS) { const x = points[k].bands[b]; if (x > 0) v.push(Math.log10(x)); }
        const [a, c] = quantiles(v, [o.qlo ?? 0.02, o.qhi ?? 0.995]); sh.push([a, Math.max(c - a, 1e-6)]); }
      const w = o.norm === "shared" ? 1 : (o.mix ?? 0.5);
      const hf = (i, b) => { const x = points[i].bands[b]; if (!(x > 0)) return 0; const L = Math.log10(x);
        const s = sh[Math.floor(i / 60)], p = cache[Math.floor(i / 60)][b];
        return Math.max(0, w * (L - s[0]) / s[1] + (1 - w) * (L - p[0]) / p[1]); };
      hf.gz = gzf; return hf;
    }
    const linB = o.lin || {};  // per-band linear mode: u = (P / P_q)^lin  (lin 0.5 = circle AREA proportional to power)
    const f = (i, b) => { const s = cache[Math.floor(i / 60)][b]; const x = points[i].bands[b]; if (!(x > 0)) return 0;
      if (linB[b]) return Math.pow(x / Math.pow(10, s[0] + s[1] * (o.linQ ?? 0.6)), linB[b]);
      return Math.max(0, (Math.log10(x) - s[0]) / s[1]); };
    f.gz = gzf; return f;
  }

  function radius(u, b, o, gz) {
    const p = o.pitch; const g = (o.gammaB && o.gammaB[b]) || o.gamma;
    const base = o.floor[b] + (o.rmax[b] - o.floor[b]) * Math.pow(Math.min(u, 1), g);
    const bc = (o.burstB && o.burstB[b]) ?? o.burst;
    const extra = u > 1 ? o.rmax[b] * Math.min(bc - 1, Math.pow(u - 1, 1.3) * 2.2) : 0;
    // rare giants: far-tail events (movement, arousal, artefact) become discs many rows wide, as in the inspo's edges
    if (o.giant && gz > 0 && !o.giantNested) return Math.max((base + extra) * p, o.giant * p * (0.5 + 0.5 * Math.min(1, gz * 4)) * (o.giantB?.[b] ?? 1));
    return (base + extra) * p;
  }

  // A giant is the whole wavelet blooming from its event band inward: ring k at R, faster rings nested inside (icon geometry).
  function drawGiants(ctx, norm, n, o) {
    for (let i = 0; i < n; i++) for (let k = 0; k < 8; k++) { const z = norm.giant(i, BANDS[k]); if (z < 0) continue;
      const [x, y] = layout(i, o); const R = o.giant * o.pitch * (0.5 + 0.5 * Math.min(1, z * 4));
      for (let j = k; j < 8; j++) { const b = BANDS[j]; const [r, g, bl] = COLOR[b]; ctx.fillStyle = `rgba(${r},${g},${bl},${o.giantAlpha ?? (ALPHA[b] ?? 0.5)})`;
        const rr = R * Math.pow(o.giantShrink ?? 0.78, j - k) * (0.6 + 0.4 * Math.min(1, norm(i, b))); ctx.beginPath(); ctx.arc(x, y, rr, 0, Math.PI * 2); ctx.fill(); } }
  }
  function layout(i, o) { return [(i % o.cols) * o.pitch + o.pitch / 2, Math.floor(i / o.cols) * o.pitch + o.pitch / 2]; }

  // Full render (poster). Live mode appends incrementally via drawRange on per-band layer canvases.
  function render(canvas, points, opts) {
    const o = Object.assign({}, DEFAULTS, opts || {}); o.rmax = Object.assign({}, DEFAULTS.rmax, (opts || {}).rmax); o.floor = Object.assign({}, DEFAULTS.floor, (opts || {}).floor);
    const rows = Math.ceil(points.length / o.cols), W = Math.round(o.cols * o.pitch), H = Math.round(rows * o.pitch);
    const d = o.dpr || 1; canvas.width = W * d; canvas.height = H * d; canvas.style.width = W + "px"; canvas.style.height = H + "px";
    const ctx = canvas.getContext("2d"); ctx.setTransform(d, 0, 0, d, 0, 0);
    ctx.fillStyle = o.paper; ctx.fillRect(0, 0, W, H);
    points = smoothPoints(points, o); const norm = normalizer(points, o);
    for (const b of BANDS) { // GLOBAL band order: slow bands underneath everything
      const [r, g, bl] = COLOR[b]; ctx.fillStyle = `rgba(${r},${g},${bl},${ALPHA[b] ?? 0.5})`;
      for (let i = 0; i < points.length; i++) { const [x, y] = layout(i, o); const rr = radius(norm(i, b), b, o, norm.giant(i, b)); if (rr < 0.3) continue; ctx.beginPath(); ctx.arc(x, y, rr, 0, Math.PI * 2); ctx.fill(); }
    }
    if (o.giant && o.giantNested) drawGiants(ctx, norm, points.length, o);
    return { W, H, rows, o };
  }

  // Reference geometry (batch): exactly what render() draws, as data. Used to verify the incremental GPU engine.
  function geometry(points, opts) {
    const o = merge(opts); points = smoothPoints(points, o); const norm = normalizer(points, o);
    const bands = BANDS.map(b => { const a = []; for (let i = 0; i < points.length; i++) { const [x, y] = layout(i, o); const rr = radius(norm(i, b), b, o, norm.giant(i, b)); if (rr >= 0.3) a.push(i, x, y, rr); } return a; });
    const giants = []; if (o.giant && o.giantNested) for (let i = 0; i < points.length; i++) for (let k = 0; k < 8; k++) { const z = norm.giant(i, BANDS[k]); if (z < 0) continue;
      const [x, y] = layout(i, o); const R = o.giant * o.pitch * (0.5 + 0.5 * Math.min(1, z * 4));
      for (let j = k; j < 8; j++) giants.push(i, x, y, R * Math.pow(o.giantShrink ?? 0.78, j - k) * (0.6 + 0.4 * Math.min(1, norm(i, BANDS[j]))), j); }
    return { bands, giants };
  }
  function merge(opts) { const o = Object.assign({}, DEFAULTS, opts || {}); o.rmax = Object.assign({}, DEFAULTS.rmax, (opts || {}).rmax); o.floor = Object.assign({}, DEFAULTS.floor, (opts || {}).floor); return o; }

  // Live: one canvas per band stacked in band order (DOM order = global back-to-front order),
  // so appending a new second never paints a slow band over older fast-band dots.
  function Live(container, opts) {
    const o = merge(opts); const d = o.dpr || window.devicePixelRatio || 1; const pts = []; let norm = null, lastNormAt = -1, sm = pts;
    container.style.position = "relative"; container.style.background = o.paper; container.style.overflow = "hidden";
    const layers = BANDS.map(b => { const c = document.createElement("canvas"); c.style.position = "absolute"; c.style.left = c.style.top = "0"; container.appendChild(c); return c; });
    const W = Math.round(o.cols * o.pitch); let rowsAlloc = 0;
    function alloc(rows) { if (rows <= rowsAlloc) return false; rowsAlloc = Math.max(rows, rowsAlloc * 2, 30); const H = Math.round(rowsAlloc * o.pitch);
      for (const c of layers) { c.width = W * d; c.height = H * d; c.style.width = W + "px"; c.style.height = H + "px"; } container.style.width = W + "px"; container.style.height = H + "px"; return true; }
    function drawOne(i) { const [x, y] = layout(i, o);
      BANDS.forEach((b, k) => { const ctx = layers[k].getContext("2d"); ctx.setTransform(d, 0, 0, d, 0, 0); const [r, g, bl] = COLOR[b]; ctx.fillStyle = `rgba(${r},${g},${bl},${ALPHA[b] ?? 0.5})`;
        const rr = radius(norm(i, b), b, o, norm.giant(i, b)); if (rr >= 0.3) { ctx.beginPath(); ctx.arc(x, y, rr, 0, Math.PI * 2); ctx.fill(); } }); }
    function redrawAll() { for (const c of layers) c.getContext("2d").clearRect(0, 0, c.width, c.height); for (let i = 0; i < pts.length; i++) drawOne(i);
      if (o.giant && o.giantNested) { const ctx = layers[7].getContext("2d"); ctx.setTransform(d, 0, 0, d, 0, 0); drawGiants(ctx, norm, pts.length, o); } }
    return {
      points: pts, opts: o,
      push(p) { pts.push(p); const grew = alloc(Math.ceil(pts.length / o.cols)); container.style.height = Math.ceil(pts.length / o.cols) * o.pitch + "px";
        // re-normalize every 60 s (expanding baseline) and repaint; else append just this second
        if (!norm || pts.length - lastNormAt >= 60 || grew) { sm = smoothPoints(pts, o); norm = normalizer(sm, o); lastNormAt = pts.length; redrawAll(); } else { sm = smoothPoints(pts, o); norm = normalizer(sm, o); drawOne(pts.length - 1); } },
      snapshot() { const c = document.createElement("canvas"); c.width = layers[0].width; c.height = Math.round(Math.ceil(pts.length / o.cols) * o.pitch * d); const x = c.getContext("2d"); x.fillStyle = o.paper; x.fillRect(0, 0, c.width, c.height); for (const l of layers) x.drawImage(l, 0, 0); return c; },
    };
  }

  // ---------- annotations (the inspo's right-hand notes column) ----------
  // Auto notes only DESCRIBE band changes (which colours grew/shrank), per minute vs the session's own baseline.
  // What you were doing comes from user tags ({i, title, text}); the poster merges both.
  const GROUPS = { slow: ["delta", "theta"], alpha: ["low_alpha", "high_alpha"], beta: ["low_beta", "high_beta"], gamma: ["low_gamma", "high_gamma"] };
  const SAY = {
    focus: ["Alpha reducing, gamma growing", "Yellow and green circles shrink while purple circles grow, compared with your previous 10 minutes."],
    betagamma: ["Beta, gamma growing", "Blue and purple circles are bigger than in your previous 10 minutes. Jaw or face tension also shows up here."],
    alpha: ["Alpha growing", "Yellow and green circles are bigger than in your previous 10 minutes. Closing your eyes often does this; not yet checked on your head."],
    slow: ["Theta, delta growing", "Red and orange circles spread. On a headband this is mostly eye movement and blinks."],
  };
  function annotate(points, opts, tags, giantList) {
    const o = merge(opts); const pts = smoothPoints(points, { smooth: Object.fromEntries(BANDS.map(b => [b, o.noteSmooth ?? 6])) }); const n = pts.length, out = [];   // fixed 6 s smoothing, independent of render
    const W = o.noteWin ?? 30, H = o.noteBase ?? 600, th = o.noteZ ?? 1.0;   // 30 s steps, trailing 10-min baseline (causal)
    if (n >= H + W) {
      const win = []; for (let s = 0; s + W <= n; s += W) { const m = {}; for (const g in GROUPS) { let v = 0, c = 0; for (let i = s; i < s + W; i++) for (const b of GROUPS[g]) { const x = pts[i].bands[b]; if (x > 0) { v += Math.log10(x); c++; } } m[g] = v / c; } win.push(m); }
      const K = H / W; let cur = null;
      for (let k = K; k < win.length; k++) {
        const z = {}; for (const g in GROUPS) { const v = win.slice(k - K, k).map(m => m[g]).sort((a, b) => a - b), med = v[v.length >> 1]; const mad = v.map(x => Math.abs(x - med)).sort((a, b) => a - b)[v.length >> 1] || 1e-6; z[g] = (win[k][g] - med) / (1.4826 * mad); }
        let lab = null;
        if (z.alpha < -th && z.gamma > th * 0.5) lab = "focus";
        else if (z.beta > th && z.gamma > th * 0.5) lab = "betagamma";
        else if (z.alpha > th) lab = "alpha";
        else if (z.slow > th && z.beta < 0) lab = "slow";
        if (cur && cur.kind === lab && cur.i1 === k * W) cur.i1 = (k + 1) * W; else { if (cur) out.push(cur); cur = lab ? { kind: lab, i0: k * W, i1: (k + 1) * W } : null; }
      }
      if (cur) out.push(cur);
    }
    const notes = out.filter(a => a.i1 - a.i0 >= (o.noteMin ?? 60)).map(a => ({ i0: a.i0, i1: a.i1, title: SAY[a.kind][0], text: SAY[a.kind][1], auto: true }));
    const NAMES = { delta: "red", theta: "orange", low_alpha: "yellow", high_alpha: "green", low_beta: "cyan", high_beta: "blue", low_gamma: "purple", high_gamma: "magenta" };
    if (giantList) for (const [i, b] of giantList) notes.push({ i0: i, i1: i, title: "Sudden burst", text: `A much bigger ${NAMES[b]} circle appears suddenly: usually movement or a blink.`, auto: true, glyph: i });
    else if (n) { const norm = normalizer(pts, o); for (let i = 0; i < n; i++) for (const b of BANDS) if (norm.giant(i, b) > 0) notes.push({ i0: i, i1: i, title: "Sudden burst", text: `A much bigger ${({ delta: "red", theta: "orange", low_alpha: "yellow", high_alpha: "green", low_beta: "cyan", high_beta: "blue", low_gamma: "purple", high_gamma: "magenta" })[b]} circle appears suddenly: usually movement or a blink.`, auto: true, glyph: i }); }
    for (const t of tags || []) notes.push({ i0: t.i, i1: t.i1 ?? t.i, title: t.title, text: t.text || "", tag: true, glyph: t.i });
    notes.sort((a, b) => a.i0 - b.i0);
    const last = {}; return notes.filter(a => { if (a.tag) return true; const k = a.title; if (last[k] !== undefined && a.i0 - last[k] < (o.noteGap ?? 180)) { last[k] = a.i1; return false; } last[k] = a.i1; return true; });
  }
  // Draw the notes column onto ctx at x0 (poster export / node renderer). Rows map 1:1 to field rows.
  function drawNotes(ctx, notes, points, o, x0, width, fmt) {
    o = merge(o); const P = o.pitch; let lastY = -1e9; ctx.textBaseline = "top";
    for (const a of notes) {
      const y0 = Math.floor(a.i0 / o.cols) * P + P / 2, y1 = Math.floor(Math.max(a.i0, a.i1 - 1) / o.cols) * P + P / 2;
      ctx.strokeStyle = "#333"; ctx.lineWidth = 1; ctx.beginPath();
      if (a.i1 > a.i0 + 1) { ctx.moveTo(x0 + 8, y0); ctx.lineTo(x0, y0); ctx.lineTo(x0, y1); ctx.lineTo(x0 + 8, y1); } else { ctx.moveTo(x0 - 6, y0); ctx.lineTo(x0 + 8, y0); }
      ctx.stroke();
      const y = Math.max(y0 - 4, lastY + 8); let x = x0 + 18;
      if (y - y0 > 10) { ctx.strokeStyle = "#bbb"; ctx.beginPath(); ctx.moveTo(x0 + 8, y0); ctx.lineTo(x0 + 14, y + 6); ctx.lineTo(x0 + 16, y + 6); ctx.stroke(); }
      if (a.glyph !== undefined) { const r = 13, cx = x + r, cy = y + r; BANDS.forEach((b, k) => { ctx.strokeStyle = `rgb(${COLOR[b]})`; ctx.beginPath(); ctx.arc(cx, cy, r * (1 - k / 9), 0, 7); ctx.stroke(); }); x += 2 * r + 10; }
      ctx.fillStyle = "#222"; ctx.font = "bold 12px Helvetica, Arial, sans-serif"; ctx.fillText(fmt(a.i0) + (a.i1 > a.i0 + 1 ? " – " + fmt(a.i1) : ""), x, y);
      ctx.font = "bold 12px Helvetica, Arial, sans-serif"; ctx.fillText(a.title, x, y + 16);
      ctx.font = "11px Helvetica, Arial, sans-serif"; ctx.fillStyle = "#555";
      const words = (a.text || "").split(" "); let line = "", ly = y + 32; const maxW = width - (x - x0) - 6;
      for (const w of words) { const t = line ? line + " " + w : w; if (ctx.measureText(t).width > maxW && line) { ctx.fillText(line, x, ly); ly += 14; line = w; } else line = t; }
      if (line) { ctx.fillText(line, x, ly); ly += 14; } lastY = ly;
    }
  }

  root.Tapestry = { BANDS, COLOR, ALPHA, DEFAULTS, render, Live, merge, annotate, drawNotes, geometry, layout };
})(typeof window !== "undefined" ? window : globalThis);
