"""Illustrative preview of option 1: families rise from the ground as stems and open at their first form.
Musicmap's restraint: bars, no boxes, uppercase names, straight hairlines, dim at rest, bright in focus."""
import json, math, html, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
LIVE = os.environ.get('LIVE') == '1'      # live map: everything at rest; focus is drawn by the page's CSS
D = json.load(open(os.path.join(HERE, 'data.json')))
N = {n['id']: n for n in D['nodes']}
FAMS = [('keyboard', 'KEYBOARD', '#3fb6a8'), ('chamber', 'CHAMBER', '#4d8fe0'), ('concerto', 'CONCERTO', '#9b7be8'),
        ('sacred', 'SACRED', '#e0b44d'), ('commons', 'THE COMMONS', '#6fbf5a'), ('song', 'SONG', '#e46d9c'),
        ('stage', 'STAGE', '#e0604d'), ('orch', 'ORCHESTRA', '#ec9640')]
GOLD, GOLD_HI, IVORY, RED, GREEN, INK = '#c9a24a', '#f0d48a', '#ece2c8', '#c8473b', '#8fbf6a', '#0b0906'
FC = {f: c for f, _, c in FAMS}
HOME, COLS = {}, []
for g in D['genres']:
    for i in g['l']: HOME[i] = g['great']
for f, _, _ in FAMS:
    for g in D['genres']:
        if g['great'] == f: COLS.append({'fam': f, 'gid': g['id'], 't': g['t'], 'ids': [i for i in g['l'] if i != 'commons' and i in N]})
    loose = [n['id'] for n in D['nodes'] if n['id'] not in HOME and (n.get('lane') or 'song') == f]
    if loose: COLS.append({'fam': f, 'ids': loose, 'style': True})
# --- time: Medieval at the ground, today at the top; each era as tall as its forms need ---
PER = D['periods']
GROUND, PRESENT = 930, 70
weights = [len([n for n in D['nodes'] if n['period'] == p['id']]) + 12 for p in PER]
tot = sum(weights); y = GROUND
for p, w in zip(PER, weights):
    p['y0'] = y; y -= (GROUND - PRESENT) * w / tot; p['y1'] = y        # y0 = bottom (start), y1 = top (end)
def Y(yr, pid=None):
    p = next((q for q in PER if q['id'] == pid), None) or next((q for q in PER if q['start'] <= yr < q['end']), PER[-1])
    t = max(0, min(1, (yr - p['start']) / (p['end'] - p['start'])))
    return p['y0'] - 8 - t * (p['y0'] - p['y1'] - 16)
# --- columns: families either side of the central spire, balanced ---
fam_cols = {f: [c for c in COLS if c['fam'] == f] for f, _, _ in FAMS}
CW, GAP, SPW = 31, 16, 46
left = ['keyboard', 'chamber', 'concerto', 'sacred']; right = ['song', 'stage', 'orch']
W = 1600; CX = 150 + (W - 150 - 90) / 2
def width(f): return len(fam_cols[f]) * CW
lw = sum(width(f) for f in left) + GAP * len(left); rw = sum(width(f) for f in right) + GAP * len(right)
half = max(lw, rw); gl = GAP + (half - lw) / len(left); gr = GAP + (half - rw) / len(right)      # equal wings either side of the spire
X = {}
x = CX - SPW / 2 - half
for f in left: X[f] = x; x += width(f) + gl
x = CX + SPW / 2 + gr
for f in right: X[f] = x; x += width(f) + gr
X['commons'] = CX - SPW / 2
POS = {}
for f, _, _ in FAMS:
    for k, c in enumerate(fam_cols[f]):
        cx = X[f] + (SPW / 2 if f == 'commons' else k * CW + CW / 2)
        for i in c['ids']: POS[i] = [cx, Y(N[i]['y'], N[i]['period'])]
# forms dated almost together in one column share the row: spread them sideways, dates unchanged
for f, _, _ in FAMS:
    for c in fam_cols[f]:
        ids = sorted([i for i in c['ids'] if i in POS], key=lambda i: POS[i][1]); grp = []
        for i in ids + [None]:
            if i and grp and POS[i][1] - POS[grp[-1]][1] < 6: grp.append(i); continue
            if len(grp) > 1:
                step = min(16, CW * 1.1 / (len(grp) - 1)) if f != "commons" else 9
                for k, j in enumerate(grp): POS[j][0] += (k - (len(grp) - 1) / 2) * step
                if f != 'commons':               # keep the spread inside the family's bar
                    lo, hi = X[f] + 4, X[f] + width(f) - 4; xs = [POS[j][0] for j in grp]
                    sh = max(0, lo - min(xs)) - max(0, max(xs) - hi)
                    for j in grp: POS[j][0] += sh
            grp = [i] if i else []
POS['commons'] = [CX, GROUND + 70]
first = {f: max((POS[i][1] for c in fam_cols[f] for i in c['ids']), default=GROUND) + 10 for f in X}
first['commons'] = GROUND

# --- labels: two uppercase lines that always touch their own point; none may touch another name or point ---
from PIL import ImageFont
FS = 3.4; LH = FS * 1.12; PAD = .7
_F = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'Outfit-Regular.ttf'), 100)
def tw(t): return _F.getlength(t) / 100 * FS          # true width in map units (Arial metrics)
NAMES = json.load(open(os.path.join(HERE, 'names.json')))
SMALL = .8
def lines(i):
    if i in NAMES: return NAMES[i]
    t = N[i]['t'].upper().replace(':', ''); w = t.split()
    if len(t) <= 13 or len(w) == 1: return [t]
    cut = min(range(1, len(w)), key=lambda k: max(tw(' '.join(w[:k])), tw(' '.join(w[k:]))))
    return [' '.join(w[:cut]), ' '.join(w[cut:])]
small = lambda ln: ln[:1].islower()
def lw(ln): return tw(ln) * (SMALL if small(ln) else 1) + len(ln) * (.1 if small(ln) else .25) + .6      # include the letter-spacing
def lh(ln): return LH * (SMALL if small(ln) else 1)
def cands(x, y, w, h):          # every place a name can sit and still touch its point (x, y)
    g = 1.2; out = []
    for fx, pen in [(0, 0), (-.3, 2), (.3, 2), (-.5, 4), (.5, 4), (-.75, 6), (.75, 6)]:
        out.append(((x - w / 2 + fx * w, y - g - h, x + w / 2 + fx * w, y - g), pen))          # above
        out.append(((x - w / 2 + fx * w, y + g, x + w / 2 + fx * w, y + g + h), pen + 1))      # below
    out.append(((x + g + .6, y - h / 2, x + g + .6 + w, y + h / 2), 3))                       # right
    out.append(((x - g - .6 - w, y - h / 2, x - g - .6, y + h / 2), 3))                       # left
    return out
