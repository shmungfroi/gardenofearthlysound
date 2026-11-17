import asyncio, subprocess, time, json, sys
from playwright.async_api import async_playwright
PORT = sys.argv[1] if len(sys.argv) > 1 else '8926'; TAG = sys.argv[2] if len(sys.argv) > 2 else 'before'
srv = subprocess.Popen(['python3','/home/claude/tools/serve.py',PORT,'/home/claude/gardenofearthlysound'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
AUDIT = r"""async () => {
  const P = document.getElementById('panel'), R = e => e.getBoundingClientRect(), bad = [], seen = {cards: 0, terms: 0, els: 0};
  const vis = e => { const r = R(e); return r.height > 0 && r.width > 0; };
  function check(box, anchor, where, what) {
    const flow = e => { let x = e; while (x && (!vis(x) || ['absolute','fixed'].includes(getComputedStyle(x).position))) x = x.nextElementSibling; return x; }, b = R(box), a = anchor ? R(anchor) : null, nx = flow(box.nextElementSibling), n = nx ? R(nx) : null, p = R(P), cs = getComputedStyle(P);
    const inL = p.left + parseFloat(cs.paddingLeft) - 2, inR = p.right - parseFloat(cs.paddingRight) + 2, why = [];
    if (!vis(box)) why.push('not visible');
    if (a && b.top < a.bottom - 1) why.push(`covers the text above by ${Math.round(a.bottom - b.top)}px`);
    if (n && n.top < b.bottom - 1) why.push(`covers the text below by ${Math.round(b.bottom - n.top)}px`);
    if (b.left < inL || b.right > inR) why.push(`spills outside the card (${Math.round(b.left - inL)} / ${Math.round(inR - b.right)}px)`);
    const ps = getComputedStyle(box); if (ps.position === 'fixed' || ps.position === 'absolute') why.push('position ' + ps.position);
    if (why.length) bad.push({where, what, why: why.join('; ')}); }
  const cards = [];
  __map.LAY && Object.keys(__map.LAY.nodes).forEach(id => cards.push(['lantern', id]));
  (window.GardenCard && Object.keys(window.GardenCard.VOICES || {}) || []).forEach(k => cards.push(['composer', k]));
  (window.GardenCard && Object.keys(window.GardenCard.EVENTS || {}) || []).forEach(k => cards.push(['event', k]));
  for (const [kind, id] of cards) {
    try { if (kind === 'lantern') __map.choose(id, false); else if (kind === 'composer') __map.showThread(id); else __map.showEvent(id); } catch (e) { bad.push({where: kind + ' ' + id, what: 'open', why: String(e)}); continue; }
    seen.cards++;
    const kws = [...P.querySelectorAll('button.kw')];
    for (const k of kws) { if (!k.isConnected) continue; k.click(); seen.terms++; const d = P.querySelector('.gdef'); if (!d) { bad.push({where: kind + ' ' + id, what: k.textContent, why: 'no box opened'}); continue; }
      check(d, d.previousElementSibling, kind + ' ' + id, '“' + k.textContent + '”'); k.click(); }
    const ebs = [...P.querySelectorAll('.els > button')];
    for (const b of ebs) { b.click(); seen.els++; const ec = P.querySelector('.ecard'); if (ec) { const slot = ec.parentElement; check(slot, slot.previousElementSibling, kind + ' ' + id, 'element ' + b.textContent);
        for (const k of [...ec.querySelectorAll('button.kw')]) { k.click(); seen.terms++; const d = P.querySelector('.gdef'); if (d) check(d, d.previousElementSibling, kind + ' ' + id, 'element ' + b.textContent + ' › “' + k.textContent + '”'); k.click(); } }
      b.click(); }
  }
  return {seen, bad};
}"""
async def run(b, vp, label, mobile=False):
    ctx = await b.new_context(viewport=vp, is_mobile=mobile, has_touch=mobile, device_scale_factor=1)
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto(f'http://localhost:{PORT}/index.html'); await pg.wait_for_timeout(1500)
    res = await pg.evaluate(AUDIT)
    print(label, json.dumps(res['seen']), 'problems:', len(res['bad']), 'page errors:', len(errs))
    kinds = {}
    for x in res['bad']: kinds.setdefault(x['why'].split(' by ')[0].split(' (')[0], []).append(x)
    for k, v in kinds.items(): print('   ', len(v), '×', k, '· e.g.', v[0]['where'], v[0]['what'], '|', v[0]['why'])
    json.dump(res['bad'], open(f'/home/claude/shots/gloss/{TAG}_{label}.json', 'w'), ensure_ascii=False, indent=0)
    # one picture of basso continuo on the Monody card
    await pg.evaluate("__map.choose('monody', true)"); await pg.wait_for_timeout(900)
    ok = await pg.evaluate("(()=>{const k=[...document.querySelectorAll('#panel button.kw')].find(k=>/basso continuo/i.test(k.textContent)&&k.offsetParent);if(!k)return false;k.click();const d=document.querySelector('#panel .gdef');d.scrollIntoView({block:'center'});return true})()")
    await pg.wait_for_timeout(300)
    if ok: await pg.screenshot(path=f'/home/claude/shots/gloss/{TAG}_{label}_basso.png')
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        await run(b, {'width': 1600, 'height': 1000}, 'desktop')
        await run(b, {'width': 390, 'height': 844}, 'phone', True)
        await b.close()
try: asyncio.run(main())
finally: srv.kill()
