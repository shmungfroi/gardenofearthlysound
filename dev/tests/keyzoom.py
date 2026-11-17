import asyncio, subprocess, time
from playwright.async_api import async_playwright
srv = subprocess.Popen(['python3','/home/claude/tools/serve.py','8923','/home/claude/gardenofearthlysound'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg = await b.new_page(viewport={'width':1600,'height':1000}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8923/index.html'); await pg.wait_for_timeout(1500)
        vis = "getComputedStyle(document.querySelector('.era .starkey')).visibility"
        print('garden', await pg.evaluate("__map.view.k.toFixed(2)"), await pg.evaluate(vis))
        await pg.evaluate("(()=>{const e=__map.LAY.eras.find(e=>e.id==='contemporary'),b=__map.LAY.bounds;__map.fitBox(b[0],e.top-40,b[2],e.bottom+40,3)})()"); await pg.wait_for_timeout(1300)
        print('mid', await pg.evaluate("__map.view.k.toFixed(2)"), await pg.evaluate(vis))
        await pg.evaluate("__map.goEra(null,'contemporary')"); await pg.wait_for_timeout(1300)
        print('storey', await pg.evaluate("__map.view.k.toFixed(2)"), await pg.evaluate(vis))
        await pg.screenshot(path='/home/claude/shots/stars/3_storey.png')
        print('errors', errs); await b.close()
try: asyncio.run(main())
finally: srv.kill()
