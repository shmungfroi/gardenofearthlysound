/* ---------- My glossary: terms a student collects, in their own words (19 Nov 2026) ----------
   Stored in localStorage 'garden.glossary' = {v, by, sort: 'az'|'made', items}. A Garden term stores only its key,
   so later corrections to the Garden's definitions reach every saved glossary. Own terms: {own: 1, id, w, def, met, at}. */
const MGK = 'garden.glossary';
const S60 = (x, n) => (typeof x === 'string' ? x : (typeof x === 'number' ? String(x) : '')).slice(0, n);
function mgClean(list, keepIds) { const seen = new Set(), out = [];      /* coerce every field, drop what is not a real Garden term, merge duplicates */
  (Array.isArray(list) ? list : []).forEach(e => { if (!e || typeof e !== 'object') return;
    if (e.own) { const w = S60(e.w, 60).trim(); if (!w || seen.has('o:' + fold(w))) return; seen.add('o:' + fold(w)); out.push({own: 1, id: keepIds && typeof e.id === 'string' ? e.id : uid('o'), w, def: S60(e.def, 280), met: S60(e.met, 60), at: +e.at || Date.now()}); }
    else { const k = typeof e.k === 'string' ? e.k : ''; if (!isT(k) || seen.has(k)) return; seen.add(k); out.push({k, note: S60(e.note, 280), from: typeof e.from === 'string' && N[e.from] ? e.from : null, via: ['card', 'search', 'dances'].includes(e.via) ? e.via : 'card', at: +e.at || Date.now()}); } });
  return out; }
let MG = (() => { const g = LS(MGK, null), o = {v: 1, by: '', sort: 'az', items: []}; if (g && typeof g === 'object' && !Array.isArray(g)) { o.items = mgClean(g.items, true); o.by = S60(g.by, 40); o.sort = g.sort === 'made' ? 'made' : 'az'; } return o; })();
const saveMG = () => { try { localStorage.setItem(MGK, JSON.stringify(MG)); return true; } catch (err) { toast('This browser is full: share or print your glossary to make room', 5000); return false; } };
let mgOpen = null, mgQ = '', mgShared = null, mgFocus = null;
const capT = k => k.charAt(0).toUpperCase() + k.slice(1);
const mgId = e => e.own ? 'o:' + e.id : 'k:' + e.k;
const mgName = e => e.own ? e.w : e.k;
const mgHas = k => MG.items.some(e => !e.own && e.k === k);
const mgEls = k => { const M = GMT[k] || {}; if (M.el && M.el.length) return M.el; return Object.keys(ELN).filter(c => (ELN[c].vocab || []).some(v => fold(v) === fold(k))); };
const elLabel = c => c === 'ctx' ? 'Context' : (ELN[c] ? ELN[c].name : c);
const shortDate = t => new Date(t).toLocaleDateString('en-AU', {day: 'numeric', month: 'short'});
let mgFlush = null; addEventListener('pagehide', () => mgFlush && mgFlush()); document.addEventListener('visibilitychange', () => { if (document.hidden && mgFlush) mgFlush(); });
const quiet = x => { x.addEventListener('keydown', e => { if (e.key !== 'Escape') e.stopPropagation(); }); return x; };      /* typing / + - in a text box must not search or zoom */
function mgOpenIn(id, key) { closeSheet(); choose(id, true);
  setTimeout(() => { const k = [...document.querySelectorAll('button.kw')].find(x => gk(x.textContent) === key); if (k) { if (k.getAttribute('aria-expanded') !== 'true') k.click(); k.scrollIntoView({block: 'center'}); } }, 260); }
function openGlossary() { const b = document.querySelector('.rail button[data-sheet="glossary"]');
  if (sheet.classList.contains('open') && sheet.dataset.kind === 'glossary') return glossarySheet(true); closeSheet(); if (b) openSheet('glossary', b); }

