"""No focus frame around the map for mouse or touch (Justin, 19 Nov: "a blue rectangle that turns gold").
The blue was the browser's own focus ring (macOS accent colour) on the focusable <svg id="map">; the gold was #map:focus-visible.
Now: never for pointer users; a faint 1px gold line only when the map is reached with the Tab key (keyboard users still see where they are). Idempotent."""
import pathlib
R = pathlib.Path(__file__).resolve().parents[2]; tp = R / 'src' / 'template.html'; t = tp.read_text(encoding='utf-8')
def rep(a, b):
    global t
    if b in t: return
    assert t.count(a) == 1, ('anchor', a[:80], t.count(a)); t = t.replace(a, b)
rep("#map:focus-visible{outline:2px solid var(--gold);outline-offset:-3px}",
    "#map:focus,#map:focus-visible{outline:none} #map.kbd:focus{outline:1px solid rgba(201,162,74,.55);outline-offset:-2px}      /* frame only for Tab users (19 Nov) */")
rep("const $ = s => document.querySelector(s), svg = $('#map'), cam = $('#cam'), panel = $('#panel');",
    "const $ = s => document.querySelector(s), svg = $('#map'), cam = $('#cam'), panel = $('#panel');\n"
    "let tabbed = false; addEventListener('keydown', e => { if (e.key === 'Tab') tabbed = true; }, true); addEventListener('pointerdown', () => { tabbed = false; svg.classList.remove('kbd'); }, true);\n"
    "svg.addEventListener('focus', () => svg.classList.toggle('kbd', tabbed)); svg.addEventListener('blur', () => svg.classList.remove('kbd'));      /* the map's focus frame shows only after Tab */")
tp.write_text(t, encoding='utf-8'); print('applied')
