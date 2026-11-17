import asyncio, subprocess, time, json
from playwright.async_api import async_playwright
srv = subprocess.Popen(['python3','/home/claude/tools/serve.py','8890','/home/claude/live/site'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
O = '/home/claude/shots/live'
ST = "JSON.stringify({lvl:__map.level(), k:+__map.view.k.toFixed(2), crumbs:[...document.querySelectorAll('#crumbs button')].map(b=>b.textContent).join(' > '), panel:document.body.classList.contains('pan'), hint:getComputedStyle(document.getElementById('hint')).display==='block'?document.getElementById('hint').textContent:'', on:document.querySelectorAll('#map .fm.on').length, me:(document.querySelector('#map .fm.me')||{}).dataset?.id||''})"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        pg = await b.new_page(viewport={'width':1600,'height':1000}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text))
        await pg.goto('http://localhost:8890/index.html'); await pg.wait_for_timeout(1500)
        async def shot(n, label):
            await pg.wait_for_timeout(900); await pg.screenshot(path=f'{O}/{n}.png'); print(label.ljust(22), await pg.evaluate(ST))
        await shot('01_garden', 'garden')
        await pg.click('.fam:has-text("SACRED")'); await shot('02_family', 'family strip: Sacred')
        await pg.click('.era:has-text("BAROQUE")'); await shot('03_era', 'gutter: Baroque')
        # click the first visible form name on screen
        box = await pg.evaluate("""(()=>{for(const g of document.querySelectorAll('#map .fm:not(.soil)')){const r=g.querySelector('text').getBoundingClientRect();const m=document.getElementById('map').getBoundingClientRect();if(r.left>m.left+40&&r.right<m.right-40&&r.top>m.top+40&&r.bottom<m.bottom-160)return [r.left+r.width/2,r.top+r.height/2,g.dataset.id]}})()""")
        await pg.mouse.click(box[0], box[1]); await shot('04_form', f'click form {box[2]}')
        await pg.click('aside .conn-g .lk-b >> nth=0'); await shot('05_chip', 'panel chip')
        await pg.click('#crumbs button >> nth=0'); await shot('06_home', 'crumb: Garden')
        await pg.click('#q'); await pg.keyboard.type('sonata form', delay=30); await pg.keyboard.press('Enter'); await shot('07_spot', 'search sonata form')
        await pg.click('#hint'); await shot('08_open', 'hint opens card')
        await pg.keyboard.press('Escape'); await shot('09_esc', 'Escape closes')
        await pg.click('.rung[data-l="1"]'); await shot('10_rung_family', 'ladder: Family')
        await pg.keyboard.press('ArrowRight'); await shot('11_right', 'arrow right')
        await pg.keyboard.press('ArrowUp'); await shot('12_up', 'arrow up (later era)')
        await pg.click('#zout'); await pg.click('#zout'); await shot('13_out', 'minus twice')
        mm = await pg.evaluate("(()=>{const r=document.getElementById('mm').getBoundingClientRect();return [r.left+r.width*.78,r.top+r.height*.3]})()")
        await pg.mouse.click(*mm); await shot('14_minimap', 'minimap click')
        await pg.mouse.move(800, 500); await pg.mouse.down(); await pg.mouse.move(600, 420, steps=8); await pg.mouse.up(); await shot('15_drag', 'drag')
        for i in range(6): await pg.mouse.wheel(0, -300); await pg.wait_for_timeout(60)
        await shot('16_wheel', 'wheel in')
        await pg.click('.rail button[data-sheet="az"]'); await pg.wait_for_timeout(300); await pg.click('#sheet button >> nth=3'); await shot('17_az', 'A-Z pick')
        await pg.click('.rail button[data-sheet="guide"]'); await shot('18_guide', 'guide sheet')
        await pg.keyboard.press('Escape'); await pg.click('.rung[data-l="0"]'); await shot('19_back', 'ladder: Garden')
        # the commons pyramid
        pyr = await pg.evaluate("(()=>{const r=document.querySelector('#map .fm.soil .hit').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height*.7]})()")
        await pg.mouse.click(*pyr); await shot('20_commons', 'click pyramid')
        print('errors', errs); await b.close()
try: asyncio.run(main())
finally: srv.kill()
