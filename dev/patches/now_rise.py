"""Now storey: stars sit at the year of their work; living stems run from each Now lantern up to its latest work. Idempotent."""
import sys
P = '/home/claude/thegardenofearthlysounds/src/template.html'
t = open(P, encoding='utf-8').read()
def once(old, new):
    global t
    if new in t and old not in t: return
    assert t.count(old) == 1, ('count', t.count(old), old[:80]); t = t.replace(old, new)

# CSS: stems faint at rest, quieter when something is in focus
once("#map.focus #stars .st:not(.me){opacity:.35}",
     "#map.focus #stars .st:not(.me){opacity:.35}\n/* living stems: a Now lantern's line up to its latest work */\n#map #lstems line{stroke-width:.32;stroke-linecap:round;stroke-opacity:.42} #map #lstems circle{fill-opacity:.6} #map.focus #lstems{opacity:.3} #map #lstems .on line{stroke-opacity:.9} #map #lstems .on circle{fill-opacity:1}")

# placement: rise to the work's year, beside the lantern's stem
once("""/* ---------- makers of the Now storey: every composer of a Now work is a small star beside their lantern; click to follow their thread ---------- */
const gStars = document.createElementNS(SVGNS, 'g'); gStars.setAttribute('id', 'stars'); cam.appendChild(gStars);""",
"""/* ---------- makers of the Now storey: every composer of a Now work is a small star at the year of that work, beside their lantern's stem; click to follow their thread ---------- */
const nowYr = s => { const m = String(s || '').match(/\\d{4}/); return m ? +m[0] : null; };
const gStems = document.createElementNS(SVGNS, 'g'); gStems.setAttribute('id', 'lstems'); cam.appendChild(gStems);
const gStars = document.createElementNS(SVGNS, 'g'); gStars.setAttribute('id', 'stars'); cam.appendChild(gStars);
const STEM = {};
(() => {      /* living stems: each Now lantern grows a faint line up to its most recent work; lanterns sharing a column sit side by side */
  const NOWE = LAY.eras.find(e => e.id === 'contemporary'), cols = {}, boxes = [];
  document.querySelectorAll('#map .fm:not(.soil)').forEach(g => g.querySelectorAll('text').forEach(t => { const b = t.getBBox(); if (b.width) boxes.push({id: g.dataset.id, x0: b.x, x1: b.x + b.width, y0: b.y, y1: b.y + b.height}); }));
  D.nodes.filter(n => n.period === 'contemporary' && LAY.nodes[n.id]).forEach(n => { const ys = (n.works || []).map(w => nowYr(w[2])).filter(Boolean); if (!ys.length) return;
    const last = Math.min(NOWE.end, Math.max(...ys)), p = LAY.nodes[n.id], top = yOfYear(last); if (top > p.y - 3) return; (cols[p.x] = cols[p.x] || []).push([n, p, top, last]); });
  Object.values(cols).forEach(list => { list.sort((a, b) => b[1].y - a[1].y); list.forEach(([n, p, top, last], k) => { const dx = list.length > 1 ? (k - (list.length - 1) / 2) * 1.6 : 0, x = p.x + dx, c = FC(p.f) || 'var(--gold)';
    const cuts = boxes.filter(b => x > b.x0 - .5 && x < b.x1 + .5 && b.y1 > top && b.y0 < p.y - 1.3).sort((a, b) => b.y1 - a.y1);      /* the stem breaks around every lantern name it passes, its own included */
    let segs = '', from = p.y - 1.3; cuts.forEach(b => { if (b.y1 + .6 < from - 1 && from - Math.max(top, b.y1 + .6) > 1) segs += `<line x1="${x}" y1="${from}" x2="${x}" y2="${Math.max(top, b.y1 + .6)}" stroke="${c}"/>`; from = Math.min(from, b.y0 - .6); }); if (from - top > 1) segs += `<line x1="${x}" y1="${from}" x2="${x}" y2="${top}" stroke="${c}"/>`;
    const g = document.createElementNS(SVGNS, 'g'); g.dataset.id = n.id; g.innerHTML = `${segs}<circle cx="${x}" cy="${top}" r=".42" fill="${c}"/><title>${n.t}: still growing, latest work here ${last}</title>`;
    gStems.appendChild(g); STEM[n.id] = {g, x}; }); });
})();""")

once("""  const byHome = {}; Object.values(VOICES).forEach(V => { const fs = V.forms.filter(f => N[f.id] && N[f.id].period === 'contemporary' && LAY.nodes[f.id]); if (fs.length) (byHome[fs[0].id] = byHome[fs[0].id] || []).push([V, fs]); });
  const placed = [];""",
"""  const byHome = {}; Object.values(VOICES).forEach(V => { const fs = V.forms.filter(f => N[f.id] && N[f.id].period === 'contemporary' && LAY.nodes[f.id]); if (fs.length) (byHome[fs[0].id] = byHome[fs[0].id] || []).push([V, fs]); });
  const placed = [], yrW = w => Math.max(NOWE.start, Math.min(NOWE.end, nowYr(w[2]) || NOWE.start));""")

once("""    list.sort((a, b) => a[0].first - b[0].first).forEach(([V, fs]) => { let spot = null;
      for (let ring = 0; ring < 9 && !spot; ring++) { const rr = 4 + ring * 1.9, n = Math.max(8, Math.round(2 * Math.PI * rr / 2.4));
        for (let j = 0; j < n; j++) { const a = (j / n) * 2 * Math.PI + ring * .37, x = p.x + Math.cos(a) * rr, y = p.y + Math.sin(a) * rr * .8; if (ok(x, y, F)) { spot = [x, y]; break; } } }
      if (!spot) return; placed.push(spot); const [x, y] = spot, g = document.createElementNS(SVGNS, 'g'); g.setAttribute('class', 'st'); g._V = V; g._fs = fs; g.dataset.x = x; g.dataset.y = y;
      const w = fs[0].works[0][0], d =""",
"""    list.map(([V, fs]) => { const w = fs[0].works.map(x => x[0]).reduce((a, b) => yrW(b) > yrW(a) ? b : a); return [V, fs, w, yrW(w)]; })      /* the work that places the star: their latest here */
      .sort((a, b) => a[3] - b[3]).forEach(([V, fs, w, yr]) => { let spot = null; const sx = (STEM[lid] || {}).x ?? p.x, sy = yOfYear(yr);
      for (let ring = 0; ring < 14 && !spot; ring++) for (const sd of ring ? [1, -1] : [1]) { const x = sx + sd * (2.2 + ring * 2.1);      /* step sideways from the stem, at the same year */
        for (const dy of [0, -.8, .8, -1.6, 1.6]) { if (ok(x, sy + dy, F)) { spot = [x, sy + dy]; break; } } if (spot) break; }
      if (!spot) return; placed.push(spot); const [x, y] = spot, g = document.createElementNS(SVGNS, 'g'); g.setAttribute('class', 'st'); g._V = V; g._fs = fs; g._w = w; g.dataset.x = x; g.dataset.y = y;
      const d =""")

once("""gStars.addEventListener('mousemove', e => { const g = e.target.closest('.st'); if (!g) return; const V = g._V, w = g._fs[0].works[0][0];""",
     """gStars.addEventListener('mousemove', e => { const g = e.target.closest('.st'); if (!g) return; const V = g._V, w = g._w || g._fs[0].works[0][0];""")
open(P, 'w', encoding='utf-8').write(t); print('ok')
