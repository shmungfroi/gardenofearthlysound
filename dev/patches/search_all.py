"""Search reaches glossary terms, dances and card text (19 Nov 2026, §7.8 Part A). Idempotent: run, then ./build.sh."""
import sys, pathlib
p = pathlib.Path(__file__).resolve().parents[2] / 'src' / 'template.html'
t = p.read_text(encoding='utf-8')
if '/* ---- search reaches terms' in t:
    print('already applied'); sys.exit(0)

def rep(a, b):
    global t
    assert t.count(a) == 1, ('anchor not unique', a[:80], t.count(a))
    t = t.replace(a, b)

# 1. placeholder
rep('placeholder="Find a lantern (any form)…"', 'placeholder="Search the Garden…"')
rep('aria-label="Find a form"', 'aria-label="Search the Garden"')

# 2. CSS (after the existing result styles)
rep("#res .none{padding:8px 10px;font-size:13px;color:var(--muted)}",
    "#res .none{padding:8px 10px;font-size:13px;color:var(--muted)}\n"
    "/* search: dances, terms and card text (19 Nov) */\n"
    "#res .dres,#res .gres{order:1;color:var(--ivory)} #res .dres small,#res .gres small{color:var(--gold)} #res .mres{order:6;color:var(--muted);font-style:italic} #res .mres small{font-style:normal}\n"
    ".sheet .tp-h{margin:2px 6px 2px;display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 8px} .sheet .tp-h b{font-size:18px;font-weight:600;color:var(--ivory)}\n"
    ".sheet .tp-el{display:inline-flex;gap:4px} .sheet .tp-el i{font-style:normal;font-size:10.5px;color:var(--green);border:1px solid #3d5a2c;border-radius:8px;padding:0 6px}\n"
    ".sheet .tp-ex{color:var(--muted)} .sheet .tp-k{display:block;font-size:10.5px;letter-spacing:1.6px;text-transform:uppercase;color:var(--gold);margin:14px 6px 4px}\n"
    ".sheet ul.tp-l{list-style:none;margin:0 6px;padding:0} .sheet ul.tp-l li{position:relative;margin:0 0 4px;padding-left:16px;font-size:13px;line-height:1.45} .sheet ul.tp-l li::before{content:\"\";position:absolute;left:0;top:.74em;width:8px;border-top:1px solid var(--gold)}\n"
    ".sheet button.tp-go{display:inline;width:auto;padding:0;border-radius:0;font-size:13.5px;color:var(--goldhi);border-bottom:1px solid #5d5546} .sheet button.tp-go:hover{background:none;color:var(--ivory);border-color:var(--gold)} .sheet button.tp-go::after{content:\"\\00a0›\";color:var(--gold)}\n"
    ".sheet button.tp-x{float:right;width:auto;padding:0 8px;margin:-2px -2px 0 6px;font-size:20px;line-height:1.2;color:var(--muted)} .sheet button.tp-x:hover{color:var(--goldhi)}\n.sheet .tp-home small{margin-left:6px} .sheet .tp-snip{display:block;margin:2px 0 0;font-size:12px;line-height:1.4;color:var(--muted);white-space:normal}\n")