/* the add button: one component on the term page, in the card's definition box and in open Dances rows */
function mgLabel(b) { const k = b.dataset.k, on = mgHas(k); b.setAttribute('aria-pressed', on ? 'true' : 'false'); b.innerHTML = '';
  el('i', '', b, on ? '✓' : '＋').setAttribute('aria-hidden', 'true'); b.append(on ? 'In my glossary' : 'My glossary');
  b.setAttribute('aria-label', on ? `${k} is in my glossary. Remove it` : `Add ${k} to my glossary`);
  const row = b.parentNode, go = row && row.querySelector('.mg-go.mg-at');
  if (on && !go && row) { const g = el('button', 'mg-go mg-at', row, 'Open'); g.type = 'button'; g.setAttribute('aria-label', 'Open my glossary at ' + k); g.onclick = () => { mgOpen = 'k:' + k; mgQ = ''; openGlossary(); }; }
  else if (!on && go) go.remove(); }
function mgSync() { document.querySelectorAll('button.mg-add[data-k]').forEach(mgLabel); if (sheet.classList.contains('open') && sheet.dataset.kind === 'glossary') glossarySheet(true); }
function mgRemove(e) { const i = MG.items.indexOf(e); if (i < 0) return; if (sheet.dataset.kind === 'glossary' && sheet.contains(document.activeElement)) mgFocus = {near: [...sheet.querySelectorAll('.mg-row')].findIndex(r => r.parentNode.contains(document.activeElement))}; MG.items.splice(i, 1); saveMG(); if (mgOpen === mgId(e)) mgOpen = null; mgSync();
  toast(`Removed “${esc(e.own ? e.w : capT(e.k))}” <button class="undo" aria-label="Undo remove">Undo</button>`, 6000); say('Removed. Undo is available.');
  const u = $('#toast .undo'); if (u) u.onclick = () => { MG.items.splice(Math.min(i, MG.items.length), 0, e); saveMG(); mgSync(); toast('Term restored'); say('Term restored'); }; }
function mgToggle(k, from, via) { const e = MG.items.find(x => !x.own && x.k === k); if (e) return mgRemove(e);
  MG.items.push({k, note: '', from: from && N[from] ? from : null, via: via || 'card', at: Date.now()}); mgOpen = 'k:' + k; saveMG(); mgSync(); say(capT(k) + ' added to your glossary'); }
function mgButton(parent, k, via, from) { if (!isT(k)) return null; const row = el('div', 'mg-addrow', parent), b = el('button', 'mg-add', row); b.type = 'button'; b.dataset.k = k;
  b.onclick = () => mgToggle(k, from !== undefined ? from : (via === 'card' ? (sel || spot) : null), via); mgLabel(b); return row; }
window.__mg = {button: mgButton};

/* the rail sheet */
function mgOrdered(items, sort) { const L = items.map((e, i) => ({e, i})); if (sort === 'az') L.sort((a, b) => mgName(a.e).localeCompare(mgName(b.e), 'en', {sensitivity: 'base'})); return L; }
function mgSrc(p, e, ro) { if (ro) el('small', '', p, 'Found in ');
  if (e.own) p.append(e.met ? e.met : (ro ? 'Added by them' : 'Added by me'));
  else if (e.from && N[e.from]) { const b = el('button', 'mg-go', p, N[e.from].t); b.type = 'button'; b.setAttribute('aria-label', 'Open ' + N[e.from].t); b.onclick = () => mgOpenIn(e.from, e.k); if (N[e.from].d) p.append(' ' + N[e.from].d); }
  else if (e.via === 'dances') { const dn = DNC.find(x => gk(x.dance) === e.k); p.append('the '); const b = el('button', 'mg-go', p, 'Dances guide'); b.type = 'button'; b.onclick = () => dn && openDance(dn.dance); }
  else p.append('a search');
  if (!ro && e.at) p.append(' · collected ' + shortDate(e.at)); }