def ov(r, q): return max(0, min(r[2], q[2]) - max(r[0], q[0]) + PAD) * max(0, min(r[3], q[3]) - max(r[1], q[1]) + PAD * .5)
IDS = [i for i in POS if i != 'commons']
TXT = {i: lines(i) for i in IDS}
SZ = {i: (max(lw(ln) for ln in L), sum(lh(ln) for ln in L)) for i, L in TXT.items()}
CAND = {i: cands(*POS[i], *SZ[i]) for i in IDS}
PT = {i: (POS[i][0] - .9, POS[i][1] - .9, POS[i][0] + .9, POS[i][1] + .9) for i in IDS}
choice = {i: 0 for i in IDS}
def cost(i, k):
    r, pen = CAND[i][k]; c = pen * .02
    for j in IDS:
        if j == i: continue
        if abs(POS[j][1] - POS[i][1]) > 30 or abs(POS[j][0] - POS[i][0]) > 60: continue
        c += 50 * ov(r, CAND[j][choice[j]][0]) + 50 * ov(r, PT[j])
    return c
for it in range(30):                     # settle: each name moves to its least crowded place, until nothing changes
    moved = 0
    for i in sorted(IDS, key=lambda i: POS[i][1]):
        best = min(range(len(CAND[i])), key=lambda k: cost(i, k))
        if best != choice[i] and cost(i, best) < cost(i, choice[i]) - 1e-9: choice[i] = best; moved += 1
    if not moved: break
def bad(i): return cost(i, choice[i]) - CAND[i][choice[i]][1] * .02 > 1e-6
for _ in range(6):               # where one name cannot settle alone, move it together with each crowded neighbour
    stuck = [i for i in IDS if bad(i)]
    if not stuck: break
    for i in stuck:
        near = [j for j in IDS if j != i and abs(POS[j][1] - POS[i][1]) < 24 and abs(POS[j][0] - POS[i][0]) < 70]
        for j in near:
            ci, cj = choice[i], choice[j]; best = (cost(i, ci) + cost(j, cj), ci, cj)
            for ki in range(len(CAND[i])):
                choice[i] = ki
                for kj in range(len(CAND[j])):
                    choice[j] = kj; t = cost(i, ki) + cost(j, kj)
                    if t < best[0] - 1e-9: best = (t, ki, kj)
            choice[i], choice[j] = best[1], best[2]
LAB = {i: (TXT[i], CAND[i][choice[i]][0]) for i in IDS}
clash = [(i, j) for n, i in enumerate(IDS) for j in IDS[n + 1:] if ov(LAB[i][1], LAB[j][1]) > PAD * PAD * .5 + 1e-6]
cover = [(i, j) for i in IDS for j in IDS if i != j and ov(LAB[i][1], PT[j]) > PAD * PAD * .5 + 1e-6]
print(f'labels: {len(clash)} name clashes, {len(cover)} names covering another point, settled in {it + 1} passes')
for i, j in clash[:12]: print('  clash:', N[i]['t'], '|', N[j]['t'])
for i, j in cover: print('  cover:', N[i]['t'], 'over point of', N[j]['t'], [round(v,1) for v in POS[i]], [round(v,1) for v in POS[j]])
FOCUS = None if LIVE else ('sonataform' if 'sonataform' in N else next(i for i in N if N[i]['t'] == 'Sonata form'))
web = {FOCUS} | {b if a == FOCUS else a for a, b, t in D['links'] if FOCUS in (a, b)}

o = []
o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} 1100" width="{W}" height="1100" font-family="Outfit, sans-serif">')
o.append('<defs><linearGradient id="py" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#6fbf5a" stop-opacity=".55"/><stop offset=".25" stop-color="#3b5a2a" stop-opacity=".55"/><stop offset="1" stop-color="#1c1a12" stop-opacity=".9"/></linearGradient>')
for f, _, c in FAMS:
    o.append(f'<linearGradient id="st-{f}" x1="0" x2="0" y1="1" y2="0"><stop offset="0" stop-color="{c}" stop-opacity=".14"/><stop offset=".55" stop-color="{c}" stop-opacity=".28"/><stop offset="1" stop-color="{c}" stop-opacity=".42"/></linearGradient>')
o.append('<radialGradient id="glow" cx=".5" cy="1" r=".6"><stop offset="0" stop-color="#6fbf5a" stop-opacity=".18"/><stop offset="1" stop-color="#6fbf5a" stop-opacity="0"/></radialGradient></defs>')
o.append('<style>.disp{font-family:"Poiret One",sans-serif}</style>')
o.append(f'<rect width="{W}" height="1100" fill="{INK}"/>')
# time lines and era names (fixed left gutter)
o.append('<g id="gut">')
for p in PER:
    o.append(f'<line x1="160" x2="{W-90}" y1="{p["y0"]:.1f}" y2="{p["y0"]:.1f}" stroke="{GOLD}" stroke-opacity=".16" stroke-width=".6"/>')
    for k in range(1, 4):
        yy = p['y0'] - (p['y0'] - p['y1']) * k / 4
        o.append(f'<line x1="150" x2="{W-90}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="{GOLD}" stroke-opacity=".07" stroke-width=".4" stroke-dasharray="3 4"/>')
    name = 'NOW' if p['id'] == 'contemporary' else p['name'].upper()
    o.append(f'<text x="150" y="{(p["y0"]+p["y1"])/2:.1f}" fill="{GOLD}" font-size="11.5" text-anchor="end" letter-spacing="1.6" class="disp">{name}</text>')
    o.append(f'<text x="150" y="{(p["y0"]+p["y1"])/2+13:.1f}" fill="{IVORY}" fill-opacity=".45" font-size="9" text-anchor="end">{p["start"]}</text>')