# 3. the engine, before the search listener
rep("q.addEventListener('input', () => { res.innerHTML = '';",
r"""/* ---- search reaches terms, dances and card text (19 Nov) ----
   TERMS: every glossary key, with the lanterns whose cards bold it (its homes).
   TXT: each lantern's card text, folded, for "mentioned in". Built on the first search. */
const GLO = (G.ATLAS && G.ATLAS.glossary) || {}, GMT = (G.ATLAS && G.ATLAS.glossmeta) || {}, DNC = (G.ATLAS && G.ATLAS.dances) || [], ELN = (G.ATLAS && G.ATLAS.elements) || {};
const gk = x => { const k = String(x || '').toLowerCase().replace(/\s+/g, ' ').trim(); if (!k) return null; if (GLO[k]) return k;
  const t = []; if (k.endsWith('ies')) t.push(k.slice(0, -3) + 'y'); if (k.endsWith('es')) t.push(k.slice(0, -2)); if (k.endsWith('s')) t.push(k.slice(0, -1)); t.push(k + 's', k + 'es'); if (k.endsWith('y')) t.push(k.slice(0, -1) + 'ies');
  return t.find(y => GLO[y]) || null; };
let SIX = null;
const sIndex = () => { if (SIX) return SIX; const homes = {}, txt = {}, raw = {}, FULL = (G.ATLAS && G.ATLAS.full) || {};
  const walk = (o, out) => { if (typeof o === 'string') { if (!/^https?:/.test(o)) out.push(o); } else if (Array.isArray(o)) o.forEach(x => walk(x, out)); else if (o && typeof o === 'object') Object.keys(o).forEach(k => { if (k !== 'media') walk(o[k], out); }); return out; };
  D.nodes.filter(n => LAY.nodes[n.id]).sort((a, b) => a.y - b.y).forEach(n => { const ss = walk([n.brief, FULL[n.id]], []), j = ss.join(' ');
    j.split('**').forEach((part, i) => { if (!(i % 2)) return; const k = gk(part); if (k) { (homes[k] = homes[k] || []); if (!homes[k].includes(n.id)) homes[k].push(n.id); } });
    raw[n.id] = j.replace(/\*\*/g, ''); txt[n.id] = fold(raw[n.id]); });
  return SIX = {homes, txt, raw}; };
const rank = (name, s) => { const t = fold(name); return t === s ? 0 : t.startsWith(s) ? 1 : t.split(/[\s&,():/-]+/).some(w => w.startsWith(s)) ? 2 : 3; };
function extraResults(sv, lanterns) { const out = {d: [], g: [], m: []}; if (sv.length < 3) return out; const X = sIndex();
  out.d = DNC.filter(d => fold(d.dance).includes(sv)).sort((a, b) => rank(a.dance, sv) - rank(b.dance, sv)).slice(0, 3);
  const exact = gk(sv), gs = Object.keys(GLO).filter(k => fold(k).includes(sv) || k === exact);
  out.g = gs.sort((a, b) => (a === exact ? -1 : rank(a, sv)) - (b === exact ? -1 : rank(b, sv)) || a.length - b.length).slice(0, 4);
  if (sv.length >= 4) { const shown = new Set(lanterns.map(n => n.id)); out.m = Object.keys(X.txt).filter(id => !shown.has(id) && X.txt[id].includes(sv)); }
  return out; }
function openDance(name) { const b = document.querySelector('.rail button[data-sheet="dances"]'); closeSheet(); if (b) openSheet('dances', b);
  const row = [...sheet.querySelectorAll('.dn-row')].find(r => { const n = r.querySelector('.dn-n'); return n && n.textContent === name; }); if (row) { row.click(); row.focus(); } }
function bareSheet(kind) { closeSheet(); sheet.innerHTML = ''; sheet.dataset.kind = kind; sheet.classList.add('open'); sheet.scrollTop = 0;
  const x = el('button', 'tp-x', sheet, '×'); x.type = 'button'; x.setAttribute('aria-label', 'Close'); x.onclick = closeSheet; }
/* the term page: definition, example, Listen for / Hear it in / Then and now, and the lanterns it lives in */
function showTerm(key) { const X = sIndex(), M = GMT[key] || {}, homes = X.homes[key] || []; bareSheet('term');
  el('h3', '', sheet, 'GLOSSARY'); const hd = el('div', 'tp-h', sheet); el('b', '', hd, key.charAt(0).toUpperCase() + key.slice(1));
  if (M.el && M.el.length) { const sp = el('span', 'tp-el', hd); M.el.forEach(c => el('i', '', sp, c === 'ctx' ? 'Context' : (ELN[c] ? ELN[c].name : c))); }
  el('p', '', sheet, GLO[key]); if (M.ex) el('p', 'tp-ex', sheet, M.ex);
  const listen = (M.listen || []).filter(Boolean).slice(0, 3); if (listen.length) { el('small', 'tp-k', sheet, 'Listen for'); const ul = el('ul', 'tp-l', sheet); listen.forEach(x => el('li', '', ul, x)); }
  if (M.hear && M.hear.work) { el('small', 'tp-k', sheet, 'Hear it in'); const p = el('p', '', sheet); if (M.hear.composer) p.append(M.hear.composer + ', ');
    if (M.hear.lantern && N[M.hear.lantern]) { const b = el('button', 'tp-go', p, M.hear.work); b.type = 'button'; b.onclick = () => { closeSheet(); choose(M.hear.lantern, true); }; } else p.append(M.hear.work);
    if (M.hear.where) p.append(' · ' + M.hear.where); }
  if (M.now) { el('small', 'tp-k', sheet, 'Then and now'); el('p', '', sheet, M.now); }
  const dn = DNC.find(d => fold(d.dance) === fold(key)); if (dn) { el('small', 'tp-k', sheet, 'Dances guide'); const p = el('p', '', sheet), b = el('button', 'tp-go', p, '¾ ' + dn.dance + ': metre, speed, rhythm'); b.type = 'button'; b.onclick = () => openDance(dn.dance); }
  el('small', 'tp-k', sheet, homes.length ? 'Found in ' + homes.length + ' lantern' + (homes.length === 1 ? '' : 's') : 'Not yet used in a lantern');
  homes.forEach(id => { const b = el('button', 'tp-home', sheet, N[id].t); el('small', '', b, N[id].d || ''); b.onclick = () => { closeSheet(); choose(id, true);
      setTimeout(() => { const k = [...document.querySelectorAll('button.kw')].find(x => gk(x.textContent) === key); if (k) { if (k.getAttribute('aria-expanded') !== 'true') k.click(); k.scrollIntoView({block: 'center'}); } }, 260); }; });
  const f = sheet.querySelector('button:not(.tp-x)'); if (f) f.focus({preventScroll: true}); }
/* every lantern whose card mentions the words, with a line of context */
function showMentions(raw, ids) { const X = sIndex(), s = raw.trim().toLowerCase(); bareSheet('mentions');
  el('h3', '', sheet, 'MENTIONED IN · ' + ids.length); el('p', 'lnote', sheet, 'Lanterns whose cards mention “' + raw.trim() + '”.');
  ids.forEach(id => { const b = el('button', 'tp-home', sheet, N[id].t); el('small', '', b, N[id].d || ''); const R = X.raw[id], i = R.toLowerCase().indexOf(s);
    if (i >= 0) { const a = Math.max(0, R.lastIndexOf(' ', Math.max(0, i - 50)) + 1), z = R.indexOf(' ', Math.min(R.length, i + s.length + 60)); el('span', 'tp-snip', b, (a > 0 ? '…' : '') + R.slice(a, z < 0 ? R.length : z) + (z < 0 ? '' : '…')); }
    b.onclick = () => { closeSheet(); choose(id, true); }; }); }
q.addEventListener('input', () => { res.innerHTML = '';""")

