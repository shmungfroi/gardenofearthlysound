"""Fixes after My glossary (19 Nov 2026, Justin: "4 yes fix it of course. 5 yes, both"). Run after myglossary.py. Idempotent.
- A link hash with a stray "%" no longer stops the page loading (readHash decodes safely).
- The search term page is headed THE GARDEN'S GLOSSARY, so it is never confused with the phone bar's "Glossary" (My glossary)."""
import pathlib
R = pathlib.Path(__file__).resolve().parents[2]; tp = R / 'src' / 'template.html'; t = tp.read_text(encoding='utf-8')
def rep(a, b):
    global t
    if b in t: return
    assert t.count(a) == 1, ('anchor', a[:80], t.count(a)); t = t.replace(a, b)
rep("Q[kv.slice(0, i)] = decodeURIComponent(kv.slice(i + 1)); });",
    "let v = kv.slice(i + 1); try { v = decodeURIComponent(v); } catch (err) { v = ''; } Q[kv.slice(0, i)] = v; });      /* a stray % must not stop the page loading */")
rep("el('h3', '', sheet, 'GLOSSARY'); const hd = el('div', 'tp-h', sheet);", "el('h3', '', sheet, 'THE GARDEN’S GLOSSARY'); const hd = el('div', 'tp-h', sheet);")
tp.write_text(t, encoding='utf-8'); print('applied')