o.append('</g>')
o.append(f'<line x1="150" x2="{W-90}" y1="{GROUND}" y2="{GROUND}" stroke="#6fbf5a" stroke-opacity=".5" stroke-width="1.2"/>')
o.append(f'<ellipse cx="{CX}" cy="{GROUND + 150}" rx="420" ry="140" fill="url(#glow)"/>')
# stems and bars
for f, name, c in FAMS:
    if f == 'commons': continue
    x0, w, fy = X[f], width(f), first[f]
    sx = x0 + w / 2
    o.append(f'<path d="M{sx-1.5},{GROUND} L{sx-1.5},{fy+60} Q{sx-1.5},{fy+28} {x0},{fy+14} L{x0},{PRESENT} L{x0+w},{PRESENT} L{x0+w},{fy+14} Q{sx+1.5},{fy+28} {sx+1.5},{fy+60} L{sx+1.5},{GROUND} Z" fill="url(#st-{f})"/>')
    o.append(f'<line x1="{sx}" x2="{sx}" y1="{GROUND}" y2="{fy+40}" stroke="{c}" stroke-opacity=".75" stroke-width="1.6"/>')      # the stem
    top = f'M{x0+w},{PRESENT}' if os.environ.get('CROWNS', 'fractal') == 'fractal' else f'L{x0+w},{PRESENT}'      # an integrated crown flows into the spire, so no seam across the top
    o.append(f'<path d="M{x0},{fy+14} L{x0},{PRESENT} {top} L{x0+w},{fy+14}" fill="none" stroke="{GOLD}" stroke-opacity=".45" stroke-width=".6"/>')
    for k in range(1, len(fam_cols[f])):
        o.append(f'<line x1="{x0+k*CW}" x2="{x0+k*CW}" y1="{fy+20}" y2="{PRESENT}" stroke="{GOLD}" stroke-opacity=".08" stroke-width=".4" stroke-dasharray="2 3"/>')
    fs = min(26, w * .5, (fy - PRESENT - 40) / (len(name) * .75))
    o.append(f'<text class="famname" transform="translate({x0+w/2+fs*.35:.1f},{fy-10:.1f}) rotate(-90)" fill="{c}" fill-opacity=".75" class="disp" font-size="{fs:.1f}" letter-spacing="3" font-weight="300">{name}</text>')

# ---- crowns: a sacred-geometry roundel in an ogee crown on top of every spire (one shared form, a different figure for each family)
import math
def crown(f, x0, w, c):
    sx, P = x0 + w / 2, PRESENT
    H = max(46, min(108, w * .58)); R = min(w * .25, H * .26, 24); cy = P - H * .38
    q = []
    # the ogee: rises straight, swells out, then draws in to a point (both sides mirrored)
    L = f'M{x0:.1f},{P} C{x0:.1f},{P-H*.42:.1f} {sx-w*.36:.1f},{P-H*.52:.1f} {sx-w*.2:.1f},{P-H*.64:.1f} C{sx-w*.08:.1f},{P-H*.73:.1f} {sx-1:.1f},{P-H*.82:.1f} {sx:.1f},{P-H:.1f}'
    Rt = f'C{sx+1:.1f},{P-H*.82:.1f} {sx+w*.08:.1f},{P-H*.73:.1f} {sx+w*.2:.1f},{P-H*.64:.1f} C{sx+w*.36:.1f},{P-H*.52:.1f} {x0+w:.1f},{P-H*.42:.1f} {x0+w:.1f},{P} Z'
    q.append(f'<path d="{L} {Rt}" fill="{c}" fill-opacity=".34" stroke="{GOLD}" stroke-opacity=".5" stroke-width=".6"/>')
    q.append(f'<path d="{L} {Rt}" fill="none" stroke="{c}" stroke-opacity=".5" stroke-width=".35" transform="translate({sx:.1f},{P}) scale(.86) translate({-sx:.1f},{-P})"/>')
    # the finial: a thin rod and a small four-point star
    ty = P - H - 9
    q.append(f'<line x1="{sx:.1f}" x2="{sx:.1f}" y1="{P-H:.1f}" y2="{ty+2.5:.1f}" stroke="{GOLD}" stroke-width=".6"/>')
    q.append(f'<path d="M{sx:.1f},{ty-3.2:.1f} L{sx+.9:.1f},{ty-.9:.1f} L{sx+3.2:.1f},{ty:.1f} L{sx+.9:.1f},{ty+.9:.1f} L{sx:.1f},{ty+3.2:.1f} L{sx-.9:.1f},{ty+.9:.1f} L{sx-3.2:.1f},{ty:.1f} L{sx-.9:.1f},{ty-.9:.1f} Z" fill="{GOLD_HI}"/>')
    # the roundel
    q.append(f'<circle cx="{sx:.1f}" cy="{cy:.1f}" r="{R+1.6:.2f}" fill="{INK}" fill-opacity=".55" stroke="{GOLD}" stroke-width=".7"/>')
    g = f'fill="none" stroke="{GOLD_HI}" stroke-opacity=".85" stroke-width=".45"'
    cg = f'fill="{c}" fill-opacity=".22" stroke="{c}" stroke-width=".55"'
    C = lambda x, y, r, a=g: f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" {a}/>'
    pt = lambda r, a: (sx + r * math.cos(a), cy + r * math.sin(a))
    poly = lambda pts, a=g: '<path d="M' + ' L'.join(f'{x:.2f},{y:.2f}' for x, y in pts) + f' Z" {a}/>'
    if f == 'keyboard':            # seed of life: seven circles, like the seven naturals of the octave
        r = R / 2; q.append(C(sx, cy, r, cg)); [q.append(C(*pt(r, k * math.pi / 3 - math.pi / 2), r)) for k in range(6)]; q.append(C(sx, cy, R))
    elif f == 'chamber':           # vesica piscis: two voices, one shared space
        r = R * .62; q.append(C(sx - r / 2, cy, r)); q.append(C(sx + r / 2, cy, r)); h = r * math.sqrt(3) / 2
        q.append(f'<path d="M{sx:.2f},{cy-h:.2f} A{r:.2f},{r:.2f} 0 0 1 {sx:.2f},{cy+h:.2f} A{r:.2f},{r:.2f} 0 0 1 {sx:.2f},{cy-h:.2f} Z" {cg}/>')
    elif f == 'concerto':          # the one and the many: a point within a triangle within the circle
        q.append(poly([pt(R * .92, k * 2 * math.pi / 3 - math.pi / 2) for k in range(3)])); q.append(poly([pt(R * .46, k * 2 * math.pi / 3 + math.pi / 2) for k in range(3)], cg)); q.append(C(sx, cy, R * .16, f'fill="{GOLD_HI}"'))
    elif f == 'sacred':            # rose window: twelve petals turning about one centre
        r = R * .5; [q.append(C(*pt(r, k * math.pi / 6), r)) for k in range(12)]; q.append(C(sx, cy, R * .2, cg)); q.append(C(sx, cy, R))
    elif f == 'song':              # the golden spiral: one breath, one line, unfolding
        phi = (1 + 5 ** .5) / 2; s0 = R * 1.18; x, y = sx - s0 / 2, cy - s0 / phi / 2; d = f'M{x:.2f},{y + s0/phi:.2f}'; a = s0 / phi
        dirs = [(1, -1), (1, 1), (-1, 1), (-1, -1)]; cx_, cy_ = x + a, y + a; px, py = x, y + a
        seq = []
        sz = a
        for k in range(7):
            dx, dy = dirs[k % 4]; nx, ny = px + dx * sz, py + dy * sz
            seq.append(f'A{sz:.2f},{sz:.2f} 0 0 1 {nx:.2f},{ny:.2f}'); px, py = nx, ny; sz /= phi
        q.append(f'<path d="M{x:.2f},{y + a:.2f} ' + ' '.join(seq) + f'" fill="none" stroke="{c}" stroke-width=".7"/>')
        q.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{s0:.2f}" height="{s0/phi:.2f}" {g}/>'); q.append(f'<line x1="{x+a:.2f}" x2="{x+a:.2f}" y1="{y:.2f}" y2="{y+a:.2f}" {g}/>'); q.append(C(sx, cy, R))
    elif f == 'stage':             # circle and square: the round audience about the square stage
        q.append(C(sx, cy, R)); s2 = R / math.sqrt(2); q.append(f'<rect x="{sx-s2:.2f}" y="{cy-s2:.2f}" width="{2*s2:.2f}" height="{2*s2:.2f}" {cg}/>'); q.append(C(sx, cy, s2)); q.append(f'<line x1="{sx-s2:.2f}" x2="{sx+s2:.2f}" y1="{cy+s2:.2f}" y2="{cy+s2:.2f}" stroke="{GOLD_HI}" stroke-width=".9"/>')
    elif f == 'orch':              # flower of life: many circles, one pattern
        r = R / 3
        for ring, n in [(0, 1), (r, 6), (r * math.sqrt(3), 6), (2 * r, 6)]:
            for k in range(n): a = k * math.pi / 3 + (math.pi / 6 if ring == r * math.sqrt(3) else 0) - math.pi / 2; q.append(C(*pt(ring, a), r, cg if ring == 0 else g))
        q.append(C(sx, cy, R))
    elif f == 'commons':           # three rings bound together: song, dance and work song
        r = R * .5
        for k in range(3): q.append(C(*pt(r * .62, k * 2 * math.pi / 3 - math.pi / 2), r, cg if k == 0 else g))
        q.append(C(sx, cy, R))
    return '<g class="crown">' + ''.join(q) + '</g>'

