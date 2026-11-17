import asyncio, subprocess, time
from playwright.async_api import async_playwright
srv = subprocess.Popen(['python3','/home/claude/tools/serve.py','8921','/home/claude/gardenofearthlysound'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
O='/home/claude/shots/stars'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg = await b.new_page(viewport={'width':1600,'height':1000}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8921/index.html'); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_timeout(1500)
        await pg.evaluate("__map.goEra(null,'contemporary')"); await pg.wait_for_timeout(1300)
        await pg.hover('.era .starkey'); await pg.wait_for_timeout(500); await pg.screenshot(path=f'{O}/1_key_hover.png')
        xy = await pg.evaluate("(()=>{const g=Object.values(__map.STAR).find(g=>{const r=g.getBoundingClientRect();return r.left>300&&r.right<1400&&r.top>100&&r.bottom<900&&g._V.name.includes('recki')})||Object.values(__map.STAR).find(g=>{const r=g.getBoundingClientRect();return r.left>300&&r.right<1400&&r.top>100&&r.bottom<900});const r=g.querySelector('path').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()")
        await pg.mouse.move(0,0); await pg.mouse.move(*xy, steps=4); await pg.wait_for_timeout(500); await pg.screenshot(path=f'{O}/2_star_hover.png')
        print('lit', await pg.evaluate("document.querySelectorAll('#map .fm.stpre').length"))
        await pg.mouse.move(xy[0]+200, xy[1]+200); await pg.wait_for_timeout(300); print('cleared', await pg.evaluate("document.querySelectorAll('#map .fm.stpre').length"))
        await pg.click('.era .starkey'); await pg.wait_for_timeout(500); print('sheet', await pg.evaluate("document.querySelector('#sheet h3').textContent"))
        print('errors', errs); await b.close()
try: asyncio.run(main())
finally: srv.kill()
