import asyncio, subprocess, time
from playwright.async_api import async_playwright
srv = subprocess.Popen(['python3','/home/claude/tools/serve.py','8898','/home/claude/gardenofearthlysound'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
O='/home/claude/shots/f7'
ST="JSON.stringify({h1:(document.querySelector('#panel h1')||{}).textContent||'', hits:document.querySelectorAll('#hit path').length, route:(document.querySelector('#panel .route small')||{}).textContent||'', also:[...document.querySelectorAll('#panel .rt-b span')].map(s=>s.textContent), chip:[...document.querySelectorAll('#lensbar span')].map(s=>s.textContent.replace('×','').trim())})"
# find a screen point on the middle of a hit path
MID="(i=>{const z=document.querySelectorAll('#hit path')[i];const L=z.getTotalLength(),pt=z.getPointAtLength(L*.5),m=z.getScreenCTM();return [m.a*pt.x+m.c*pt.y+m.e, m.b*pt.x+m.d*pt.y+m.f]})"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg = await b.new_page(viewport={'width':1600,'height':1000}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type=='error' and errs.append(m.text))
        await pg.goto('http://localhost:8898/index.html'); await pg.wait_for_timeout(1200)
        async def st(label, shot=None):
            await pg.wait_for_timeout(900); print(label.ljust(22), await pg.evaluate(ST))
            if shot: await pg.screenshot(path=f'{O}/{shot}.png')
        await pg.evaluate("__map.choose('opera', true)"); await st('opera')
        # hover a link mid point
        for i in range(12):
            xy = await pg.evaluate(MID+f"({i})")
            if 120 < xy[0] < 1150 and 70 < xy[1] < 980: break
        await pg.mouse.move(*xy); await pg.wait_for_timeout(300); print('tip:', await pg.evaluate("document.getElementById('tip').textContent")); await pg.screenshot(path=f'{O}/1_link_hover.png')
        await pg.mouse.click(*xy); await st('click link', '2_after_link')
        # routes in card
        await pg.evaluate("__map.choose('cantata', true)"); await st('cantata card')
        await pg.click('#panel .rt-b >> nth=0'); await st('walk from card', '3_walk')
        await pg.click('#panel .thread-nav .lk-b >> nth=-1'); await st('next stop')
        # click a route segment
        segs = await pg.evaluate("[...document.querySelectorAll('#hit path')].length"); print('hit paths incl route:', segs)
        await pg.click('#panel .rt-leave'); await st('leave route')
        # search a route
        await pg.click('#q'); await pg.keyboard.type('quartet', delay=25); await pg.wait_for_timeout(400); print('route results:', await pg.evaluate("[...document.querySelectorAll('#res .rres')].map(b=>b.textContent)"))
        await pg.click('#res .rres >> nth=0'); await st('search route', '4_search_route')
        # route segment hover/click at garden level, nothing selected
        n = await pg.evaluate("document.querySelectorAll('#hit path').length"); print('route segment hits:', n)
        xy = await pg.evaluate(MID+"(2)"); await pg.mouse.move(*xy); await pg.wait_for_timeout(300); print('seg tip:', await pg.evaluate("document.getElementById('tip').textContent"))
        await pg.mouse.click(*xy); await st('click segment', '5_seg'); print('DBG', await pg.evaluate("[__map.spot&&__map.spot(), document.body.classList.contains('pan'), document.getElementById('hint').textContent]"))
        # event link
        await pg.evaluate("__map.setCourse('')"); await pg.evaluate("__map.showEvent('petrucci')"); await pg.wait_for_timeout(1200)
        xy = await pg.evaluate(MID+"(0)"); await pg.mouse.move(*xy); await pg.wait_for_timeout(300); print('ev tip:', await pg.evaluate("document.getElementById('tip').textContent"))
        await pg.mouse.click(*xy); await st('click event line')
        print('errors', errs); await b.close()
try: asyncio.run(main())
finally: srv.kill()