# ---- crown, integrated (draft for approval): the figure fills the dome and its lattice runs down into the spire, fading as it goes
def crown2(f, x0, w, c):
    sx, P = x0 + w / 2, PRESENT
    H = max(46, min(108, w * .58)); FADE = 210; R2 = min(w * .3, H * .4); cy = P - H * .4
    L = f'M{x0:.1f},{P} C{x0:.1f},{P-H*.42:.1f} {sx-w*.36:.1f},{P-H*.52:.1f} {sx-w*.2:.1f},{P-H*.64:.1f} C{sx-w*.08:.1f},{P-H*.73:.1f} {sx-1:.1f},{P-H*.82:.1f} {sx:.1f},{P-H:.1f}'
    Rt = f'C{sx+1:.1f},{P-H*.82:.1f} {sx+w*.08:.1f},{P-H*.73:.1f} {sx+w*.2:.1f},{P-H*.64:.1f} C{sx+w*.36:.1f},{P-H*.52:.1f} {x0+w:.1f},{P-H*.42:.1f} {x0+w:.1f},{P} Z'
    dome = f'{L} {Rt}'
    q = [f'<defs><clipPath id="cc-{f}"><path d="{dome}"/><path d="M{x0},{P-.5} C{x0},{P+FADE*.32:.1f} {sx-w*.12:.1f},{P+FADE*.74:.1f} {sx},{P+FADE} C{sx+w*.12:.1f},{P+FADE*.74:.1f} {x0+w},{P+FADE*.32:.1f} {x0+w},{P-.5} Z"/></clipPath>'
         f'<linearGradient id="cf-{f}" gradientUnits="userSpaceOnUse" x1="0" x2="0" y1="{P-H}" y2="{P+FADE}"><stop offset="0" stop-color="#fff"/><stop offset="{H/(H+FADE):.3f}" stop-color="#fff" stop-opacity=".9"/><stop offset="{(H+FADE*.45)/(H+FADE):.3f}" stop-color="#fff" stop-opacity=".32"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
         f'<mask id="cm-{f}" maskUnits="userSpaceOnUse" x="{x0-5}" y="{P-H-5}" width="{w+10}" height="{H+FADE+10}"><rect x="{x0-5}" y="{P-H-5}" width="{w+10}" height="{H+FADE+10}" fill="url(#cf-{f})"/></mask></defs>']
    q.append(f'<path d="{dome}" fill="{c}" fill-opacity=".34"/><path d="{dome[:-2]}" fill="none" stroke="{GOLD}" stroke-opacity=".5" stroke-width=".6"/>')
    ty = P - H - 9
    q.append(f'<line x1="{sx:.1f}" x2="{sx:.1f}" y1="{P-H:.1f}" y2="{ty+2.5:.1f}" stroke="{GOLD}" stroke-width=".6"/>')
    q.append(f'<path d="M{sx:.1f},{ty-3.2:.1f} L{sx+.9:.1f},{ty-.9:.1f} L{sx+3.2:.1f},{ty:.1f} L{sx+.9:.1f},{ty+.9:.1f} L{sx:.1f},{ty+3.2:.1f} L{sx-.9:.1f},{ty+.9:.1f} L{sx-3.2:.1f},{ty:.1f} L{sx-.9:.1f},{ty-.9:.1f} Z" fill="{GOLD_HI}"/>')
    g = []; r = R2 / 2
    hl = f'fill="none" stroke="{GOLD_HI}" stroke-width=".4"'
    # the lattice: the rose window's own circles, repeated on a triangular grid down the spire
    dy = r * math.sqrt(3) / 2; row = 0; y = cy + R2 * .95
    while y < P + FADE + r:
        off = (r / 2) if row % 2 else 0; x = sx - math.ceil((w / 2 + r) / r) * r + off
        while x < x0 + w + r:
            g.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" {hl} stroke-opacity=".42"/>'); x += r
        y += dy; row += 1
    # the rose itself: twelve petals, its outer rings, a glowing heart
    for k in range(12):
        a = k * math.pi / 6; g.append(f'<circle cx="{sx + r*math.cos(a):.2f}" cy="{cy + r*math.sin(a):.2f}" r="{r:.2f}" {hl} stroke-opacity=".9"/>')
    g.append(f'<circle cx="{sx:.2f}" cy="{cy:.2f}" r="{R2:.2f}" fill="none" stroke="{GOLD}" stroke-width=".8"/>')
    g.append(f'<circle cx="{sx:.2f}" cy="{cy:.2f}" r="{R2*1.12:.2f}" fill="none" stroke="{GOLD}" stroke-opacity=".6" stroke-width=".4"/>')
    g.append(f'<circle cx="{sx:.2f}" cy="{cy:.2f}" r="{R2*.18:.2f}" fill="{c}" fill-opacity=".5" stroke="{GOLD_HI}" stroke-width=".5"/>')
    # a soft column of the family's colour under the rose, so the dome pours into the spire
    g.append(f'<rect x="{x0}" y="{P-H}" width="{w}" height="{H+FADE}" fill="{c}" fill-opacity=".12"/>')
    g.append(f'<path d="M{x0},{P} C{x0},{P+FADE*.32:.1f} {sx-w*.12:.1f},{P+FADE*.74:.1f} {sx},{P+FADE} C{sx+w*.12:.1f},{P+FADE*.74:.1f} {x0+w},{P+FADE*.32:.1f} {x0+w},{P}" fill="none" stroke="{GOLD}" stroke-opacity=".55" stroke-width=".5"/>')
    q.append(f'<g clip-path="url(#cc-{f})" mask="url(#cm-{f})">' + ''.join(g) + '</g>')
    return '<g class="crown">' + ''.join(q) + '</g>'