function mgEntry(ul, e, first, ro, num) {
  const id = mgId(e), open = !ro && mgOpen === id, dom = 'mgd-' + id.replace(/[^\w-]/g, '_'), li = el('li', 'mg-e' + (first ? ' first' : '') + (open ? ' open' : ''), ul);
  const row = el(ro ? 'div' : 'button', 'mg-row', li);
  if (!ro) { row.type = 'button'; row.setAttribute('aria-expanded', open ? 'true' : 'false'); row.setAttribute('aria-controls', dom); }
  el('span', 'mg-i' + (num ? ' n' : ''), row, first ? (num ? String(num) : mgName(e).charAt(0).toUpperCase()) : '').setAttribute('aria-hidden', 'true');
  const hd = el('span', 'mg-hd', row); el('span', 'mg-n', hd, e.own ? e.w : capT(e.k));
  if (e.own) el('span', 'mg-mine', hd, ro ? 'their term' : 'my term');
  else { const els = mgEls(e.k); if (els.length) { const sp = el('span', 'mg-el', hd); els.forEach(c => el('i', '', sp, elLabel(c))); } }
  if (!e.own) el('span', 'mg-def', row, GLO[e.k]);
  const own = (e.own ? e.def : e.note) || ''; if (own.trim()) { if (ro) el('span', 'mg-k me mg-ownk', row, e.own ? 'Their definition' : 'In their own words'); el('span', 'mg-own', row, own.trim()); }
  if (ro) { mgSrc(el('span', 'mg-src', row), e, true); return; }
  row.onclick = () => { mgOpen = open ? null : id; glossarySheet(true); const r = sheet.querySelector(`[aria-controls="${dom}"]`); if (r) { r.focus({preventScroll: true}); r.parentNode.scrollIntoView({block: 'nearest'}); } };
  if (!open) return;
  const d = el('div', 'mg-d', li); d.id = dom;
  if (!e.own) { el('p', '', d, GLO[e.k]); const M = GMT[e.k] || {}; if (M.ex) el('p', 'mg-ex', d, M.ex); }
  const lab = el('label', 'mg-f', d); el('span', 'mg-k me', lab, e.own ? 'What it means' : 'In my own words');
  const ta = quiet(el('textarea', 'mg-note', lab)); ta.maxLength = 280; ta.rows = 3; ta.value = own; ta.placeholder = e.own ? 'Write it in your own words.' : 'Say it the way you would explain it to a friend.';
  ta.setAttribute('aria-label', `${e.own ? 'What it means' : 'In my own words'}, for ${mgName(e)}. 280 characters at most`);
  const cnt = el('div', 'mg-cnt', d, `${ta.value.length} / 280`); cnt.setAttribute('aria-live', 'polite');
  let tmr = 0; const put = () => { clearTimeout(tmr); if (mgFlush === put) mgFlush = null; const v = ta.value.slice(0, 280), was = e.own ? e.def : e.note; if (v === was) return; if (e.own) e.def = v; else e.note = v; saveMG(); };
  ta.oninput = () => { cnt.textContent = `${ta.value.length} / 280`; clearTimeout(tmr); tmr = setTimeout(put, 400); mgFlush = put; }; ta.onblur = put;      /* only unsaved typing is flushed when the page is hidden */
  ta.onfocus = () => { if (COARSE()) setTimeout(() => ta.scrollIntoView({block: 'center'}), 250); };
  el('span', 'mg-k', d, 'Found in'); mgSrc(el('p', 'mg-src', d), e);
  const ft = el('div', 'mg-foot', d);
  if (!e.own) { const o = el('button', 'mg-go', ft, 'Open the full entry'); o.type = 'button'; o.onclick = () => showTerm(e.k); } else el('span', '', ft);
  const rm = el('button', 'mg-rm', ft, 'Remove'); rm.type = 'button'; rm.setAttribute('aria-label', `Remove ${mgName(e)} from my glossary`); rm.onclick = () => mgRemove(e); }
