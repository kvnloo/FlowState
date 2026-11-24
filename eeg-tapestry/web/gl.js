// WebGL2 instanced renderer for the tapestry. One quad per circle, coverage computed in the fragment shader
// (analytic 1-px AA), premultiplied source-over on white = Canvas2D's look. Band-major segments keep the global
// back-to-front order (all delta, then theta, ... then nested giants). Rows are contiguous per band, so view culling
// is just an index range per band.
(function (root) {
  const T = root.Tapestry, BANDS = T.BANDS, NB = 8;
  const VS = `#version 300 es
  precision highp float;
  layout(location=0) in vec2 a_corner;
  layout(location=1) in vec4 a_inst;   // x, y, r (world px), birth (s, <0 = no anim)
  layout(location=2) in vec4 a_col;    // premultiplied rgba
  uniform vec3 u_view;                 // scale (device px per world px), tx, ty (device px)
  uniform vec2 u_res; uniform float u_time, u_dur, u_dim, u_w;
  out vec2 v_p; out float v_R; out vec4 v_col;
  void main(){
    float g = 1.0;
    if (a_inst.w >= 0.0) { float t = max(u_time - a_inst.w, 0.0); g = 1.0 - (1.0 + u_w * t) * exp(-u_w * t); } // critically damped: never passes measured size
    float R = a_inst.z * g * u_view.x;                       // device px
    if (a_inst.z < 0.3 || R < 0.05) { gl_Position = vec4(2.0, 2.0, 2.0, 1.0); return; }
    vec2 c = a_inst.xy * u_view.x + u_view.yz;
    vec2 p = c + a_corner * (R + 1.0);
    v_p = a_corner * (R + 1.0); v_R = R; v_col = a_col * u_dim;
    gl_Position = vec4(p / u_res * 2.0 - 1.0, 0.0, 1.0); gl_Position.y = -gl_Position.y;
  }`;
  const FS = `#version 300 es
  precision highp float;
  in vec2 v_p; in float v_R; in vec4 v_col; out vec4 o;
  void main(){ float a = clamp(v_R - length(v_p) + 0.5, 0.0, 1.0); if (a <= 0.0) discard; o = v_col * a; }`;

  function Renderer(canvas, engine) {
    const gl = canvas.getContext("webgl2", { premultipliedAlpha: true, alpha: true, antialias: false, preserveDrawingBuffer: false, powerPreference: "high-performance", desynchronized: false });
    if (!gl) throw new Error("WebGL2 unavailable");
    const sh = (t, s) => { const x = gl.createShader(t); gl.shaderSource(x, s); gl.compileShader(x); if (!gl.getShaderParameter(x, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(x)); return x; };
    const prog = gl.createProgram(); gl.attachShader(prog, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, FS)); gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(prog));
    const U = n => gl.getUniformLocation(prog, n); const uView = U("u_view"), uRes = U("u_res"), uTime = U("u_time"), uDur = U("u_dur"), uDim = U("u_dim"), uW = U("u_w");
    // per-band landing time (s): slow bands swell, fast bands snap. w = 6.6/dur reaches 99% at dur.
    const DUR = [0.6, 0.4, 0.25, 0.25, 0.15, 0.15, 0.07, 0.07], GIANT_DUR = 1.0;
    const vao = gl.createVertexArray(); gl.bindVertexArray(vao);
    const quad = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, quad); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    gl.enableVertexAttribArray(0); gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);
    const ib = gl.createBuffer(), gb = gl.createBuffer();
    const o = engine.o, info = { renderer: "?" };
    try { const ext = gl.getExtension("WEBGL_debug_renderer_info"); info.renderer = ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER); } catch (e) {}
    let cap = 0, inst = null, n = 0, maxR = new Float32Array(NB), births = null, giants = new Float32Array(0), giantCount = 0;
    const colors = BANDS.map(b => { const [r, g, bl] = T.COLOR[b]; const a = T.ALPHA[b] ?? 0.5; return [r / 255 * a, g / 255 * a, bl / 255 * a, a]; });
    const dim = new Float32Array(NB).fill(1); let giantDim = 1;

    function ensure(need) { if (need <= cap) return false; cap = Math.max(4096, 1 << Math.ceil(Math.log2(need * 1.25)));
      const ni = new Float32Array(cap * NB * 4); if (inst) for (let b = 0; b < NB; b++) ni.set(inst.subarray(b * (inst.length / NB), b * (inst.length / NB) + n * 4), b * cap * 4);
      inst = ni; const nb = new Float32Array(cap); if (births) nb.set(births.subarray(0, n)); births = nb;
      gl.bindBuffer(gl.ARRAY_BUFFER, ib); gl.bufferData(gl.ARRAY_BUFFER, inst, gl.DYNAMIC_DRAW); return true; }

    // sync instance data for points [from, engine.n). `birthAt` (s) stamps newly appended points for the grow animation.
    let cellOf = null, marks = [];
    const cx = c => (c % o.cols) * o.pitch + o.pitch / 2, cy = c => ((c / o.cols) | 0) * o.pitch + o.pitch / 2;
    // cellOfArr: engine point index -> sheet cell (time-keyed; gaps allowed). markList: [{cell, birth}] excluded seconds.
    function sync(from, birthAt, cellOfArr, markList) {
      if (cellOfArr) cellOf = cellOfArr; if (markList) marks = markList;
      const C = i => cellOf ? cellOf[i] : i;
      const N = engine.n, R = engine.R, oldN = n; const grew = ensure(N);
      for (let i = oldN; i < N; i++) births[i] = birthAt ?? -1;
      for (let b = 0; b < NB; b++) { const base = b * cap * 4;
        for (let i = from; i < N; i++) { const k = base + i * 4; const r = R[i * NB + b];
          inst[k] = cx(C(i)); inst[k + 1] = cy(C(i)); inst[k + 2] = r; inst[k + 3] = births[i]; if (r > maxR[b]) maxR[b] = r; } }
      if (N > from) invalidateFrom(((C(Math.min(from, Math.max(0, N - 1))) / o.cols) | 0) * o.pitch - (Math.max(...maxR) + o.giant * o.pitch + o.pitch));
      n = N; gl.bindBuffer(gl.ARRAY_BUFFER, ib);
      if (grew) gl.bufferData(gl.ARRAY_BUFFER, inst, gl.DYNAMIC_DRAW);
      else if (N > from) for (let b = 0; b < NB; b++) gl.bufferSubData(gl.ARRAY_BUFFER, (b * cap + from) * 16, inst, b * cap * 4 + from * 4, (N - from) * 4);
      // giants: tiny, rebuild every sync (births kept per point)
      const gr = engine.giantRings(); const gc = gr.length / 5, M = marks.length; giantCount = gc + M; giants = new Float32Array(giantCount * 8);
      // not-measured marks first (so they recede under giants): one small grey dot, premultiplied alpha
      for (let j = 0; j < M; j++) { const m = marks[j], gA = 0.45; giants.set([cx(m.cell), cy(m.cell), o.pitch * 0.18, m.birth ?? -1, 0.55 * gA, 0.53 * gA, 0.50 * gA, gA], j * 8); }
      for (let jj = 0; jj < gc; jj++) { const j = jj + M; const [i, , , r, band] = gr.slice(jj * 5, jj * 5 + 5); const x = cx(C(i)), y = cy(C(i)); const a = o.giantAlpha ?? (T.ALPHA[BANDS[band]] ?? 0.5); const [cr, cg, cb] = T.COLOR[BANDS[band]];
        giants.set([x, y, r, births[i] >= 0 ? births[i] + 0.15 : -1, cr / 255 * a, cg / 255 * a, cb / 255 * a, a], j * 8); }
      gl.bindBuffer(gl.ARRAY_BUFFER, gb); gl.bufferData(gl.ARRAY_BUFFER, giants, gl.DYNAMIC_DRAW);
    }

    let stats = { instances: 0, draws: 0 };
    // cam: {s, tx, ty} in DEVICE px. opts: {cull, time, dur, sheet:[x,y,w,h] device px}
    function draw(cam, opt) { gl.bindFramebuffer(gl.FRAMEBUFFER, null); return scene(canvas.width, canvas.height, cam, opt); }
    let lowTex = null, lowFbo = gl.createFramebuffer(), lowW = 0, lowH = 0;
    function drawSplit(cam, opt) { const W = canvas.width, H = canvas.height, f = opt.lowScale ?? 0.5, lb = opt.lowBands ?? 2;
      const w = Math.max(1, Math.ceil(W * f)), h = Math.max(1, Math.ceil(H * f));
      // allocate once at the largest scale (>= 0.5) and render smaller scales into its corner: no realloc when the scale switches (was an ~18 ms first-frame spike)
      const aw = Math.max(w, Math.ceil(W * 0.5)), ah = Math.max(h, Math.ceil(H * 0.5));
      if (!lowTex || aw !== lowW || ah !== lowH) { if (lowTex) gl.deleteTexture(lowTex); lowTex = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, lowTex); gl.texStorage2D(gl.TEXTURE_2D, 1, gl.RGBA8, aw, ah);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
        lowW = aw; lowH = ah; }
      gl.bindFramebuffer(gl.FRAMEBUFFER, lowFbo); gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, lowTex, 0);
      const k = w / W, lc = { s: cam.s * k, tx: cam.tx * k, ty: cam.ty * k }, sh = opt.sheet;
      scene(w, h, lc, Object.assign({}, opt, { sheet: [sh[0] * k, sh[1] * k, sh[2] * k, sh[3] * k], b0: 0, b1: lb, giants: false, shadow: 0 }));
      gl.bindFramebuffer(gl.FRAMEBUFFER, null);
      const st = scene(W, H, cam, Object.assign({}, opt, { b0: lb, b1: NB, noPaper: true, underlay: () => {
        gl.useProgram(tprog); gl.bindVertexArray(vao); gl.disableVertexAttribArray(1); gl.disableVertexAttribArray(2); gl.uniform2f(tRes, W, H); gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, lowTex);
        gl.uniform4f(tRect, 0, 0, w / k, h / k); gl.uniform2f(tUvs, w / lowW, h / lowH); gl.blendFunc(gl.ONE, gl.ZERO); gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4); gl.enableVertexAttribArray(1); gl.useProgram(prog); gl.bindVertexArray(vao);
        gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA); gl.uniform3f(uView, cam.s, cam.tx, cam.ty); gl.uniform2f(uRes, W, H); } }));
      return st; }
    function drawShadowOnly(sheet, blur) { shadow(sheet, canvas.width, canvas.height, blur); }
    function scene(W, H, cam, opt) {
      gl.viewport(0, 0, W, H);
      const b0 = opt.b0 ?? 0, b1 = opt.b1 ?? NB, giantsOn = opt.giants ?? true;
      if (!opt.noClear) { gl.disable(gl.SCISSOR_TEST); gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT); if (opt.shadow) shadow(opt.sheet, W, H, opt.shadow); }
      const [sx, sy, sw, shh] = opt.sheet; gl.enable(gl.SCISSOR_TEST);
      const x0 = Math.max(0, Math.floor(sx)), y0 = Math.max(0, Math.floor(sy)), x1 = Math.min(W, Math.ceil(sx + sw)), y1 = Math.min(H, Math.ceil(sy + shh));
      if (x1 <= x0 || y1 <= y0) return stats;
      gl.scissor(x0, H - y1, x1 - x0, y1 - y0); if (!opt.noPaper) { gl.clearColor(1, 1, 1, 1); gl.clear(gl.COLOR_BUFFER_BIT); }
      if (opt.underlay) opt.underlay();
      gl.useProgram(prog); gl.bindVertexArray(vao); gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
      gl.uniform3f(uView, cam.s, cam.tx, cam.ty); gl.uniform2f(uRes, W, H); gl.uniform1f(uTime, opt.time || 0); gl.uniform1f(uDur, opt.dur || 0.45);
      gl.bindBuffer(gl.ARRAY_BUFFER, ib); gl.enableVertexAttribArray(1); gl.vertexAttribDivisor(1, 1); gl.disableVertexAttribArray(2);
      const wy0 = -cam.ty / cam.s, wy1 = (H - cam.ty) / cam.s; let inst = 0, draws = 0;
      for (let b = b0; b < b1; b++) { let i0 = 0, i1 = n;
        if (opt.cull !== false) { const m = maxR[b] + 1; i0 = Math.max(0, Math.floor((wy0 - m) / o.pitch) * o.cols); i1 = Math.min(n, (Math.ceil((wy1 + m) / o.pitch) + 1) * o.cols); }
        if (i1 <= i0) continue; const c = colors[b];
        gl.vertexAttrib4f(2, c[0], c[1], c[2], c[3]); gl.uniform1f(uDim, dim[b]); gl.uniform1f(uW, 6.6 / DUR[b]);
        gl.vertexAttribPointer(1, 4, gl.FLOAT, false, 16, (b * cap + i0) * 16);
        gl.drawArraysInstanced(gl.TRIANGLE_STRIP, 0, 4, i1 - i0); inst += i1 - i0; draws++; }
      if (giantCount && giantsOn) { gl.bindBuffer(gl.ARRAY_BUFFER, gb); gl.vertexAttribPointer(1, 4, gl.FLOAT, false, 32, 0); gl.enableVertexAttribArray(2); gl.vertexAttribDivisor(2, 1);
        gl.vertexAttribPointer(2, 4, gl.FLOAT, false, 32, 16); gl.uniform1f(uDim, giantDim); gl.uniform1f(uW, 6.6 / GIANT_DUR); gl.drawArraysInstanced(gl.TRIANGLE_STRIP, 0, 4, giantCount); inst += giantCount; draws++;
        gl.disableVertexAttribArray(2); gl.vertexAttribDivisor(2, 0); }
      stats = { instances: inst, draws }; return stats;
    }
    // ---------------- tile cache (map-style): field rendered once per zoom level into 512px tiles ----------------
    const TS = 512, tiles = new Map(); let tick = 0, tileStats = { rendered: 0, fallback: 0, cached: 0 };
    const tprog = (() => { const p = gl.createProgram();
      gl.attachShader(p, sh(gl.VERTEX_SHADER, `#version 300 es
        layout(location=0) in vec2 a_corner; uniform vec4 u_rect; uniform vec2 u_res; uniform vec2 u_uvs; out vec2 v_uv;
        void main(){ vec2 t = a_corner*0.5+0.5; vec2 p = u_rect.xy + t*u_rect.zw; v_uv = vec2(t.x, 1.0 - t.y) * u_uvs; gl_Position = vec4(p/u_res*2.0-1.0,0.,1.); gl_Position.y = -gl_Position.y; }`));
      gl.attachShader(p, sh(gl.FRAGMENT_SHADER, `#version 300 es
        precision highp float; uniform sampler2D u_tex; in vec2 v_uv; out vec4 o; void main(){ o = texture(u_tex, v_uv); }`)); gl.linkProgram(p); return p; })();
    const tRect = gl.getUniformLocation(tprog, "u_rect"), tRes = gl.getUniformLocation(tprog, "u_res"), tUvs = gl.getUniformLocation(tprog, "u_uvs");
    const fbo = gl.createFramebuffer();
    const sprog = (() => { const p = gl.createProgram();
      gl.attachShader(p, sh(gl.VERTEX_SHADER, `#version 300 es
        layout(location=0) in vec2 a_corner; uniform vec4 u_rect; uniform vec2 u_res; uniform float u_blur; out vec2 v_p;
        void main(){ vec2 c = u_rect.xy + u_rect.zw*0.5, h = u_rect.zw*0.5 + vec2(u_blur*3.0); vec2 p = c + a_corner*h; v_p = p; gl_Position = vec4(p/u_res*2.0-1.0,0.,1.); gl_Position.y=-gl_Position.y; }`));
      gl.attachShader(p, sh(gl.FRAGMENT_SHADER, `#version 300 es
        precision highp float; uniform vec4 u_rect; uniform float u_blur; in vec2 v_p; out vec4 o;
        void main(){ vec2 c = u_rect.xy + u_rect.zw*0.5, h = u_rect.zw*0.5; vec2 d = abs(v_p - c) - h; float dist = length(max(d,0.0)) + min(max(d.x,d.y),0.0);
          float a = 0.16 * (1.0 - smoothstep(-u_blur*0.3, u_blur*2.2, dist)); o = vec4(vec3(60.,40.,20.)/255.*a, a); }`)); gl.linkProgram(p); return p; })();
    const sRect = gl.getUniformLocation(sprog, "u_rect"), sRes = gl.getUniformLocation(sprog, "u_res"), sBlur = gl.getUniformLocation(sprog, "u_blur");
    function shadow(sheet, W, H, blur) { gl.useProgram(sprog); gl.bindVertexArray(vao); gl.disableVertexAttribArray(1); gl.disableVertexAttribArray(2); gl.disable(gl.SCISSOR_TEST);
      gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA); gl.uniform4f(sRect, sheet[0], sheet[1] + blur * 0.3, sheet[2], sheet[3]); gl.uniform2f(sRes, W, H); gl.uniform1f(sBlur, blur);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4); gl.enableVertexAttribArray(1); }
    function levelScale(L, base) { return base * Math.pow(2, L); }
    function tileKey(L, x, y) { return L * 1e8 + y * 1e4 + x; }
    function renderTile(t, base, sheetWorld, opt) {
      if (!t.tex) { t.tex = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, t.tex); gl.texStorage2D(gl.TEXTURE_2D, 1, gl.RGBA8, TS, TS);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE); }
      gl.bindFramebuffer(gl.FRAMEBUFFER, fbo); gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, t.tex, 0);
      const s = levelScale(t.L, base), c = { s, tx: -t.x * TS, ty: -t.y * TS };
      scene(TS, TS, c, { sheet: [sheetWorld[0] * s + c.tx, sheetWorld[1] * s + c.ty, sheetWorld[2] * s, sheetWorld[3] * s], time: opt.time, dur: opt.dur, cull: true });
      t.ver = version; t.anim = animatingUntil() > opt.time - 1.2; tileStats.rendered++; }
    let version = 0, dirtyY = Infinity;  // world y from which content changed since tiles were made
    function invalidateFrom(worldY) { dirtyY = Math.min(dirtyY, worldY); version++; }
    // Composite visible tiles at level L = ceil(log2(cam.s/base)). Missing tiles fall back to a cached coarser level and
    // are rendered within a per-frame budget, so a frame never pays for the whole field.
    function drawTiled(cam, opt) {
      const W = canvas.width, H = canvas.height, base = opt.base, sheetWorld = opt.sheetWorld; tick++; tileStats = { rendered: 0, fallback: 0, cached: 0 };
      // apply data invalidation: tiles whose world y-range reaches below dirtyY are stale
      if (dirtyY < Infinity) { for (const t of tiles.values()) { const s = levelScale(t.L, base); if ((t.y + 1) * TS / s >= dirtyY) t.stale = true; } dirtyY = Infinity; }
      const lf = Math.log2(cam.s / base), L = Math.max(0, opt.levelMode === "ceil" ? Math.ceil(lf - 1e-6) : Math.round(lf + (opt.settled ? 0.5 - 1e-6 : 0))), s = levelScale(L, base), k = cam.s / s;
      const wx0 = -cam.tx / cam.s, wy0 = -cam.ty / cam.s, wx1 = (W - cam.tx) / cam.s, wy1 = (H - cam.ty) / cam.s;
      const sx0 = Math.max(wx0, 0), sx1 = Math.min(wx1, sheetWorld[2]), sy0 = Math.max(wy0, 0), sy1 = Math.min(wy1, sheetWorld[3]);
      gl.bindFramebuffer(gl.FRAMEBUFFER, null); gl.viewport(0, 0, W, H); gl.disable(gl.SCISSOR_TEST); gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT);
      if (opt.shadow) shadow([cam.tx, cam.ty, sheetWorld[2] * cam.s, sheetWorld[3] * cam.s], W, H, opt.shadow);
      if (sx1 <= sx0 || sy1 <= sy0) return tileStats;
      const tx0 = Math.floor(sx0 * s / TS), tx1 = Math.floor((sx1 * s - 1e-3) / TS), ty0 = Math.floor(sy0 * s / TS), ty1 = Math.floor((sy1 * s - 1e-3) / TS);
      const want = [], budget = opt.budget ?? 4; let made = 0;
      const animTail = animatingUntil() > opt.time - 1.2;
      for (let y = ty0; y <= ty1; y++) for (let x = tx0; x <= tx1; x++) want.push([x, y]);
      // centre-out priority
      const cx = (tx0 + tx1) / 2, cy = (ty0 + ty1) / 2; want.sort((a, b) => Math.hypot(a[0] - cx, a[1] - cy) - Math.hypot(b[0] - cx, b[1] - cy));
      const draws = [];
      for (const [x, y] of want) { const key = tileKey(L, x, y); let t = tiles.get(key);
        const needs = !t || t.stale || (t.anim && animTail);
        if (needs && made < budget) { if (!t) { t = { L, x, y }; tiles.set(key, t); } renderTile(t, base, sheetWorld, opt); t.stale = false; made++; }
        if (t && t.tex && !(t.stale && !t.ver)) { t.used = tick; draws.push([t, L]); if (needs && made >= budget) tileStats.fallback++; else tileStats.cached++; continue; }
        // fallback: nearest cached coarser tile covering this one
        let found = false; for (let l = L - 1; l >= 0 && !found; l--) { const f = Math.pow(2, L - l), ct = tiles.get(tileKey(l, Math.floor(x / f), Math.floor(y / f))); if (ct && ct.tex) { ct.used = tick; draws.push([ct, l]); found = true; } }
        tileStats.fallback++; }
      if (opt.probe) { const px = new Uint8Array(4); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); opt.probe.tiles = performance.now(); }
      gl.bindFramebuffer(gl.FRAMEBUFFER, null); gl.viewport(0, 0, W, H); gl.useProgram(tprog); gl.bindVertexArray(vao); gl.disableVertexAttribArray(1); gl.disableVertexAttribArray(2);
      gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA); gl.uniform2f(tRes, W, H); gl.uniform2f(tUvs, 1, 1); gl.activeTexture(gl.TEXTURE0);
      // coarse fallbacks first so fine tiles paint over them
      draws.sort((a, b) => a[1] - b[1]); const seen = new Set();
      for (const [t, l] of draws) { if (seen.has(t)) continue; seen.add(t); const sl = levelScale(l, base), kk = cam.s / sl;
        const r = [t.x * TS * kk + cam.tx, t.y * TS * kk + cam.ty, TS * kk, TS * kk]; gl.scissor(0, 0, W, H);
        gl.bindTexture(gl.TEXTURE_2D, t.tex); gl.uniform4f(tRect, r[0], r[1], r[2], r[3]); gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4); }
      gl.enableVertexAttribArray(1);
      // LRU eviction
      const MAX = opt.maxTiles ?? 220; if (tiles.size > MAX) { const arr = [...tiles.values()].sort((a, b) => (a.used || 0) - (b.used || 0)); for (const t of arr.slice(0, tiles.size - MAX)) { if (t.used === tick) continue; if (t.tex) gl.deleteTexture(t.tex); tiles.delete(tileKey(t.L, t.x, t.y)); } }
      tileStats.pending = want.length - tileStats.cached; tileStats.tiles = tiles.size; return tileStats;
    }
    function prefetch(cam, opt, n) { const W = canvas.width, H = canvas.height, base = opt.base, sw = opt.sheetWorld; let made = 0;
      const lf = Math.log2(cam.s / base), L0 = Math.max(0, Math.round(lf));
      for (const L of [L0, L0 + 1, L0 - 1]) { if (L < 0 || made >= n) continue; const s = levelScale(L, base), pad = 0.5;
        const wx0 = Math.max(0, -cam.tx / cam.s - W / cam.s * pad), wx1 = Math.min(sw[2], (W - cam.tx) / cam.s + W / cam.s * pad), wy0 = Math.max(0, -cam.ty / cam.s - H / cam.s * pad), wy1 = Math.min(sw[3], (H - cam.ty) / cam.s + H / cam.s * pad);
        if (wx1 <= wx0 || wy1 <= wy0) continue;
        for (let y = Math.floor(wy0 * s / TS); y <= Math.floor((wy1 * s - 1e-3) / TS) && made < n; y++) for (let x = Math.floor(wx0 * s / TS); x <= Math.floor((wx1 * s - 1e-3) / TS) && made < n; x++) {
          const key = tileKey(L, x, y); let t = tiles.get(key); if (t && t.tex && !t.stale) continue; if (!t) { t = { L, x, y, used: tick }; tiles.set(key, t); } renderTile(t, base, sw, opt); t.stale = false; made++; } }
      return made; }
    function dropTiles() { for (const t of tiles.values()) if (t.tex) gl.deleteTexture(t.tex); tiles.clear(); }
    function animatingUntil() { let t = -1; for (let i = Math.max(0, n - 600); i < n; i++) if (births[i] > t) t = births[i]; for (const m of marks.slice(-20)) if ((m.birth ?? -1) > t) t = m.birth; return t; }
    function reset() { n = 0; maxR.fill(0); marks = []; cellOf = null; giantCount = 0; giants = new Float32Array(0); if (births) births.fill(-1); dropTiles(); }
    // Poster: draw the whole sheet at `scale` (device px per world px) into an FBO and read it back as ImageData (top-down).
    function renderPoster(scale, sheetW, sheetH) { const W = Math.ceil(sheetW * scale), H = Math.ceil(sheetH * scale);
      const tex = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, tex); gl.texStorage2D(gl.TEXTURE_2D, 1, gl.RGBA8, W, H);
      gl.bindFramebuffer(gl.FRAMEBUFFER, fbo); gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, tex, 0);
      scene(W, H, { s: scale, tx: 0, ty: 0 }, { sheet: [0, 0, W, H], time: 1e9, cull: false });
      const px = new Uint8Array(W * H * 4); gl.readPixels(0, 0, W, H, gl.RGBA, gl.UNSIGNED_BYTE, px); gl.bindFramebuffer(gl.FRAMEBUFFER, null); gl.deleteTexture(tex);
      const img = new ImageData(W, H); for (let y = 0; y < H; y++) img.data.set(px.subarray((H - 1 - y) * W * 4, (H - y) * W * 4), y * W * 4); return img; }
    function setEngine(e) { engine = e; }
    // re-stamp birth times for points [from, n): birthOf(i) -> seconds (used by "while you were away" to pour hidden-time seconds in row by row)
    function restamp(from, birthOf) { if (from >= n) return; for (let i = from; i < n; i++) births[i] = birthOf(i);
      for (let b = 0; b < NB; b++) { const base = b * cap * 4; for (let i = from; i < n; i++) inst[base + i * 4 + 3] = births[i]; }
      gl.bindBuffer(gl.ARRAY_BUFFER, ib); for (let b = 0; b < NB; b++) gl.bufferSubData(gl.ARRAY_BUFFER, (b * cap + from) * 16, inst, b * cap * 4 + from * 4, (n - from) * 4); dropTiles(); }
    return { gl, info, sync, reset, setEngine, restamp, renderPoster, draw, drawTiled, dropTiles, prefetch, drawSplit, get tileStats() { return tileStats; }, dim, setGiantDim: v => giantDim = v, animatingUntil, get n() { return n; }, finish: () => gl.finish(), maxR };
  }
  root.TapestryGL = { Renderer };
})(typeof window !== "undefined" ? window : globalThis);