# ---- crowns, fractal (14 Nov 20:45): the family's figure at the heart of the dome, smaller copies packed out to the dome's very edges,
#      and a short pendant of still smaller copies that fades into the spire within one storey
import numpy as np
def _circ(x, y, r): return f'M{x-r:.1f},{y:.1f}a{r:.1f},{r:.1f} 0 1,0 {2*r:.1f},0a{r:.1f},{r:.1f} 0 1,0 {-2*r:.1f},0'
def _poly(pts): return 'M' + 'L'.join(f'{x:.1f},{y:.1f}' for x, y in pts) + 'Z'
def figure(f, x, y, R):
    """the family's figure inside a circle of radius R, as path data: (gold lines, family-colour lines)"""
    g, c = [_circ(x, y, R)], []
    P = lambda r, a: (x + r * math.cos(a), y + r * math.sin(a))
    if R < 2.2: return g, c
    if f == 'keyboard':
        r = R / 2; c.append(_circ(x, y, r)); g += [_circ(*P(r, k * math.pi / 3 - math.pi / 2), r) for k in range(6)]
    elif f == 'chamber':
        r = R * .62; g += [_circ(x - r / 2, y, r), _circ(x + r / 2, y, r)]; h = r * math.sqrt(3) / 2
        c.append(f'M{x:.1f},{y-h:.1f}A{r:.1f},{r:.1f} 0 0 1 {x:.1f},{y+h:.1f}A{r:.1f},{r:.1f} 0 0 1 {x:.1f},{y-h:.1f}Z')
    elif f == 'concerto':
        g.append(_poly([P(R * .92, k * 2 * math.pi / 3 - math.pi / 2) for k in range(3)])); c.append(_poly([P(R * .46, k * 2 * math.pi / 3 + math.pi / 2) for k in range(3)])); c.append(_circ(x, y, R * .14))
    elif f == 'sacred':
        r = R / 2; g += [_circ(*P(r, k * math.pi / 6), r) for k in range(12 if R > 5 else 6)]; c.append(_circ(x, y, R * .18))
    elif f == 'song':
        phi = (1 + 5 ** .5) / 2; s0 = R * 1.3; x0, y0 = x - s0 / 2, y - s0 / phi / 2; a = s0 / phi
        g.append(_poly([(x0, y0), (x0 + s0, y0), (x0 + s0, y0 + a), (x0, y0 + a)])); g.append(f'M{x0+a:.1f},{y0:.1f}V{y0+a:.1f}')
        d = f'M{x0:.1f},{y0+a:.1f}'; px, py, sz = x0, y0 + a, a
        for k in range(7 if R > 5 else 3):
            dx, dy = [(1, -1), (1, 1), (-1, 1), (-1, -1)][k % 4]; px, py = px + dx * sz, py + dy * sz; d += f'A{sz:.1f},{sz:.1f} 0 0 1 {px:.1f},{py:.1f}'; sz /= phi
        c.append(d)
    elif f == 'stage':
        s2 = R / math.sqrt(2); c.append(_poly([(x - s2, y - s2), (x + s2, y - s2), (x + s2, y + s2), (x - s2, y + s2)])); g.append(_circ(x, y, s2))
    elif f == 'orch':
        r = R / 3; c.append(_circ(x, y, r))
        rings = [(r, 6, 0), (r * math.sqrt(3), 6, math.pi / 6), (2 * r, 6, 0)] if R > 6 else [(r, 6, 0)]
        for rr, n, o in rings: g += [_circ(*P(rr, k * math.pi / 3 + o - math.pi / 2), r) for k in range(n)]
    elif f == 'commons':
        r = R * .5; c.append(_circ(*P(r * .62, -math.pi / 2), r)); g += [_circ(*P(r * .62, k * 2 * math.pi / 3 - math.pi / 2), r) for k in (1, 2)]
    return g, c
