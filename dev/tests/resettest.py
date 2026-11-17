import asyncio, subprocess, time
from playwright.async_api import async_playwright
srv = subprocess.Popen(['python3','/home/claude/tools/serve.py','8919','/home/claude/gardenofearthlysound'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg = await b.new_page(viewport={'width':1600,'height':1000}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8919/index.html'); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_timeout(1500)
        await pg.evaluate("__map.pin('fugue'); __map.travel('ricercar'); __map.travel('canzona')"); await pg.wait_for_timeout(400)
        await pg.click('.rail button[data-sheet="journeys"]'); await pg.wait_for_timeout(300)
        await pg.click('.sheet .jbig >> text=Save your trail'); await pg.wait_for_timeout(300); await pg.keyboard.press('Escape')
        await pg.click('.rail button[data-sheet="journeys"]'); await pg.wait_for_timeout(300)
        print('before', await pg.evaluate("[__map.trail(), document.querySelector('.sheet .jreset').textContent]"))
        await pg.screenshot(path='/home/claude/shots/journey/9_reset_btn.png')
        await pg.click('.sheet .jreset'); await pg.wait_for_timeout(400)
        print('after', await pg.evaluate("[__map.trail(), document.getElementById('toast').textContent, JSON.parse(localStorage.getItem('garden.journeys')).length, document.querySelector('.sheet .jreset').disabled]"))
        await pg.screenshot(path='/home/claude/shots/journey/10_reset_done.png')
        await pg.click('#toast .undo'); await pg.wait_for_timeout(300); print('undo', await pg.evaluate("__map.trail()"))
        await pg.keyboard.press('Escape'); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300); await pg.click('#trail .tclr'); await pg.wait_for_timeout(300); print('strip clear', await pg.evaluate("[__map.trail(), !!document.querySelector('#toast .undo')]"))
        print('errors', errs); await b.close()
try: asyncio.run(main())
finally: srv.kill()
