(function () {
  if (window.__GG__) return; window.__GG__ = true;
  var doc = document;
  function $(id) { return doc.getElementById(id); }
  function esc(s) { var d = doc.createElement('div'); d.appendChild(doc.createTextNode(String(s == null ? '' : s))); return d.innerHTML; }

  var CANON = window.FLEET_CANON || { src: "manifest.json", ships: [{"n": 1, "name": "DeepSeek RAG — the origin ship", "url": "https://github.com/qaevelyn/a-mirror-of-my-becoming-rag-ship1-deepseek", "status": "flown"}, {"n": 2, "name": "IBM Granite Agentic RAG", "url": "https://github.com/qaevelyn/a-mirror-of-my-becoming-rag-ship2-ibm-granite-agentic", "status": "flown"}, {"n": 3, "name": "IBM Granite RAG", "url": "https://github.com/qaevelyn/a-mirror-of-my-becoming-rag-ship3-ibm-granite", "status": "flown"}, {"n": 4, "name": "IBM Granite Agentic RAG — the agentic flagship", "url": "https://github.com/qaevelyn/a-mirror-of-my-becoming-rag-ship4-ibm-granite-agentic", "status": "flown"}, {"n": 5, "name": "EvidenceFlow — fail-closed verification", "url": "https://github.com/qaevelyn/a-mirror-of-my-becoming-rag-ship5-ibm-granite-agentic-evidenceflow", "status": "flown"}, {"n": 6, "name": "Ingestion Tools — Scribe · Warden · Hand", "url": "https://github.com/qaevelyn/a-mirror-of-my-becoming-suite-ingestion-tools", "status": "flown"}, {"n": 7, "name": "msgvault Adapter", "url": "https://github.com/qaevelyn/a-mirror-of-my-becoming-suite-msgvault-adapter", "status": "flown"}, {"n": 8, "name": "DV14™: The Box — AI containment blueprint", "url": "", "status": "flown"}, {"n": 9, "name": "Radiology Companion™", "url": "", "status": "flown"}, {"n": 10, "name": "Overseer™ — tier-authority orchestrator", "url": "https://github.com/qaevelyn/a-mirror-of-my-becoming-suite-overseer", "status": "flown"}, {"n": 11, "name": "AWS CCP Study Manual — Sleep Is Studying Too™", "url": "https://github.com/qaevelyn/a-mirror-of-my-becoming-ship11-aws-ccp-study-manual", "status": "flown"}, {"n": 12, "name": "CARO COMMAND — SCOUT OPS (this console)", "url": "https://github.com/qaevelyn/a-mirror-of-my-becoming-ship12-caro-command", "status": "live"}, {"n": 13, "name": "TriviaGate™ — the ONE Ship 13 study engine · single file", "url": "https://github.com/qaevelyn/a-mirror-of-my-becoming-ship13-triviagate", "status": "live"}] };
  var SEAL = /seal|draft|planned|concept|pending|stub|future/i;
  function normalize(data) {
    var list = data;
    if (data && typeof data === 'object' && !Array.isArray(data)) list = data.ships || data.fleet || data.vessels || null;
    if (!Array.isArray(list)) return [];
    var seen = {}, res = [];
    list.forEach(function (it) {
      if (!it || typeof it !== 'object') return;
      var n = null, name = '', url = '', status = 'live', k;
      var keys = ['n', 'num', 'number', 'no', 'ship'];
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
      name = name.replace(/^\s*ship\s*\d+\s*[\u00b7:\u2014\u2013-]\s*/i, '').trim();
      var key = (n != null) ? n : name;
      if (seen[key]) return; seen[key] = 1;
      res.push({ n: n, name: name, url: url, status: status });
    });
    res.sort(function (a, b) { return (a.n || 0) - (b.n || 0); });
    return res;
  }
  var ships = normalize(CANON);
  function total() { return ships.length; }
  function litCount() { return ships.length; }

  try {
    if (!$('gg-css')) {
      var srcAttr = (doc.currentScript && doc.currentScript.src) || '';
      var cssHref = srcAttr ? srcAttr.replace(/gate-module\.js([?#].*)?$/, 'gate-module.css') : 'assets/gate-module.css';
      var l = doc.createElement('link'); l.id = 'gg-css'; l.rel = 'stylesheet'; l.href = cssHref;
      (doc.head || doc.documentElement).appendChild(l);
    }
  } catch (e) {}

  var strip = doc.createElement('div'); strip.id = 'ggStrip';
  strip.innerHTML =
    '<button class="gg-btn gg-primary" id="ggDial" type="button">\u25C8 DIAL THE GATE</button>' +
    '<button class="gg-btn" id="ggView" type="button">\u25C0 VIEW THE GATE</button>' +
    '<span class="gg-read" id="ggRead"></span>' +
    '<button class="gg-min" id="ggMin" type="button" title="collapse / expand">&ndash;</button>';
  (doc.body || doc.documentElement).appendChild(strip);

  var ov = doc.createElement('div'); ov.id = 'ggOverlay';
  ov.innerHTML =
    '<button class="gg-close" id="ggClose" type="button">\u2715 CLOSE</button>' +
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
      var label = 'S' + (s.n != null ? s.n : '?') + (s.name ? ' \u00b7 ' + esc(s.name) : '');
      if (s.url) html += '<a class="gg-ship" href="' + esc(s.url) + '" target="_blank" rel="noopener">' + label + '</a>';
      else html += '<span class="gg-ship gg-none">' + label + '</span>';
    });
    f.innerHTML = html || '<span class="gg-ship gg-none">FLEET NOT READ</span>';
    var r = $('ggRead');
    if (r) r.innerHTML = (total() > 0 && litCount() === total())
      ? 'FLEET <span class="gg-lit">' + litCount() + '/' + total() + ' LIT</span> \u00b7 GATE DIALABLE'
      : 'FLEET <span class="gg-lock">' + litCount() + '/' + total() + ' LIT</span> \u00b7 GATE LOCKED';
  }

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
    else { cx.strokeStyle = 'rgba(180,140,80,0.4)'; cx.shadowBlur = 0; cx.lineWidth = R * 0.026; }
    cx.stroke(); cx.shadowBlur = 0; cx.restore();
  }

  function water(now, Rv) {
    var r = Rv * 0.62, open = (state === 'open'), k, x, y;
    cx.save();
    cx.beginPath(); cx.arc(0, 0, r, 0, Math.PI * 2); cx.clip();
    var g = cx.createRadialGradient(0, 0, 0, 0, 0, r);
    if (open) { g.addColorStop(0, 'rgba(255,240,200,0.95)'); g.addColorStop(0.75, 'rgba(240,200,100,0.9)'); g.addColorStop(1, 'rgba(200,150,50,0.85)'); }
    else { g.addColorStop(0, 'rgba(180,140,50,0.45)'); g.addColorStop(1, 'rgba(30,18,6,0.6)'); }
    cx.fillStyle = g; cx.fillRect(-r, -r, 2 * r, 2 * r);
    var rows = 7, amp = open ? 3.4 : 1.5, spd = open ? 260 : 900;
    for (k = 0; k < rows; k++) {
      cx.beginPath();
      for (x = -r; x <= r; x += 5) {
        y = Math.sin(now / spd + x * 0.045 + k * 0.9) * amp * (1 - k / (rows + 2));
        if (x === -r) cx.moveTo(x, y); else cx.lineTo(x, y);
      }
      cx.strokeStyle = 'rgba(255,240,200,' + Math.max(0.02, (open ? 0.22 : 0.1) - k * 0.018).toFixed(3) + ')';
      cx.lineWidth = 1.15; cx.stroke();
    }
    if (whooshT > 0) {
      var dt = now - whooshT;
      if (dt < 750) {
        var a = 1 - dt / 750;
        var wg = cx.createRadialGradient(0, 0, r * 0.15, 0, 0, r * 1.9);
        wg.addColorStop(0, 'rgba(255,255,240,' + (0.9 * a).toFixed(3) + ')');
        wg.addColorStop(1, 'rgba(255,220,140,0)');
        cx.fillStyle = wg; cx.fillRect(-r * 2, -r * 2, 4 * r, 4 * r);
      } else whooshT = -1;
    }
    cx.restore();
    if (open) {
      cx.beginPath(); cx.arc(0, 0, r + 1, 0, Math.PI * 2);
      cx.strokeStyle = 'rgba(255,220,140,0.85)'; cx.lineWidth = 2.5;
      cx.shadowColor = '#ffd27a'; cx.shadowBlur = 26; cx.stroke(); cx.shadowBlur = 0;
    }
  }

  function draw(now) {
    raf = requestAnimationFrame(draw);
    if (!cx) return;
    R = Math.min(W, H) * 0.36;
    var i, cxm = W / 2, cym = H * 0.46, t = now / 1000;
    cx.clearRect(0, 0, W, H);
    var bg = cx.createRadialGradient(cxm, cym, R * 0.2, cxm, cym, Math.max(W, H) * 0.75);
    bg.addColorStop(0, 'rgba(40,24,8,0.5)'); bg.addColorStop(1, 'rgba(2,1,0,0)');
    cx.fillStyle = bg; cx.fillRect(0, 0, W, H);
    for (i = 0; i < stars.length; i++) {
      var st = stars[i], tw = 0.25 + 0.45 * Math.abs(Math.sin(t * (1.2 + st[2]) + i));
      cx.fillStyle = 'rgba(255,240,200,' + (tw * st[2]).toFixed(3) + ')';
      cx.fillRect(st[0] * W, st[1] * H, 1.4, 1.4);
    }
    cx.save(); cx.translate(cxm, cym);
    cx.beginPath(); cx.arc(0, 0, R, 0, Math.PI * 2);
    cx.lineWidth = R * 0.17; cx.strokeStyle = '#2a1a08'; cx.stroke();
    cx.beginPath(); cx.arc(0, 0, R + R * 0.095, 0, Math.PI * 2);
    cx.lineWidth = 1.5; cx.strokeStyle = 'rgba(200,160,80,0.35)'; cx.stroke();
    cx.beginPath(); cx.arc(0, 0, R - R * 0.1, 0, Math.PI * 2);
    cx.lineWidth = 1.2; cx.strokeStyle = 'rgba(180,140,60,0.22)'; cx.stroke();
    cx.save(); cx.rotate(t * 0.22 * SPD);
    cx.setLineDash([R * 0.055, R * 0.042]); cx.lineWidth = R * 0.05;
    cx.strokeStyle = 'rgba(220,180,90,0.5)';
    cx.beginPath(); cx.arc(0, 0, R * 0.855, 0, Math.PI * 2); cx.stroke();
    cx.restore();
    cx.save(); cx.rotate(-t * 0.15 * SPD);
    cx.setLineDash([R * 0.014, R * 0.05]); cx.lineWidth = R * 0.034;
    cx.strokeStyle = 'rgba(200,160,70,0.4)';
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
          setStatus('GATE OPEN \u00b7 WORMHOLE STABLE \u00b7 FLEET ' + L + '/' + T + ' LIT');
        } else setStatus('CHEVRON ' + k + '/' + CHEV_N + ' LOCKED \u00b7 FLEET ' + L + '/' + T);
      }, 210);
      setStatus('DIALING \u00b7 FLEET ' + L + '/' + T + ' LIT');
    } else {
      state = 'idle';
      setStatus('GATE DIAL \u00b7 FLEET ' + L + '/' + T + ' LIT \u00b7 WATER EFFECT LIVE');
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
  function dial() {
    var T = total(), L = litCount();
    if (T === 0 || L < T) { flashLocked(); openOv('idle'); setStatus('GATE LOCKED \u00b7 FLEET ' + L + '/' + T + ' LIT'); return; }
    openOv('dial');
  }
  function view() { openOv('idle'); }

  function renderJobs(d) {
    var box = $('ggJobs'); if (!box) return;
    var jobs = (d && d.jobs) || [], html = '';
    html += '<div class="gg-jobs-h">JOB BOARD \u00b7 AUTO-FEED \u00b7 SYNC ' + new Date().toLocaleTimeString() + '</div>';
    jobs.slice(0, 12).forEach(function (j) {
      var st = String((j.status || 'open')).toLowerCase();
      html += '<div class="gg-job"><span class="gg-job-id">' + esc(j.id || '') + '</span>' +
        '<span class="gg-job-t">' + esc(j.title || '') + '</span>' +
        '<span class="gg-st gg-st-' + esc(st) + '">' + esc(st.toUpperCase()) + '</span></div>';
    });
    if (!jobs.length) html += '<div class="gg-job"><span class="gg-job-t">jobs.json empty</span></div>';
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

  try {
    var els = doc.querySelectorAll('button, a, [role="button"]');
    for (var i = 0; i < els.length; i++) {
      var el = els[i];
      if (el.id && /^gg/.test(el.id)) continue;
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
  pollJobs();
  setInterval(pollJobs, 60000);
  if (/[?&]ggview=1/.test(location.search)) view();
})();
