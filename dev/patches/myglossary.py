"""My glossary (19 Nov 2026, §7.8 Part B). Needs search_all.py applied first. Idempotent: run, then ./build.sh.
Design: Fable (dev/patches/myglossary/mg.css, sheet.css); copy: Sonnet; code: dev/patches/myglossary/mg.js."""
import sys, json, pathlib
R = pathlib.Path(__file__).resolve().parents[2]; H = R / 'dev' / 'patches' / 'myglossary'
tp, cp = R / 'src' / 'template.html', R / 'card.js'
t, c = tp.read_text(encoding='utf-8'), cp.read_text(encoding='utf-8')
if '/* search reaches terms' not in t and '/* ---- search reaches terms' not in t: sys.exit('apply search_all.py first')
def rep(s, a, b):
    assert s.count(a) == 1, ('anchor', a[:90], s.count(a)); return s.replace(a, b)
if 'My glossary: terms a student collects' not in t:
    css = (H / 'mg.css').read_text(encoding='utf-8'); js = (H / 'mg.js').read_text(encoding='utf-8'); sh = (H / 'sheet.css').read_text(encoding='utf-8')
    t = rep(t, ".pg-nav[hidden]{display:none}\n</style>", ".pg-nav[hidden]{display:none}\n" + css + "</style>")
    t = rep(t, '<button data-sheet="journeys" title="Journeys and listening tasks">⤳<small>Journeys</small></button>',
        '<button data-sheet="journeys" title="Journeys and listening tasks">⤳<small>Journeys</small></button>\n  <button data-sheet="glossary" title="Your glossary: terms you collect and your own words" aria-label="My glossary">❧<small><b>My </b>glossary</small></button>')
    t = rep(t, "if (kind === 'journeys') return journeySheet();", "if (kind === 'journeys') return journeySheet();\n  if (kind === 'glossary') return glossarySheet();")
    t = rep(t, "if (Q.task) { unpack(Q.task)", "if (Q.g) { unpack(Q.g).then(o => o && showSharedGlossary(o)).catch(() => toast('That glossary link could not be read')); return true; }\n  if (Q.task) { unpack(Q.task)")
    t = rep(t, "el('p', '', sheet, GLO[key]); if (M.ex) el('p', 'tp-ex', sheet, M.ex);", "el('p', '', sheet, GLO[key]); if (M.ex) el('p', 'tp-ex', sheet, M.ex); mgButton(sheet, key, 'search', null);")
    t = rep(t, "} else p.appendChild(document.createTextNode(ex.work)); }", "} else p.appendChild(document.createTextNode(ex.work)); }\n      if (window.__mg) window.__mg.button(d, gk(r.dance), 'dances', ex.lantern || null);")
    t = rep(t, "     ['Every line is a path:',", "     ['My glossary ❧:', ' choose “＋ My glossary” on any definition to keep the term. The tab lists what you have collected, with the Garden’s definition, where you found it and a box for your own words. Add terms of your own, sort A–Z or by the order you collected them, then print it, copy it as text or share it as a link. It stays in this browser, so share or print it to keep it.'],\n     ['Every line is a path:',")
    t = rep(t, "const gk = x => { const k = String(x || '').toLowerCase().replace(/\\s+/g, ' ').trim(); if (!k) return null; if (GLO[k]) return k;",
        "const isT = k => typeof k === 'string' && Object.prototype.hasOwnProperty.call(GLO, k) && typeof GLO[k] === 'string';      /* a real glossary term, never 'constructor' or '__proto__' */\nconst gk = x => { const k = String(x || '').toLowerCase().replace(/\\s+/g, ' ').trim(); if (!k) return null; if (isT(k)) return k;")
    t = rep(t, "return t.find(y => GLO[y]) || null; };", "return t.find(y => isT(y)) || null; };")
    t = rep(t, "readHash(location.hash); drawTrail();", "const MG_SHEET_CSS = " + json.dumps(sh, ensure_ascii=False) + ";\n" + js + "\nreadHash(location.hash); drawTrail();")
    tp.write_text(t, encoding='utf-8'); print('template: applied')
else: print('template: already applied')
if 'window.__mg' not in c:
    c = rep(c, "if (M.ex) h('p', 'gex', d, M.ex); glossExtras(d, M);", "if (M.ex) h('p', 'gex', d, M.ex); glossExtras(d, M); if (window.__mg) window.__mg.button(d, key, 'card');")
    cp.write_text(c, encoding='utf-8'); print('card.js: applied')
else: print('card.js: already applied')