function mgNew(parent) { const b = el('button', 'mg-new', parent, '＋ Add your own term'); b.type = 'button'; b.onclick = () => mgForm(b); return b; }
function mgForm(btn) { const f = el('form', 'mg-form'); btn.replaceWith(f); f.noValidate = true;
  el('span', 'mg-k', f, 'Your own term');
  const L = (t, opt) => { const l = el('label', 'mg-l', f, t); if (opt) el('em', '', l, 'optional'); return l; };
  const w = el('input', 'mg-in', L('Term')); w.maxLength = 60; w.placeholder = 'e.g. riff, hook, drop';
  w.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); d.focus(); } }); quiet(w);
  let d = null; d = quiet(el('textarea', 'mg-note', L('What it means'))); d.maxLength = 280; d.rows = 3; d.placeholder = 'Write it in your own words.';
  const c = el('div', 'mg-cnt', f, '0 / 280'); c.setAttribute('aria-live', 'polite'); d.oninput = () => c.textContent = d.value.length + ' / 280';
  const m = quiet(el('input', 'mg-in', L('Where you met it', true))); m.maxLength = 60; m.placeholder = 'e.g. class, a lantern, a song';
  const act = el('div', 'mg-act', f), sv = el('button', 'mg-b gold', act, 'Save term'), cn = el('button', 'mg-b', act, 'Cancel'); sv.type = 'submit'; cn.type = 'button';
  el('small', 'mg-hint', f, 'It will be marked “my term” so it is never mistaken for one of the Garden’s definitions.');
  const back = () => { glossarySheet(true); const n = sheet.querySelector('.mg-new'); if (n) n.focus(); };
  cn.onclick = back;
  f.addEventListener('keydown', e => { if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); back(); } else if (e.key === 'Enter' && e.target === w) { e.preventDefault(); d.focus(); } });
  [w, d, m].forEach(x => x.addEventListener('focus', () => { if (COARSE()) setTimeout(() => x.scrollIntoView({block: 'center'}), 250); }));
  f.onsubmit = e => { e.preventDefault(); const word = w.value.trim().replace(/\s+/g, ' '); if (!word) { say('Write the term first'); toast('Write the term first', 2500); w.focus(); return; }
    const k = gk(word); if (k) { toast(`“${esc(capT(k))}” is already in the Garden. <button class="undo">Open it</button>`, 7000); const u = $('#toast .undo'); if (u) u.onclick = () => { $('#toast').style.display = 'none'; showTerm(k); }; w.focus(); w.select(); return; }
    if (MG.items.some(x => x.own && fold(x.w) === fold(word))) { toast('That term is already in your glossary', 3000); return; }
    const id = Date.now().toString(36); MG.items.push({own: 1, id, w: word, def: d.value.trim().slice(0, 280), met: m.value.trim().slice(0, 60), at: Date.now()});
    mgOpen = 'o:' + id; mgFocus = {id: 'o:' + id}; saveMG(); glossarySheet(true); say(word + ' added to your glossary'); };
  w.focus(); }
function mgStarters() { const H = sIndex().homes, last = trail.length ? trail[trail.length - 1] : null;
  const ks = last ? Object.keys(H).filter(k => H[k].includes(last)).slice(0, 3) : []; return ks.length ? ks : ['sarabande', 'ritornello', 'hemiola'].filter(k => GLO[k]); }
