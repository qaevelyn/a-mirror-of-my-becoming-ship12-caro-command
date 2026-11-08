(function () {
  if (window.__GG__) return; window.__GG__ = true;
  var doc = document;
  function $(id) { return doc.getElementById(id); }
  function esc(s) { var d = doc.createElement('div'); d.appendChild(doc.createTextNode(String(s == null ? '' : s))); return d.innerHTML; }

  /* ---------- fleet canon (baked from the console's own const FLEET) ---------- */
  var CANON = window.FLEET_CANON || { src: null, ships: [{"n": 1, "name": "DeepSeek RAG", "url": "", "status": "live"}, {"n": 2, "name": "IBM Granite Agentic RAG", "url": "", "status": "live"}, {"n": 3, "name": "IBM Granite RAG", "url": "", "status": "live"}, {"n": 4, "name": "IBM Granite Agentic RAG", "url": "", "status": "live"}, {"n": 5, "name": "Granite + EvidenceFlow", "url": "", "status": "live"}, {"n": 6, "name": "Suite: Ingestion Tools", "url": "https://github.com/qaevelyn/a-mirror-of-my-becoming-suite-ingestion-tools", "status": "live"}, {"n": 7, "name": "msgvault Adapter", "url": "https://github.com/qaevelyn/a-mirror-of-my-becoming-suite-msgvault-adapter", "status": "live"}, {"n": 8, "name": "DV14\u2122: The Box", "url": "", "status": "live"}, {"n": 9, "name": "Radiology Companion\u2122", "url": "", "status": "live"}, {"n": 10, "name": "Overseer\u2122", "url": "", "status": "live"}, {"n": 11, "name": "AWS CCP Study Manual", "url": "https://github.com/qaevelyn/a-mirror-of-my-becoming-ship11-aws-ccp-study-manual", "status": "live"}, {"n": 12, "name": "Caro Command Deck\u2122", "url": "https://github.com/qaevelyn/a-mirror-of-my-becoming-ship12-caro-command", "status": "live"}, {"n": 13, "name": "TriviaGate\u2122", "url": "https://qaevelyn.github.io/a-mirror-of-my-becoming-ship13-triviagate/", "status": "live"}] };
  var SEAL = /seal|draft|planned|concept|pending|stub|future/i;
  function normalize(data) {
    var list = data;
    if (data && typeof data === 'object' && !Array.isArray(data)) list = data.ships || data.fleet || data.vessels || null;
    if (!Array.isArray(list)) return [];
    var seen = {}, res = [];
    list.forEach(function (it) {
      if (!it || typeof it !== 'object') return;
      var n = null, name = '', url = '', status = 'live', k;
      var keys = ['n', 'num', 'number', 'no', 'suite'];
      for (var ki = 0; ki < keys.length; ki++) {
        k = keys[ki];
        if (n === null && typeof it[k] === 'number') n = it[k];
        if (n === null && typeof it[k] === 'string' && /^\d+$/.test(it[k])) n = parseInt(it[k], 10);
      }
      name = String(it.name || it.title || it.codename || '');
      url = String(it.url || it.link || it.href || '');
      status = String(it.status || it.state || 'live');
      if (n === null) { var m = /ship\s*(\d+)/i.exec(name + ' ' + String(it.id || '')); if (m) n = parseInt(m[1], 10); }
      if (n === null && !name.trim()) return;
      if (SEAL.test(status)) return;
      name = name.replace(/^\s*ship\s*\d+\s*[·:—–-]\s*/i, '').trim();
      var key = (n != null) ? n : name;
      if (seen[key]) return; seen[key] = 1;
      res.push({ n: n, name: name, url: url, repo: String(it.repo || ''), status: status });
    });
    res.sort(function (a, b) { return (a.n || 0) - (b.n || 0); });
    return res;
  }
  var ships = normalize(CANON);
  function total() { return ships.length; }
  function litCount() { return ships.length; }
  function pad(n) { return (n < 10 ? '0' : '') + n; }

  /* ---------- stylesheet ---------- */
  try {
    if (!$('gg-css')) {
      var srcAttr = (doc.currentScript && doc.currentScript.src) || '';
      var cssHref = srcAttr ? srcAttr.replace(/gate-module\.js([?#].*)?$/, 'gate-module.css') : 'assets/gate-module.css';
      var l = doc.createElement('link'); l.id = 'gg-css'; l.rel = 'stylesheet'; l.href = cssHref;
      (doc.head || doc.documentElement).appendChild(l);
    }
  } catch (e) {}

  /* ---------- control strip: THE standalone gate button ---------- */
  var strip = doc.createElement('div'); strip.id = 'ggStrip';
  strip.innerHTML =
    '<button class="gg-btn gg-primary" id="ggDial" type="button">&#9672; DIAL THE GATE</button>' +
    '<button class="gg-btn" id="ggView" type="button">&#9680; VIEW THE GATE</button>' +
    '<span class="gg-read" id="ggRead"></span>' +
    '<button class="gg-min" id="ggMin" type="button" title="collapse / expand">&ndash;</button>';
  (doc.body || doc.documentElement).appendChild(strip);

  /* ---------- gate view overlay: dial + water effect + fleet chips + job board ---------- */
  var ov = doc.createElement('div'); ov.id = 'ggOverlay';
  ov.innerHTML =
    '<button class="gg-close" id="ggClose" type="button">&#10005; CLOSE</button>' +
    '<canvas id="ggCanvas"></canvas>' +
    '<div class="gg-status" id="ggStatus"></div>' +
    '<div class="gg-fleet" id="ggFleet"></div>' +
    '<div class="gg-jobs" id="ggJobs"></div>';
  (doc.body || doc.documentElement).appendChild(ov);

  function setStatus(t) { var el = $('ggStatus'); if (el) el.textContent = t; }

  function renderFleet() {
    var f = $('ggFleet'); if (!f) return;
    var html = '';
    ships.forEach(function (s) {
      var lbl = 'S' + (s.n != null ? pad(s.n) : '?') + (s.name ? ' &middot; ' + esc(s.name) : '');
      var href = s.repo || s.url || '';
      html += href ? '<a class="gg-ship" href="' + esc(href) + '" target="_blank" rel="noopener">' + lbl + '</a>' : '<span class="gg-ship">' + lbl + '</span>';
    });
    f.innerHTML = html || '<span class="gg-ship gg-none">FLEET NOT READ</span>';
    syncRead();
  }

  /* ---------- strip readout MIRRORS the console's own gateCount (always true, N-expandable) ---------- */
  function syncRead() {
    var r = $('ggRead'); if (!r) return;
    var gc = doc.getElementById('gateCount');
    var m = gc ? /^(\d+)\s*\/\s*(\d+)$/.exec((gc.textContent || '').trim()) : null;
    if (m) {
      var n = parseInt(m[1], 10), N = parseInt(m[2], 10), ok = n >= N && N > 0;
      r.innerHTML = 'FLEET <span class="' + (ok ? 'gg-lit' : 'gg-lock') + '">' + n + '/' + N + ' LIT</span> &middot; ' + (ok ? 'GATE DIALABLE' : 'GATE LOCKED');
    } else {
      var T = total(), L = litCount(), ok2 = T > 0 && L >= T;
      r.innerHTML = 'FLEET <span class="' + (ok2 ? 'gg-lit' : 'gg-lock') + '">' + L + '/' + T + ' LIT</span> &middot; ' + (ok2 ? 'GATE DIALABLE' : 'GATE LOCKED');
    }
  }

  /* ---------- gate dial canvas (VIEW THE GATE cinematic) ---------- */
  var cv = $('ggCanvas'), cx = cv ? cv.getContext('2d') : null;
  var W = 0, H = 0, R = 0, raf = null, dialTimer = null;
  var state = 'idle', dialStart = 0, whooshT = -1;
  var RM = false;
  try { RM = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}
  var SPD = RM ? 0.18 : 1;
  var CHEV_N = 9, CHEV_ORDER = [0, 4, 5, 3, 6, 2, 7, 1, 8];
  var stars = [];
  (function () { var s = 7; function rnd() { s = (s * 16807) % 2147483647; return s / 2147483647; }
    for (var i = 0; i < 110; i++) stars.push([rnd(), rnd(), 0.3 + rnd() * 1.4]); })();

  function fit() {
    if (!cv) return;
    var d = Math.min(window.devicePixelRatio || 1, 2);
    var r = cv.getBoundingClientRect();
    W = r.width; H = r.height;
    cv.width = Math.max(1, Math.round(W * d)); cv.height = Math.max(1, Math.round(H * d));
    if (cx) cx.setTransform(d, 0, 0, d, 0, 0);
  }

  function chevron(ang, litN, flash) {
    cx.save(); cx.rotate(ang); cx.translate(0, -R);
    cx.beginPath();
    cx.moveTo(-R * 0.085, -R * 0.03);
    cx.lineTo(0, R * 0.105);
    cx.lineTo(R * 0.085, -R * 0.03);
    if (litN) { cx.strokeStyle = '#ffd27a'; cx.shadowColor = '#ffb545'; cx.shadowBlur = flash ? 30 : 16; cx.lineWidth = R * 0.034; }
    else { cx.strokeStyle = 'rgba(140,170,215,0.4)'; cx.shadowBlur = 0; cx.lineWidth = R * 0.026; }
    cx.stroke(); cx.shadowBlur = 0; cx.restore();
  }

  function water(now, Rv) {
    var r = Rv * 0.62, open = (state === 'open'), k, x, y;
    cx.save();
    cx.beginPath(); cx.arc(0, 0, r, 0, Math.PI * 2); cx.clip();
    var g = cx.createRadialGradient(0, 0, 0, 0, 0, r);
    if (open) { g.addColorStop(0, 'rgba(205,238,255,0.95)'); g.addColorStop(0.75, 'rgba(120,185,240,0.9)'); g.addColorStop(1, 'rgba(70,130,200,0.85)'); }
    else { g.addColorStop(0, 'rgba(70,120,180,0.45)'); g.addColorStop(1, 'rgba(12,28,55,0.6)'); }
    cx.fillStyle = g; cx.fillRect(-r, -r, 2 * r, 2 * r);
    var rows = 7, amp = open ? 3.4 : 1.5, spd = open ? 260 : 900;
    for (k = 0; k < rows; k++) {
      cx.beginPath();
      for (x = -r; x <= r; x += 5) {
        y = Math.sin(now / spd + x * 0.045 + k * 0.9) * amp * (1 - k / (rows + 2));
        if (x === -r) cx.moveTo(x, y); else cx.lineTo(x, y);
      }
      cx.strokeStyle = 'rgba(255,255,255,' + Math.max(0.02, (open ? 0.22 : 0.1) - k * 0.018).toFixed(3) + ')';
      cx.lineWidth = 1.15; cx.stroke();
    }
    if (whooshT > 0) {
      var dt = now - whooshT;
      if (dt < 750) {
        var a = 1 - dt / 750;
        var wg = cx.createRadialGradient(0, 0, r * 0.15, 0, 0, r * 1.9);
        wg.addColorStop(0, 'rgba(255,255,255,' + (0.9 * a).toFixed(3) + ')');
        wg.addColorStop(1, 'rgba(140,210,255,0)');
        cx.fillStyle = wg; cx.fillRect(-r * 2, -r * 2, 4 * r, 4 * r);
      } else whooshT = -1;
    }
    cx.restore();
    if (open) {
      cx.beginPath(); cx.arc(0, 0, r + 1, 0, Math.PI * 2);
      cx.strokeStyle = 'rgba(170,225,255,0.85)'; cx.lineWidth = 2.5;
      cx.shadowColor = '#8fd0ff'; cx.shadowBlur = 26; cx.stroke(); cx.shadowBlur = 0;
    }
  }

  function draw(now) {
    raf = requestAnimationFrame(draw);
    if (!cx) return;
    R = Math.min(W, H) * 0.36;
    var i, cxm = W / 2, cym = H * 0.46, t = now / 1000;
    cx.clearRect(0, 0, W, H);
    var bg = cx.createRadialGradient(cxm, cym, R * 0.2, cxm, cym, Math.max(W, H) * 0.75);
    bg.addColorStop(0, 'rgba(12,34,68,0.5)'); bg.addColorStop(1, 'rgba(2,4,10,0)');
    cx.fillStyle = bg; cx.fillRect(0, 0, W, H);
    for (i = 0; i < stars.length; i++) {
      var st = stars[i], tw = 0.25 + 0.45 * Math.abs(Math.sin(t * (1.2 + st[2]) + i));
      cx.fillStyle = 'rgba(190,220,255,' + (tw * st[2]).toFixed(3) + ')';
      cx.fillRect(st[0] * W, st[1] * H, 1.4, 1.4);
    }
    cx.save(); cx.translate(cxm, cym);
    cx.beginPath(); cx.arc(0, 0, R, 0, Math.PI * 2);
    cx.lineWidth = R * 0.17; cx.strokeStyle = '#16294a'; cx.stroke();
    cx.beginPath(); cx.arc(0, 0, R + R * 0.095, 0, Math.PI * 2);
    cx.lineWidth = 1.5; cx.strokeStyle = 'rgba(120,180,255,0.35)'; cx.stroke();
    cx.beginPath(); cx.arc(0, 0, R - R * 0.1, 0, Math.PI * 2);
    cx.lineWidth = 1.2; cx.strokeStyle = 'rgba(120,180,255,0.22)'; cx.stroke();
    cx.save(); cx.rotate(t * 0.22 * SPD);
    cx.setLineDash([R * 0.055, R * 0.042]); cx.lineWidth = R * 0.05;
    cx.strokeStyle = 'rgba(150,210,255,0.5)';
    cx.beginPath(); cx.arc(0, 0, R * 0.855, 0, Math.PI * 2); cx.stroke();
    cx.restore();
    cx.save(); cx.rotate(-t * 0.15 * SPD);
    cx.setLineDash([R * 0.014, R * 0.05]); cx.lineWidth = R * 0.034;
    cx.strokeStyle = 'rgba(95,165,235,0.4)';
    cx.beginPath(); cx.arc(0, 0, R * 0.775, 0, Math.PI * 2); cx.stroke();
    cx.restore();
    cx.setLineDash([]);
    var lockedN = 0;
    if (state === 'dialing') lockedN = Math.min(CHEV_N, Math.floor((now - dialStart) / 420) + 1);
    if (state === 'open') lockedN = CHEV_N;
    for (i = 0; i < CHEV_N; i++) {
      var ang = -Math.PI / 2 + i * (Math.PI * 2 / CHEV_N);
      var litN = CHEV_ORDER.indexOf(i) < lockedN;
      var isFlash = litN && state === 'dialing' && CHEV_ORDER.indexOf(i) === lockedN - 1 && ((now - dialStart) % 420) < 170;
      chevron(ang, litN, isFlash);
    }
    water(now, R);
    cx.restore();
  }

  function openOv(mode) {
    if (!ov || !cv) return;
    ov.classList.add('gg-show');
    fit();
    if (!raf) raf = requestAnimationFrame(draw);
    var T = total(), L = litCount();
    if (mode === 'dial') {
      state = 'dialing'; dialStart = performance.now(); whooshT = -1;
      if (dialTimer) clearInterval(dialTimer);
      dialTimer = setInterval(function () {
        if (!ov.classList.contains('gg-show')) { clearInterval(dialTimer); dialTimer = null; return; }
        var k = Math.min(CHEV_N, Math.floor((performance.now() - dialStart) / 420) + 1);
        if (k >= CHEV_N) {
          clearInterval(dialTimer); dialTimer = null;
          state = 'open'; whooshT = performance.now();
          setStatus('GATE OPEN · WORMHOLE STABLE · FLEET ' + L + '/' + T + ' LIT');
        } else setStatus('CHEVRON ' + k + '/' + CHEV_N + ' LOCKED · FLEET ' + L + '/' + T);
      }, 210);
      setStatus('DIALING · FLEET ' + L + '/' + T + ' LIT');
    } else {
      state = 'idle';
      setStatus('GATE DIAL · FLEET ' + L + '/' + T + ' LIT · WATER EFFECT LIVE');
    }
  }
  function closeOv() {
    ov.classList.remove('gg-show');
    if (dialTimer) { clearInterval(dialTimer); dialTimer = null; }
    if (raf) { cancelAnimationFrame(raf); raf = null; }
    state = 'idle';
  }
  function flashLocked() {
    strip.classList.add('gg-locked');
    setTimeout(function () { strip.classList.remove('gg-locked'); }, 1200);
  }

  /* DIAL THE GATE on command — drives the console's OWN native gate (SVG kawoosh + sound) */
  function dial() {
    try { if (typeof window.dialGate === 'function') { window.dialGate(); return; } } catch (e) {}
    var T = total(), L = litCount();
    if (T === 0 || L < T) { flashLocked(); openOv('idle'); setStatus('GATE LOCKED · FLEET ' + L + '/' + T + ' LIT'); return; }
    openOv('dial');
  }
  function view() { openOv('idle'); }

  /* ---------- job board (auto-feed: polls jobs.json every 60s) ---------- */
  function renderJobs(d) {
    var box = $('ggJobs'); if (!box) return;
    var jobs = (d && d.jobs) || [], html = '';
    html += '<div class="gg-jobs-h">JOB BOARD · AUTO-FEED · SYNC ' + new Date().toLocaleTimeString() + '</div>';
    jobs.slice(0, 8).forEach(function (j) {
      var st = String((j.status || 'open')).toLowerCase();
      html += '<div class="gg-job"><span class="gg-job-id">' + esc(j.id || '') + '</span>' +
        '<span class="gg-job-t">' + esc(j.title || '') + '</span>' +
        '<span class="gg-st gg-st-' + esc(st) + '">' + esc(st.toUpperCase()) + '</span></div>';
    });
    if (!jobs.length) html += '<div class="gg-job"><span class="gg-job-t">jobs.json empty — crawler feed lands here automatically</span></div>';
    box.innerHTML = html;
  }
  function pollJobs() {
    try {
      fetch('jobs.json?_=' + Date.now(), { cache: 'no-store' })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (d) { if (d) renderJobs(d); })
        .catch(function () {});
    } catch (e) {}
  }

  /* ---------- expandable canon: runtime refresh if a manifest src exists ---------- */
  if (CANON && CANON.src) {
    try {
      fetch(CANON.src + '?_=' + Date.now(), { cache: 'no-store' })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (d) {
          if (!d) return;
          var list = normalize(d);
          if (list.length && list.length !== ships.length) { ships = list; renderFleet(); }
        })
        .catch(function () {});
    } catch (e) {}
  }

  /* ---------- legacy stray gate buttons: rebind to the real gate (never the console's own dialBtn) ---------- */
  try {
    var els = doc.querySelectorAll('button, a, [role="button"]');
    for (var i = 0; i < els.length; i++) {
      var el = els[i];
      if (el.id && (el.id === 'dialBtn' || /^gg/.test(el.id))) continue;
      if (el.getAttribute && el.getAttribute('data-gg-bound')) continue;
      var txt = (el.textContent || '').trim();
      if (/dial\s*the\s*gate/i.test(txt)) {
        var clone = el.cloneNode(true);
        el.parentNode.replaceChild(clone, el);
        clone.setAttribute('data-gg-bound', '1');
        clone.addEventListener('click', function (ev) { ev.preventDefault(); dial(); });
      }
    }
  } catch (e) {}

  /* ---------- wire + init ---------- */
  var bD = $('ggDial'), bV = $('ggView'), bC = $('ggClose'), bM = $('ggMin');
  if (bD) bD.addEventListener('click', dial);
  if (bV) bV.addEventListener('click', view);
  if (bC) bC.addEventListener('click', closeOv);
  if (bM) bM.addEventListener('click', function () {
    strip.classList.toggle('gg-collapsed');
    bM.textContent = strip.classList.contains('gg-collapsed') ? '+' : '\u2013';
  });
  doc.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeOv(); });
  renderFleet();
  syncRead(); setInterval(syncRead, 2000);
  pollJobs(); setInterval(pollJobs, 60000);
  if (/[?&]ggview=1/.test(location.search)) view();
})();
