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
        if g['great'] == f: COLS.append({'fam': f, 'ids': [i for i in g['l'] if i != 'commons' and i in N]})
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
    o.append(f'<path d="M{x0},{fy+14} L{x0},{PRESENT} L{x0+w},{PRESENT} L{x0+w},{fy+14}" fill="none" stroke="{GOLD}" stroke-opacity=".45" stroke-width=".6"/>')
    for k in range(1, len(fam_cols[f])):
        o.append(f'<line x1="{x0+k*CW}" x2="{x0+k*CW}" y1="{fy+20}" y2="{PRESENT}" stroke="{GOLD}" stroke-opacity=".08" stroke-width=".4" stroke-dasharray="2 3"/>')
    fs = min(26, w * .5, (fy - PRESENT - 40) / (len(name) * .75))
    o.append(f'<text class="famname" transform="translate({x0+w/2+fs*.35:.1f},{fy-10:.1f}) rotate(-90)" fill="{c}" fill-opacity=".75" class="disp" font-size="{fs:.1f}" letter-spacing="3" font-weight="300">{name}</text>')
# the spire and the pyramid
sx = CX
o.append(f'<path d="M{sx-SPW/2+6},{PRESENT} L{sx+SPW/2-6},{PRESENT} L{sx+SPW/2+4},{GROUND} L{sx-SPW/2-4},{GROUND} Z" fill="#6fbf5a" fill-opacity=".22" stroke="#6fbf5a" stroke-opacity=".5" stroke-width=".8"/>')
o.append(f'<text class="famname" transform="translate({sx+5},{(GROUND+PRESENT)/2}) rotate(-90)" fill="{GREEN}" fill-opacity=".7" class="disp" font-size="20" letter-spacing="3" text-anchor="middle" font-weight="300">THE COMMONS</text>')
MW, MD = 520, 168          # the mound, inverted: wide at the ground, narrowing to one seed point, the origin
SEED = (sx, GROUND + MD)
mound = f'M{sx-MW},{GROUND} L{sx+MW},{GROUND} L{SEED[0]},{SEED[1]} Z'
o.append(f'<path d="{mound}" fill="url(#py)" stroke="#6fbf5a" stroke-opacity=".6" stroke-width=".8"/>')
for f2, _, c2 in FAMS:             # roots: from the seed, one to the foot of every spire
    if f2 == 'commons': continue
    fx = X[f2] + width(f2) / 2; my = GROUND + MD * .45
    o.append(f'<path class="root" d="M{SEED[0]},{SEED[1]} C{SEED[0] + (fx - SEED[0]) * .15},{my} {fx},{GROUND + 40} {fx},{GROUND}" fill="none" stroke="{c2}" stroke-opacity=".55" stroke-width=".9" stroke-linecap="round"/>')
o.append(f'<path d="M{sx},{SEED[1]} L{sx},{GROUND}" stroke="#6fbf5a" stroke-opacity=".8" stroke-width="1.6"/>')      # the central root, up into the spire
o.append(f'<circle cx="{SEED[0]}" cy="{SEED[1]}" r="3.2" fill="{GOLD_HI}"/><circle cx="{SEED[0]}" cy="{SEED[1]}" r="7" fill="none" stroke="{GOLD_HI}" stroke-opacity=".45" stroke-width=".6"/>')
o.append(f'<g class="fm soil" data-id="commons"><path class="hit" d="{mound}" fill="transparent"/><circle class="hit" cx="{SEED[0]}" cy="{SEED[1]}" r="9" fill="transparent"/>')
o.append(f'<text class="famname moundname disp" x="{sx}" y="{GROUND+34}" fill="{GOLD_HI}" font-size="24" text-anchor="middle" letter-spacing="4">THE COMMONS</text>')
o.append(f'<text class="famname moundname" x="{sx}" y="{GROUND+52}" fill="{IVORY}" fill-opacity=".75" font-size="10" text-anchor="middle" letter-spacing="2">FOLK SONG · DANCE · WORK SONG</text>')
o.append(f'<text class="famname moundname" x="{sx}" y="{GROUND+66}" fill="{IVORY}" fill-opacity=".6" font-size="9" font-style="italic" text-anchor="middle" letter-spacing=".6">the ground all music springs from</text></g>')
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
               'present': PRESENT, 'ground': GROUND, 'bounds': [150, 40, W - 60, GROUND + 188]}, open(os.path.join(OUT, 'layout.json'), 'w'))
    print('live map written')
open(os.path.join(OUT, 'preview.svg'), 'w').write(svg)
print('forms placed', len(LAB), 'focus', N[FOCUS]['t'] if FOCUS else '-', len(web) - 1, 'links')
json.dump({'X': X, 'W': {f: (SPW if f == 'commons' else width(f)) for f in X}, 'first': first, 'per': [{'id': p['id'], 'name': p['name'], 'start': p['start'], 'y0': p['y0'], 'y1': p['y1']} for p in PER], 'present': PRESENT, 'ground': GROUND}, open(os.path.join(OUT, 'preview_layout.json'), 'w'))