function glossarySheet(keep) { const st = keep ? sheet.scrollTop : 0; sheet.innerHTML = ''; sheet.dataset.kind = 'glossary'; mgShared = null;
  const n = MG.items.length; el('h3', '', sheet, 'MY GLOSSARY' + (n ? ' · ' + n : ''));
  if (!n) { const box = el('div', 'mg-empty', sheet); el('p', 'mg-lead', box, 'Nothing here yet.');
    const p = el('p', '', box); p.append('Open any definition in the Garden and choose\u00a0'); const sp = el('span', 'mg-spec', p); el('i', '', sp, '＋'); sp.append('My glossary'); p.append(' to keep it. Or add a term of your own.');
    el('span', 'mg-k', box, 'A place to start'); const s = el('div', 'mg-start', box);
    mgStarters().forEach(k => { const b = el('button', 'mg-go', s, capT(k)); b.type = 'button'; b.onclick = () => showTerm(k); });
    mgNew(box); el('p', 'lnote', box, 'Your glossary lives in this browser only. To keep it, share a link or print it.'); sheet.scrollTop = st;
    const F = mgFocus; mgFocus = null; if (F || !keep) { const fx = sheet.querySelector('.mg-new'); if (fx) fx.focus({preventScroll: true}); } return; }
  el('p', 'lnote', sheet, 'Terms you collect as you explore, with the Garden’s definition and your own words beside it.');
  mgNew(sheet);
  if (n === 1 && !mgOpen && !keep) mgOpen = mgId(MG.items[0]);
  if (n > 1) { const tl = el('div', 'mg-tools', sheet); el('span', 'mg-k', tl, 'Sort'); const g = el('div', 'mg-sort', tl); g.setAttribute('role', 'group'); g.setAttribute('aria-label', 'Sort my glossary');
    [['az', 'A–Z'], ['made', innerWidth < 360 ? 'My order' : 'In the order I collected them']].forEach(([v, t]) => { const b = el('button', '', g, t); b.type = 'button'; b.setAttribute('aria-pressed', MG.sort === v ? 'true' : 'false'); b.onclick = () => { MG.sort = v; mgFocus = {sort: v}; saveMG(); glossarySheet(true); }; }); }
  let ul = null; const draw = () => { ul.innerHTML = ''; const q = fold(mgQ.trim()); let last = null;
    mgOrdered(MG.items, MG.sort).forEach(({e, i}) => { if (q && !fold([mgName(e), e.own ? e.def : GLO[e.k], e.own ? e.met : e.note].join(' ')).includes(q)) return;
      const L = mgName(e).charAt(0).toUpperCase(), first = MG.sort === 'made' || L !== last; last = L; mgEntry(ul, e, first, false, MG.sort === 'made' ? i + 1 : 0); });
    if (!ul.children.length) el('li', 'mg-none lnote', ul, 'Nothing in your glossary matches.'); };
  if (n >= 12) { const f = quiet(el('input', 'vf mg-find', sheet)); f.type = 'search'; f.placeholder = 'Find in my glossary…'; f.setAttribute('aria-label', 'Find in my glossary'); f.value = mgQ; f.oninput = () => { mgQ = f.value; draw(); }; }
  else mgQ = '';
  ul = el('ul', 'mg-list', sheet); draw();
  const kp = el('div', 'mg-keep', sheet); el('h4', '', kp, 'Keep and share');
  const nl = el('label', 'mg-l', kp, 'Your name (optional)'), nm = quiet(el('input', 'mg-in', nl)); nm.maxLength = 40; nm.placeholder = 'A first name is enough'; nm.value = MG.by; nm.oninput = () => { MG.by = nm.value.trim().slice(0, 40); saveMG(); };
  el('p', 'lnote mg-namenote', kp, 'Your name goes into links and sheets you share.');
  const act = el('div', 'mg-act', kp), pr = el('button', 'mg-b gold', act, '▤ Print sheet'), sh = el('button', 'mg-b', act, '⧉ Share link'), cp = el('button', 'mg-b', act, 'Copy as text');
  pr.onclick = () => glossarySheetPage(MG, false); sh.onclick = async () => shareLink(await mgLink(MG), 'Anyone who opens it can read your glossary.'); cp.onclick = () => mgCopy(MG, false);
  el('p', 'lnote', kp, 'Your glossary lives in this browser only. To keep it, share a link or print it.');
  const clr = el('button', 'mg-rm mg-clear', kp, 'Clear my glossary'); clr.type = 'button'; clr.setAttribute('aria-label', 'Clear my glossary from this browser'); clr.onclick = mgClear;
  sheet.scrollTop = st;
  const o = sheet.querySelector('.mg-e.open'); if (o && !keep) setTimeout(() => o.scrollIntoView({block: 'nearest'}), 30);
  const F = mgFocus; mgFocus = null; let fx = null;
  if (F && F.sort) fx = [...sheet.querySelectorAll('.mg-sort button')].find(b => b.getAttribute('aria-pressed') === 'true');
  else if (F && F.id) fx = sheet.querySelector(`[aria-controls="mgd-${F.id.replace(/[^\w-]/g, '_')}"]`);
  else if (F && F.near != null) { const rs = sheet.querySelectorAll('.mg-row'); fx = rs.length ? rs[Math.max(0, Math.min(F.near, rs.length - 1))] : sheet.querySelector('.mg-new'); }
  else if (!keep) fx = sheet.querySelector('.mg-e.open .mg-row') || sheet.querySelector('.mg-new');
  if (fx) fx.focus({preventScroll: true}); }

