import asyncio, subprocess, time
from playwright.async_api import async_playwright
srv = subprocess.Popen(['python3','/home/claude/tools/serve.py','8896','/home/claude/gardenofearthlysound'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
O='/home/claude/shots/f5'
ST="JSON.stringify({ln:document.querySelectorAll('#map .fm.ln').length, rings:document.querySelectorAll('#lens circle:not(.rt-dot)').length, stops:document.querySelectorAll('#lens .rt-n').length, chips:[...document.querySelectorAll('#lensbar span')].map(s=>s.textContent.replace('×','').trim()), lensed:document.getElementById('map').classList.contains('lensed'), h1:(document.querySelector('#panel h1')||{}).textContent||'', route:(document.querySelector('#panel .route small')||{}).textContent||''})"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg = await b.new_page(viewport={'width':1600,'height':1000}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type=='error' and errs.append(m.text))
        await pg.goto('http://localhost:8896/index.html'); await pg.wait_for_timeout(1200)
        async def st(label, shot=None):
            await pg.wait_for_timeout(900); print(label.ljust(22), await pg.evaluate(ST))
            if shot: await pg.screenshot(path=f'{O}/{shot}.png')
        await pg.click('.rail button[data-sheet="lenses"]'); await pg.wait_for_timeout(300)
        print('sheet toggles:', await pg.evaluate("[...document.querySelectorAll('#sheet .lz')].map(l=>l.textContent)"))
        print('options:', await pg.evaluate("document.querySelectorAll('#sheet select option').length"), 'groups:', await pg.evaluate("[...document.querySelectorAll('#sheet optgroup')].map(g=>g.label)"))
        await pg.click('#sheet .lz >> nth=0'); await st('women', '1_women')
        await pg.click('#sheet .lz >> nth=3'); await st('women + strand', '2_women_strand')
        await pg.click('#sheet .lz >> nth=0'); await pg.click('#sheet .lz >> nth=3'); await st('both off')
        await pg.click('#sheet .lz >> nth=2'); await st('oral & folk', '3_folk')
        await pg.click('#sheet .lz >> nth=2')
        await pg.select_option('#sheet select', 'm2-el-bar'); await st('NSW baroque elective', '4_nsw_baroque')
        await pg.select_option('#sheet select', 'r-mwat1'); await st('route MWAT1', '5_route')
        print('route list:', await pg.evaluate("[...document.querySelectorAll('#sheet .stops button')].slice(0,4).map(b=>b.textContent)"))
        await pg.click('#sheet .stops button >> nth=1'); await st('route stop 2', '6_route_card')
        await pg.click('#panel .route .thread-nav button >> nth=-1'); await st('route next')
        await pg.keyboard.press('Escape'); await st('Escape')
        await pg.click('#lensbar button >> nth=0'); await st('chip off')
        # selection still works with a lens on
        await pg.evaluate("__map.setLens('a', true)"); await pg.click('#q'); await pg.keyboard.type('sonata form', delay=20); await pg.keyboard.press('Enter'); await pg.wait_for_timeout(900); await pg.evaluate("(()=>{const h=document.getElementById('hint');if(getComputedStyle(h).display!=='none')h.click()})()"); await st('lens + card', '7_lens_card')
        await pg.evaluate("__map.home()"); await st('home keeps lens')
        print('errors', errs); await b.close()
try: asyncio.run(main())
finally: srv.kill()
