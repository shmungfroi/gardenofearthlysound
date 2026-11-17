import asyncio, subprocess, time
from playwright.async_api import async_playwright
srv = subprocess.Popen(['python3','/home/claude/tools/serve.py','8894','/home/claude/gardenofearthlysound'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
O='/home/claude/shots/f2'
ST="JSON.stringify({lvl:__map.level(), thread:__map.tkey(), crumbs:[...document.querySelectorAll('#crumbs button')].map(b=>b.textContent).join(' > '), panel:document.body.classList.contains('pan'), on:document.querySelectorAll('#map .fm.on').length, rings:document.querySelectorAll('#thread circle').length, h1:(document.querySelector('#panel h1')||{}).textContent||'', rung4:!document.querySelector('.rung[data-l=\"4\"]').hidden})"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg = await b.new_page(viewport={'width':1600,'height':1000}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type=='error' and errs.append(m.text))
        await pg.goto('http://localhost:8894/index.html'); await pg.wait_for_timeout(1200)
        async def st(label, shot=None):
            await pg.wait_for_timeout(1000); print(label.ljust(24), await pg.evaluate(ST))
            if shot: await pg.screenshot(path=f'{O}/{shot}.png')
        # 1. search a form, open it, follow a composer name in Listen
        await pg.click('#q'); await pg.keyboard.type('symphony', delay=25); await pg.wait_for_timeout(300)
        await pg.click('#res button:not(.vres) >> text=Symphony'); await pg.wait_for_timeout(1000); await pg.evaluate("(()=>{const h=document.getElementById('hint');if(getComputedStyle(h).display!=='none')h.click()})()"); await st('card: Symphony')
        await pg.click('#panel .plist .voice-b >> text=Beethoven'); await st('thread: Beethoven', '1_beethoven')
        # 2. follow the thread to one of its lanterns
        await pg.click('#panel .thr .lk-b >> nth=2'); await st('thread lantern clicked')
        # 3. composer window chip
        await pg.click('#panel .wins .win-b >> nth=0'); await st('window chip')
        await pg.keyboard.press('Escape'); await st('Escape')
        # 4. composer search
        await pg.click('#q'); await pg.keyboard.type('Peggy', delay=30); await pg.wait_for_timeout(400)
        print('composer results:', await pg.evaluate("[...document.querySelectorAll('#res .vres')].map(b=>b.textContent)"))
        await pg.click('#res .vres >> nth=0'); await st('search: Glanville-Hicks', '2_glanville')
        # 5. Voices sheet, women filter
        await pg.click('.rail button[data-sheet="voices"]'); await pg.wait_for_timeout(300)
        n0 = await pg.evaluate("document.querySelectorAll('#sheet .vlist button').length")
        await pg.click('#sheet .vopts label >> nth=0'); await pg.wait_for_timeout(200)
        n1 = await pg.evaluate("document.querySelectorAll('#sheet .vlist button').length"); print('voices list (2+ lanterns):', n0, '| women only:', n1)
        await pg.screenshot(path=f'{O}/3_voices_sheet.png')
        await pg.click('#sheet .vlist button >> nth=0'); await st('voices sheet pick')
        # 6. breadcrumb back to Garden; ladder
        await pg.click('#crumbs button >> nth=0'); await st('crumb Garden')
        await pg.click('.rung[data-l="1"]'); await st('rung Spire')
        print('errors', errs); await b.close()
try: asyncio.run(main())
finally: srv.kill()