# 4. "nothing" message waits for the new results; then append them after the lantern rows (so Enter still prefers a lantern)
rep("if (!r.length && !vs.length && !es.length && !rs.length && !ws.length && sv.length >= 3) {",
    "const xr = extraResults(sv, r); if (xr.d.length || xr.g.length || xr.m.length) res.style.display = 'flex';\n  if (!r.length && !vs.length && !es.length && !rs.length && !ws.length && !xr.d.length && !xr.g.length && !xr.m.length && sv.length >= 3) {")
rep("b.onmouseenter = b.onfocus = () => { if (!sel) light(n.id); }; b.onclick = () => { res.style.display = 'none'; q.value = ''; q.blur(); choose(n.id, true); }; }); });",
    "b.onmouseenter = b.onfocus = () => { if (!sel) light(n.id); }; b.onclick = () => { res.style.display = 'none'; q.value = ''; q.blur(); choose(n.id, true); }; });\n"
    "  const done = () => { res.style.display = 'none'; const v = q.value; q.value = ''; q.blur(); return v; };\n"
    "  xr.d.forEach(d => { const b = el('button', 'dres', res, '¾ ' + d.dance); b.setAttribute('role', 'option'); el('small', '', b, `dance · ${d.metre}${d.speed ? ' · ' + d.speed : ''}`); b.onclick = () => { done(); openDance(d.dance); }; });\n"
    "  xr.g.forEach(k => { const h = (sIndex().homes[k] || []).length, b = el('button', 'gres', res, '❧ ' + k.charAt(0).toUpperCase() + k.slice(1)); b.setAttribute('role', 'option'); el('small', '', b, `term${h ? ` · in ${h} lantern${h === 1 ? '' : 's'}` : ''}`); b.onclick = () => { done(); showTerm(k); }; });\n"
    "  if (xr.m.length) { const b = el('button', 'mres', res, `… mentioned in ${xr.m.length} lantern${xr.m.length === 1 ? '' : 's'}`); b.setAttribute('role', 'option'); el('small', '', b, xr.m.slice(0, 3).map(i => N[i].t).join(', ') + (xr.m.length > 3 ? ', …' : '')); b.onclick = () => { const v = done(); showMentions(v, xr.m); }; } });")
rep("res.querySelector('button:not(.vres):not(.eres):not(.rres):not(.wres)')", "res.querySelector('button:not(.vres):not(.eres):not(.rres):not(.wres):not(.mres)')")
p.write_text(t, encoding='utf-8'); print('applied')