/* clear everything from this browser (for shared school computers), with Undo */
function mgClear() { const was = {by: MG.by, sort: MG.sort, items: MG.items.slice()}; MG.items = []; MG.by = ''; mgOpen = null; mgQ = ''; saveMG(); mgFocus = {near: 0}; mgSync();
  toast('Glossary cleared from this browser <button class="undo" aria-label="Undo clear">Undo</button>', 8000); say('Glossary cleared. Undo is available.');
  const u = $('#toast .undo'); if (u) u.onclick = () => { MG.by = was.by; MG.sort = was.sort; MG.items = was.items; saveMG(); mgSync(); toast('Glossary restored'); say('Glossary restored'); }; }

/* links, text and the print sheet */
const mgPack = g => ({v: 1, b: g.by || '', d: today(), s: g.sort, i: g.items.map(e => e.own ? [1, e.w, e.def || '', e.met || ''] : [0, e.k, e.note || '', e.from || '', e.via || ''])});
const mgLink = async g => HOME + '#g=' + await pack(mgPack(g));
function mgFromPack(o) { if (!o || typeof o !== 'object' || !Array.isArray(o.i)) return null;
  const raw = o.i.filter(a => Array.isArray(a)).map(a => a[0] ? {own: 1, w: a[1], def: a[2], met: a[3]} : {k: a[1], note: a[2], from: a[3], via: a[4]}), items = mgClean(raw, false);
  return {by: S60(o.b, 40), d: S60(o.d, 40), sort: o.s === 'az' ? 'az' : 'made', items, lost: o.i.length - items.length}; }
function mgText(g, ro) { const items = mgOrdered(g.items, g.sort).map(x => x.e), L = [];
  L.push(g.by ? `${g.by}’s glossary` : (ro ? 'A shared glossary' : 'My glossary'), `The Garden of Earthly Sounds · ${g.d || today()} · ${items.length} term${items.length === 1 ? '' : 's'}`, '');
  items.forEach(e => { if (e.own) { L.push(`${e.w.toUpperCase()} (${ro ? 'their' : 'my'} term)`); if (e.def) L.push((ro ? 'Their definition: ' : 'What it means: ') + e.def); if (e.met) L.push('Found in: ' + e.met); }
    else { const els = mgEls(e.k).map(elLabel); L.push(e.k.toUpperCase() + (els.length ? ` (${els.join(', ')})` : ''), GLO[e.k]); if (e.note && e.note.trim()) L.push((ro ? 'In their own words: ' : 'In my own words: ') + e.note.trim()); L.push('Found in: ' + (e.from && N[e.from] ? `${N[e.from].t}${N[e.from].d ? ' (' + N[e.from].d + ')' : ''}` : (e.via === 'dances' ? 'the Dances guide' : 'a search'))); }
    L.push(''); });
  return L.join('\n').trim() + '\n'; }
async function mgCopy(g, ro) { const t = mgText(g, ro); try { await navigator.clipboard.writeText(t); toast('Glossary copied as text'); say('Glossary copied as text'); }
  catch (err) { toast('Copy this text<textarea readonly style="width:min(520px,80vw);height:160px;display:block;margin-top:6px;background:#0b0906;color:#ece2c8;border:1px solid #3a3222;border-radius:6px;font:12px Outfit,sans-serif">' + esc(t) + '</textarea>', 15000); } }