def _bez(p0, p1, p2, p3, n=24): return [((1-t)**3*p0[0]+3*(1-t)**2*t*p1[0]+3*(1-t)*t*t*p2[0]+t**3*p3[0], (1-t)**3*p0[1]+3*(1-t)**2*t*p1[1]+3*(1-t)*t*t*p2[1]+t**3*p3[1]) for t in [i/n for i in range(n+1)]]
def crown3(f, x0, w, c):
    sx, P = x0 + w / 2, PRESENT
    H = max(46, min(108, w * .58)); FADE = 44; R2 = min(w * .3, H * .4); cy = P - H * .4
    a = [(x0, P), (x0, P-H*.42), (sx-w*.36, P-H*.52), (sx-w*.2, P-H*.64)], [(sx-w*.2, P-H*.64), (sx-w*.08, P-H*.73), (sx-1, P-H*.82), (sx, P-H)]
    L = f'M{x0:.1f},{P} C{x0:.1f},{P-H*.42:.1f} {sx-w*.36:.1f},{P-H*.52:.1f} {sx-w*.2:.1f},{P-H*.64:.1f} C{sx-w*.08:.1f},{P-H*.73:.1f} {sx-1:.1f},{P-H*.82:.1f} {sx:.1f},{P-H:.1f}'
    Rt = f'C{sx+1:.1f},{P-H*.82:.1f} {sx+w*.08:.1f},{P-H*.73:.1f} {sx+w*.2:.1f},{P-H*.64:.1f} C{sx+w*.36:.1f},{P-H*.52:.1f} {x0+w:.1f},{P-H*.42:.1f} {x0+w:.1f},{P}'
    dome = f'{L} {Rt} Z'
    # the dome as a polygon, to pack circles inside it
    left = _bez(*a[0]) + _bez(*a[1])[1:]; poly = left + [(2 * sx - x, y) for x, y in reversed(left)][1:]
    E = np.array(poly); A, B = E, np.roll(E, -1, axis=0)
    gx, gy = np.meshgrid(np.arange(x0 + .3, x0 + w, .45), np.arange(P - H + .3, P, .45)); pts = np.stack([gx.ravel(), gy.ravel()], 1)
    # inside test and distance to the border
    inside = np.zeros(len(pts), bool); dist = np.full(len(pts), 1e9)
    for (ax, ay), (bx, by) in zip(A, B):
        if (ay > pts[:, 1]).any() or True:
            cond = ((ay > pts[:, 1]) != (by > pts[:, 1])) & (pts[:, 0] < (bx - ax) * (pts[:, 1] - ay) / ((by - ay) or 1e-9) + ax); inside ^= cond
        vx, vy = bx - ax, by - ay; t = np.clip(((pts[:, 0] - ax) * vx + (pts[:, 1] - ay) * vy) / (vx * vx + vy * vy or 1), 0, 1)
        dist = np.minimum(dist, np.hypot(pts[:, 0] - (ax + t * vx), pts[:, 1] - (ay + t * vy)))
    pts, clear = pts[inside], dist[inside] - .5
    circles = [(sx, cy, R2)]
    clear = np.minimum(clear, np.hypot(pts[:, 0] - sx, pts[:, 1] - cy) - R2 - .6)
    while len(circles) < 160:
        i = int(np.argmax(clear)); r = clear[i]
        if r < 1.1: break
        r = min(r, R2 * .62); x, y = pts[i]; circles.append((x, y, r))
        clear = np.minimum(clear, np.hypot(pts[:, 0] - x, pts[:, 1] - y) - r - .45)
    # the pendant: rows of smaller copies, narrowing as they fall, gone within one storey
    pend = []; y = P + 1.2; r = max(1.2, R2 * .13); k = 0
    while y < P + FADE and r > .8:
        n = int(w // (2 * r * 1.04)) + 2; off = r * 1.04 if k % 2 else 0
        for j in range(-n // 2 - 1, n // 2 + 2): pend.append((sx + j * 2 * r * 1.04 + off, y + r, r))
        y += 2 * r * .93; r *= .88; k += 1
    buckets = {}
    def put(lst, tag):
        for (x, y, r) in lst:
            gg, cc = figure(f, x, y, r); sw = .5 if r >= 10 else .32 if r >= 4 else .2
            buckets.setdefault((tag, 'g', sw), []).extend(gg); buckets.setdefault((tag, 'c', sw), []).extend(cc)
    put(circles, 'd'); put(pend, 'p')
    q = [f'<defs><clipPath id="cc-{f}"><path d="{dome}"/></clipPath>'
         f'<linearGradient id="cf-{f}" gradientUnits="userSpaceOnUse" x1="0" x2="0" y1="{P}" y2="{P+FADE}"><stop offset="0" stop-color="#fff" stop-opacity=".6"/><stop offset=".5" stop-color="#fff" stop-opacity=".2"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
         f'<clipPath id="cp-{f}"><path d="M{x0},{P} C{x0},{P+FADE*.32:.1f} {sx-w*.12:.1f},{P+FADE*.74:.1f} {sx},{P+FADE} C{sx+w*.12:.1f},{P+FADE*.74:.1f} {x0+w},{P+FADE*.32:.1f} {x0+w},{P} Z"/></clipPath><mask id="cm-{f}" maskUnits="userSpaceOnUse" x="{x0-5}" y="{P}" width="{w+10}" height="{FADE+5}"><rect x="{x0-5}" y="{P}" width="{w+10}" height="{FADE+5}" fill="url(#cf-{f})"/></mask></defs>']
    q.append(f'<path d="{dome}" fill="{c}" fill-opacity=".34"/>')
    dom = [f'<path d="{"".join(v)}" fill="none" stroke="{GOLD_HI if k[1] == "g" else c}" stroke-opacity="{.85 if k[1] == "g" else 1}" stroke-width="{k[2]}"/>' for k, v in buckets.items() if k[0] == 'd' and v]
    q.append(f'<g clip-path="url(#cc-{f})">' + ''.join(dom) + f'<circle cx="{sx:.1f}" cy="{cy:.1f}" r="{R2:.1f}" fill="none" stroke="{GOLD}" stroke-width=".8"/>' + (f'<circle cx="{sx:.1f}" cy="{cy:.1f}" r="{R2*.16:.1f}" fill="{c}" fill-opacity=".45"/>' if f in ('sacred', 'keyboard', 'orch') else '') + '</g>')
    pen = [f'<path d="{"".join(v)}" fill="none" stroke="{GOLD_HI if k[1] == "g" else c}" stroke-opacity="{.8 if k[1] == "g" else 1}" stroke-width="{k[2]}"/>' for k, v in buckets.items() if k[0] == 'p' and v]
    q.append(f'<g mask="url(#cm-{f})"><g clip-path="url(#cp-{f})">' + ''.join(pen) + '</g></g>')
    q.append(f'<path d="{L} {Rt}" fill="none" stroke="{GOLD}" stroke-opacity=".55" stroke-width=".6"/>')
    ty = P - H - 9
    q.append(f'<line x1="{sx:.1f}" x2="{sx:.1f}" y1="{P-H:.1f}" y2="{ty+2.5:.1f}" stroke="{GOLD}" stroke-width=".6"/>')
    q.append(f'<path d="M{sx:.1f},{ty-3.2:.1f} L{sx+.9:.1f},{ty-.9:.1f} L{sx+3.2:.1f},{ty:.1f} L{sx+.9:.1f},{ty+.9:.1f} L{sx:.1f},{ty+3.2:.1f} L{sx-.9:.1f},{ty+.9:.1f} L{sx-3.2:.1f},{ty:.1f} L{sx-.9:.1f},{ty-.9:.1f} Z" fill="{GOLD_HI}"/>')
    return '<g class="crown">' + ''.join(q) + '</g>'
CROWN_STYLE = os.environ.get('CROWNS', 'fractal')
for f, name, c in FAMS:
    if f != 'commons': o.append((crown3 if CROWN_STYLE == 'fractal' else crown)(f, X[f], width(f), c))
# the spire and the pyramid
sx = CX
o.append(f'<path d="M{sx-SPW/2+6},{PRESENT} L{sx+SPW/2-6},{PRESENT} L{sx+SPW/2+4},{GROUND} L{sx-SPW/2-4},{GROUND} Z" fill="#6fbf5a" fill-opacity=".22" stroke="#6fbf5a" stroke-opacity=".5" stroke-width=".8"/>')
o.append((crown3 if CROWN_STYLE == 'fractal' else crown)('commons', sx - SPW / 2 + 6, SPW - 12, '#6fbf5a'))
o.append(f'<text class="famname" transform="translate({sx+5},{(GROUND+PRESENT)/2}) rotate(-90)" fill="{GREEN}" fill-opacity=".7" class="disp" font-size="20" letter-spacing="3" text-anchor="middle" font-weight="300">THE COMMONS</text>')
MW, MD = 520, 168          # the mound, inverted: wide at the ground, narrowing to one seed point, the origin
SEED = (sx, GROUND + MD)
# the commons as grass: blades spring from the seed; the eight longest reach the foot of every spire and run on into its stem
import random as _rnd, math as _m
def _cub(P0, P1, P2, P3, t):
    u = 1 - t; return (u*u*u*P0[0] + 3*u*u*t*P1[0] + 3*u*t*t*P2[0] + t*t*t*P3[0], u*u*u*P0[1] + 3*u*u*t*P1[1] + 3*u*t*t*P2[1] + t*t*t*P3[1])
def blade(P0, P1, P2, P3, w0, wt, n=48):      # a broad blade along a cubic centre line: rounded at the seed, full above it, then easing to the stem's own width at the tip
    L, R, mid = [], [], []
    for k in range(n + 1):
        t = k / n; x, y = _cub(P0, P1, P2, P3, t); x2, y2 = _cub(P0, P1, P2, P3, min(1, t + .01)); x1, y1 = _cub(P0, P1, P2, P3, max(0, t - .01))
        dx, dy = x2 - x1, y2 - y1; d = _m.hypot(dx, dy) or 1; nx, ny = -dy / d, dx / d
        w = (min(1, t / .07) ** .5) * (wt + (w0 - wt) * (1 - t) ** 1.3)
        L.append((x + nx * w, y + ny * w)); R.append((x - nx * w, y - ny * w)); mid.append((x, y))
    f = lambda P: ' L'.join(f'{a:.1f},{b:.1f}' for a, b in P)
    return 'M' + f(L + R[::-1]) + 'Z', 'M' + f(mid[4:])
gdefs = []
for f2, _, c2 in FAMS:      # each blade darkens to the seed and, at its tip, takes on its spire's stem exactly (colour and strength)
    top = .22 if f2 == 'commons' else .75
    gdefs.append(f'<linearGradient id="gb-{f2}" gradientUnits="userSpaceOnUse" x1="0" x2="0" y1="{SEED[1]}" y2="{GROUND}"><stop offset="0" stop-color="#2c4a22" stop-opacity=".95"/><stop offset=".45" stop-color="#4f8a3a" stop-opacity=".9"/><stop offset=".85" stop-color="{c2}" stop-opacity="{(top + .9) / 2:.2f}"/><stop offset="1" stop-color="{c2}" stop-opacity="{top}"/></linearGradient>')
o.append('<defs>' + ''.join(gdefs) + '</defs>')
g = ['<g class="grass" pointer-events="none">']
for f2, _, c2 in FAMS:      # one blade for every spire: from the seed to the foot of its stem, and on into it
    fx = X[f2] + (SPW if f2 == 'commons' else width(f2)) / 2
    P1 = (SEED[0] + (fx - SEED[0]) * .15, GROUND + MD * .45); P2 = (fx, GROUND + 40); P3 = (fx, GROUND)
    wt = 1.5                                                    # the stem's foot is 3 wide
    if f2 == 'commons': P1, P2, wt = (SEED[0], SEED[1] - 60), (SEED[0], GROUND + 40), SPW / 2 + 4      # the central blade opens into the commons spire's foot
    body, rib = blade(SEED, P1, P2, P3, 7.5 if f2 != 'commons' else 6, wt)
    g.append(f'<path class="root" d="{body}" fill="url(#gb-{f2})"/><path d="{rib}" fill="none" stroke="#b9e08f" stroke-opacity=".22" stroke-width=".7" stroke-linecap="round"/>')
g.append('</g>'); o.append(''.join(g))
o.append(f'<circle cx="{SEED[0]}" cy="{SEED[1]}" r="3.2" fill="{GOLD_HI}"/><circle cx="{SEED[0]}" cy="{SEED[1]}" r="7" fill="none" stroke="{GOLD_HI}" stroke-opacity=".45" stroke-width=".6"/>')
o.append(f'<g class="fm soil" data-id="commons"><circle class="seedring" cx="{SEED[0]}" cy="{SEED[1]}" r="7" fill="none"/><circle class="hit" cx="{SEED[0]}" cy="{SEED[1]}" r="14" fill="transparent"/>')      # only the seed answers the pointer, not the whole mound
o.append(f'<text class="famname moundname disp" x="{sx}" y="{GROUND+34}" stroke="#0b0906" stroke-width="5" stroke-opacity=".85" paint-order="stroke" fill="{GOLD_HI}" font-size="24" text-anchor="middle" letter-spacing="4">THE COMMONS</text>')
o.append(f'<text class="famname moundname" x="{sx}" y="{GROUND+52}" stroke="#0b0906" stroke-width="4" stroke-opacity=".85" paint-order="stroke" fill="{IVORY}" fill-opacity=".75" font-size="10" text-anchor="middle" letter-spacing="2">FOLK SONG · DANCE · WORK SONG</text>')
o.append(f'<text class="famname moundname" x="{sx}" y="{GROUND+66}" stroke="#0b0906" stroke-width="4" stroke-opacity=".85" paint-order="stroke" fill="{IVORY}" fill-opacity=".6" font-size="9" font-style="italic" text-anchor="middle" letter-spacing=".6">the ground all music springs from</text></g>')
# hairlines: straight, faint at rest; the focus web bright
for a, b, t in D['links']:
    if a not in POS or b not in POS: continue
    on = FOCUS in (a, b)
    (x1, y1), (x2, y2) = POS[a], POS[b]
    if 'commons' in (a, b):
        tx, ty = POS[b if a == 'commons' else a]; x1, y1, x2, y2 = sx + (SPW / 2 if tx > sx else -SPW / 2), ty + 18, tx, ty
    col = RED if t == 'r' else (GREEN if 'commons' in (a, b) else (GOLD_HI if on else GOLD))
    dash = (' stroke-dasharray="0.6 2.4"' if on else ' stroke-dasharray="1.2 2.2"') if t == 'i' else (' stroke-dasharray="4 3"' if t == 'r' else '')
    dx, dy = x2 - x1, y2 - y1; L = math.hypot(dx, dy) or 1; bow = min(14, L * .12) * (1 if dx >= 0 else -1)
    qx, qy = (x1 + x2) / 2 - dy / L * bow, (y1 + y2) / 2 + dx / L * bow          # a slight whiplash: the line swells to one side
    kind = 'c' if 'commons' in (a, b) else t
    o.append(f'<path class="lk {kind}" data-a="{a}" data-b="{b}" d="M{x1:.1f},{y1:.1f} Q{qx:.1f},{qy:.1f} {x2:.1f},{y2:.1f}" fill="none" stroke="{col}" stroke-opacity="{.95 if on else .16}" stroke-width="{(.55 if t == 'i' else .75) if on else .35}" stroke-linecap="round"{dash}/>')
# forms: a point and a two-line uppercase name; dim at rest, bright in the web
for i, (L, r) in LAB.items():
    on = i in web; x0, y0 = POS[i]; c = FC.get(HOME.get(i, 'song'), '#ccc')
    o.append(f'<g class="fm" data-id="{i}"><rect class="hit" x="{min(r[0], x0 - 2):.1f}" y="{min(r[1], y0 - 2):.1f}" width="{max(r[2], x0 + 2) - min(r[0], x0 - 2):.1f}" height="{max(r[3], y0 + 2) - min(r[1], y0 - 2):.1f}" fill="transparent"/>')
    o.append(f'<circle cx="{x0:.1f}" cy="{y0:.1f}" r="{1.1 if on else .7}" fill="{GOLD_HI if on else GOLD}" fill-opacity="{1 if on else .7}"/>')
    op = 1 if on else .5; fw = ' font-weight="700"' if i == FOCUS else ''
    fill = GOLD_HI if i == FOCUS else (IVORY if on else IVORY)
    cx = (r[0] + r[2]) / 2
    yy = r[1]
    for ln in L:
        sm = small(ln); f = FS * (SMALL if sm else 1); yy += f * .86
        o.append(f'<text x="{cx:.1f}" y="{yy:.1f}" fill="{fill}" fill-opacity="{op * (.8 if sm else 1):.2f}" font-size="{f:.2f}" text-anchor="middle" letter-spacing="{.1 if sm else .25}"{fw}{" font-style=\"italic\"" if sm else ""}>{html.escape(ln)}</text>')
        yy += lh(ln) - f * .86
    o.append('</g>')
# fixed chrome (illustrative): left bar, controls
o.append('<g id="chrome">')
o.append('<rect x="0" y="0" width="56" height="1100" fill="#141418"/>')
for k, s in enumerate(['⌕', '≡', 'A–Z', '◎', '⚑']):
    o.append(f'<text x="28" y="{80+k*62}" fill="#cfcfd6" font-size="{16 if len(s)==1 else 12}" text-anchor="middle">{s}</text>')
o.append(f'<circle cx="{W-44}" cy="960" r="17" fill="#e8e6e0"/><text x="{W-44}" y="966" font-size="20" text-anchor="middle" fill="#111">+</text>')
o.append(f'<circle cx="{W-44}" cy="1004" r="17" fill="#e8e6e0"/><text x="{W-44}" y="1010" font-size="20" text-anchor="middle" fill="#111">−</text>')
o.append(f'<text x="80" y="40" fill="#e8e6e0" font-size="17" letter-spacing="4">THE GARDEN OF EARTHLY SOUNDS</text>')
o.append('</g>')
o.append('</svg>')
svg = '\n'.join(o)
os.makedirs(OUT, exist_ok=True)
if LIVE:
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, 'map.svg'), 'w').write(svg)
    json.dump({'nodes': {i: {'x': round(POS[i][0], 2), 'y': round(POS[i][1], 2), 'f': HOME.get(i) or N[i].get('lane') or 'song'} for i in POS},
               'fams': {f: {'x0': X[f], 'x1': X[f] + (SPW if f == 'commons' else width(f)), 'open': first[f], 'name': nm, 'c': c} for f, nm, c in FAMS},
               'eras': [{'id': p['id'], 'name': 'Now' if p['id'] == 'contemporary' else p['name'], 'start': p['start'], 'end': p['end'], 'top': p['y1'], 'bottom': p['y0']} for p in PER],
               'mins': {c['gid']: {'x0': X[f] + (0 if f == 'commons' else k * CW), 'x1': X[f] + (SPW if f == 'commons' else (k + 1) * CW), 'f': f, 't': c['t']} for f in X for k, c in enumerate(fam_cols[f]) if c.get('gid')},
               'present': PRESENT, 'ground': GROUND, 'bounds': [150, PRESENT - 150, W - 60, GROUND + 188]}, open(os.path.join(OUT, 'layout.json'), 'w'))
    print('live map written')
open(os.path.join(OUT, 'preview.svg'), 'w').write(svg)
print('forms placed', len(LAB), 'focus', N[FOCUS]['t'] if FOCUS else '-', len(web) - 1, 'links')
json.dump({'X': X, 'W': {f: (SPW if f == 'commons' else width(f)) for f in X}, 'first': first, 'per': [{'id': p['id'], 'name': p['name'], 'start': p['start'], 'y0': p['y0'], 'y1': p['y1']} for p in PER], 'present': PRESENT, 'ground': GROUND}, open(os.path.join(OUT, 'preview_layout.json'), 'w'))
