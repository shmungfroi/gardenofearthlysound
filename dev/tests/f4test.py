import asyncio, subprocess, time
from playwright.async_api import async_playwright
srv = subprocess.Popen(['python3','/home/claude/tools/serve.py','8895','/home/claude/gardenofearthlysound'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
O='/home/claude/shots/f4'
ST="JSON.stringify({lvl:__map.level(), ev:__map.ekey(), crumbs:[...document.querySelectorAll('#crumbs button')].map(b=>b.textContent).join(' > '), panel:document.body.classList.contains('pan'), on:document.querySelectorAll('#map .fm.on').length, links:document.querySelectorAll('#evlayer .ev-link').length, h1:(document.querySelector('#panel h1')||{}).textContent||''})"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg = await b.new_page(viewport={'width':1600,'height':1000}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type=='error' and errs.append(m.text))
        await pg.goto('http://localhost:8895/index.html'); await pg.wait_for_timeout(1200)
        async def st(label, shot=None):
            await pg.wait_for_timeout(1000); print(label.ljust(24), await pg.evaluate(ST))
            if shot: await pg.screenshot(path=f'{O}/{shot}.png')
        vis = await pg.evaluate("[...document.querySelectorAll('#evs .evd')].filter(b=>b.style.display!=='none').length"); print('event marks visible at Garden:', vis)
        # overlapping marks?
        ov = await pg.evaluate("(()=>{const r=[...document.querySelectorAll('#evs .evd')].filter(b=>b.style.display!=='none').map(b=>{const q=b.getBoundingClientRect();return [q.left+q.width/2,q.top+q.height/2]});let n=0;for(let i=0;i<r.length;i++)for(let j=i+1;j<r.length;j++){if(Math.hypot(r[i][0]-r[j][0],r[i][1]-r[j][1])<9)n++}return n})()"); print('overlapping marks:', ov)
        # time marker on hover over the map
        await pg.mouse.move(900, 420); await pg.wait_for_timeout(300); print('time marker:', await pg.evaluate("document.getElementById('tmark').textContent"))
        await pg.screenshot(path=f'{O}/1_timemarker.png')
        # hover then click an event mark (Petrucci)
        h = await pg.evaluate("(()=>{const b=[...document.querySelectorAll('#evs .evd')].find(x=>x.title.startsWith('Petrucci'));const r=b.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()")
        await pg.mouse.move(*h); await pg.wait_for_timeout(300); print('hover label:', await pg.evaluate("document.getElementById('tmark').textContent"))
        await pg.mouse.click(*h); await pg.wait_for_timeout(300); await pg.mouse.click(*h); await st('click Petrucci (pin, open)', '2_petrucci')
        await pg.click('#panel .evto .lk-b >> nth=0'); await st('event > lantern')
        # an event from a lantern's Connections
        await pg.click('#q'); await pg.keyboard.type('opera', delay=25); await pg.keyboard.press('Enter'); await pg.wait_for_timeout(1000); await pg.evaluate("(()=>{const h=document.getElementById('hint');if(getComputedStyle(h).display!=='none')h.click()})()"); await pg.wait_for_timeout(900)
        n = await pg.evaluate("document.querySelectorAll('#panel .ev-b').length"); print('opera card event links:', n)
        if n: await pg.click('#panel .ev-b >> nth=0'); await st('card > event', '3_card_event')
        await pg.keyboard.press('Escape'); await st('Escape')
        # events sheet and search
        await pg.click('.rail button[data-sheet="events"]'); await pg.wait_for_timeout(300); print('events sheet rows:', await pg.evaluate("document.querySelectorAll('#sheet button').length"))
        await pg.click('#sheet button >> nth=60'); await st('sheet pick', '4_sheet_pick')
        await pg.click('#q'); await pg.keyboard.type('phonograph', delay=30); await pg.wait_for_timeout(400); print('event results:', await pg.evaluate("[...document.querySelectorAll('#res .eres')].map(b=>b.textContent)"))
        if await pg.evaluate("document.querySelectorAll('#res .eres').length"): await pg.click('#res .eres >> nth=0'); await st('search event')
        await pg.click('#crumbs button >> nth=0'); await st('crumb Garden')
        print('errors', errs); await b.close()
try: asyncio.run(main())
finally: srv.kill()