async function glossarySheetPage(g, ro) {
  const items = mgOrdered(g.items, g.sort).map(x => x.e), link = await mgLink(g), own = items.filter(e => e.own).length, name = g.by ? `${g.by}’s glossary` : (ro ? 'A shared glossary' : 'My glossary'), IW = ro ? 'In their own words' : 'In my own words';
  const T = {}; items.forEach(e => { if (e.own) T['My own'] = (T['My own'] || 0) + 1; else mgEls(e.k).forEach(c => { const l = elLabel(c); T[l] = (T[l] || 0) + 1; }); });
  const tally = Object.keys(T).sort((a, b) => (a === 'My own') - (b === 'My own') || T[b] - T[a]).map(k => `<span>${esc(k)}<b>${T[k]}</b></span>`).join('');
  const rows = items.map(e => { if (e.own) return `<div class="e own"><dt><span class="nm">${esc(e.w)}</span><span class="mine">${ro ? 'Their term' : 'My term'}</span>${e.met ? `<span class="fr">Found in ${esc(e.met)}</span>` : ''}</dt><dd>${e.def ? `<blockquote><small>${ro ? 'Their definition' : 'My definition'}</small>${esc(e.def)}</blockquote>` : `<div class="lines"><small>${ro ? 'Their definition' : 'My definition'}</small><i></i><i></i><i></i></div>`}</dd></div>`;
    const M = GMT[e.k] || {}, els = mgEls(e.k).map(elLabel), fr = e.from && N[e.from] ? `Found in ${N[e.from].t}${N[e.from].d ? ', ' + N[e.from].d : ''}` : (e.via === 'dances' ? 'Found in the Dances guide' : 'Found in a search');
    const mine = e.note && e.note.trim() ? `<blockquote><small>${IW}</small>${esc(e.note.trim())}</blockquote>` : `<div class="lines"><small>${IW}</small><i></i><i></i><i></i></div>`;
    return `<div class="e"><dt><span class="nm">${esc(capT(e.k))}</span>${els.length ? `<span class="el">${esc(els.join(' · '))}</span>` : ''}<span class="fr">${esc(fr)}</span></dt><dd><p class="df">${esc(GLO[e.k])}</p>${M.ex ? `<p class="ex">${esc(M.ex)}</p>` : ''}${mine}</dd></div>`; }).join('');
  const date = today(), F = HOME.replace(/[^/]*$/, '') + 'fonts/';
  const legend = `Printed from the Garden of Earthly Sounds on ${esc(date)}. Definitions are the Garden’s; the words marked “${IW.toLowerCase()}” are ${g.by ? esc(g.by) + '’s' : (ro ? 'the sharer’s' : 'the student’s')} own.`;
  const html = `<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(name)} · The Garden of Earthly Sounds</title><style>${MG_SHEET_CSS.replace(/__F__/g, F)}</style></head>
<body><div class="bar"><button onclick="print()">Print or save as PDF</button><button onclick="document.body.classList.toggle('night')">Paper · Night</button><button onclick="document.body.classList.toggle('lined')">Writing lines</button></div><main>
<div class="over">A glossary from the Garden of Earthly Sounds</div><h1>${esc(name)}</h1><div class="by">${esc([date, `${items.length} term${items.length === 1 ? '' : 's'}, ${g.sort === 'az' ? 'A to Z' : 'in the order collected'}`, own ? `${own} of ${ro ? 'their' : 'my'} own` : ''].filter(Boolean).join(' · '))}</div>
<p class="tally">${tally}</p><dl>${rows}</dl>
<footer><p class="legend"><i></i>${legend}</p>Open this glossary in the Garden: <a href="${esc(link)}">${esc(link.length > 160 ? link.slice(0, 120) + '…' : link)}</a><br>The Garden of Earthly Sounds is a living document in the form of an interactive page. Please e-mail shmungfroi@gmail.com to make any suggestions, comments or corrections.</footer>
</main></body></html>`;
  const url = URL.createObjectURL(new Blob([html], {type: 'text/html'})); let w = null; try { w = window.open(url, '_blank'); } catch (err) {}
  if (!w) { const fn = ((g.by ? g.by + '-' : '') + 'glossary').replace(/[^\w\- ]+/g, '').trim().replace(/\s+/g, '-').toLowerCase() + '.html';
    let dl = null; try { dl = window.claude && window.claude.use ? await window.claude.use('downloads') : null; } catch (err) { dl = null; }
    if (dl) { try { await dl.save({filename: fn, data: html}); toast('Glossary sheet saved: open it to print or save as PDF', 4000); } catch (err) { if (!err || err.code !== 'declined') toast('The glossary sheet could not be saved here; try Copy as text, or open the Garden on its own page', 5000); } }
    else { const a = document.createElement('a'); a.href = url; a.download = fn; document.body.appendChild(a); a.click(); a.remove(); toast('The glossary sheet was downloaded: open it to print or save as PDF', 4000); } }
  window.__lastSheet = html; }

/* someone else's glossary, opened from a #g= link: read only, never written to storage until kept */
function showSharedGlossary(o) { const S = mgFromPack(o); if (!S || !S.items.length) { toast('That glossary link could not be read', 4000); return; } mgShared = S; const n = S.items.length, b = document.querySelector('.rail button[data-sheet="glossary"]');
  closeSheet(); sheet.innerHTML = ''; sheet.dataset.kind = 'glossary-shared'; sheet.classList.add('open'); if (b) b.classList.add('on'); sheet.scrollTop = 0; mgShared = S;
  el('h3', '', sheet, (S.by ? S.by.toUpperCase() + '’S GLOSSARY' : 'A SHARED GLOSSARY') + ' · ' + n);
  const box = el('div', 'mg-shared', sheet); el('span', 'mg-k', box, 'Shared' + (S.d ? ' · ' + S.d : '')); el('p', '', box, 'You are reading a shared glossary. You can’t change it here.'); if (S.lost > 0) el('p', 'mg-lost', box, `${S.lost} ${S.lost === 1 ? 'term is' : 'terms are'} no longer in the Garden and ${S.lost === 1 ? 'is' : 'are'} not shown.`);
  const act = el('div', 'mg-act', box), kp = el('button', 'mg-b gold', act, 'Keep a copy'), pr = el('button', 'mg-b', act, '▤ Print sheet'), bk = el('button', 'mg-b', act, 'Back to mine');
  kp.onclick = () => mgKeep(S); pr.onclick = () => glossarySheetPage(S, true); bk.onclick = () => { closeSheet(); openGlossary(); };
  const ul = el('ul', 'mg-list ro', sheet); let last = null;
  mgOrdered(S.items, S.sort).forEach(({e, i}) => { const L = mgName(e).charAt(0).toUpperCase(), first = S.sort === 'made' || L !== last; last = L; mgEntry(ul, e, first, true, S.sort === 'made' ? i + 1 : 0); }); }
function mgKeep(S) { const before = MG.items.slice(); let added = 0;
  S.items.forEach(e => { if (e.own ? MG.items.some(x => x.own && fold(x.w) === fold(e.w)) : mgHas(e.k)) return; MG.items.push(Object.assign({}, e, {at: Date.now()}, e.own ? {id: uid('o')} : {})); added++; });
  saveMG(); closeSheet(); openGlossary(); mgSync();
  toast(`Kept in your glossary${added ? '' : ' (you had every term already)'} <button class="undo" aria-label="Undo keep a copy">Undo</button>`, 6000);
  const u = $('#toast .undo'); if (u) u.onclick = () => { MG.items = before; saveMG(); mgSync(); toast('Copy undone'); }; }
