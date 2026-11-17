import asyncio, subprocess, time
from playwright.async_api import async_playwright
srv = subprocess.Popen(['python3','/home/claude/tools/serve.py','8920','/home/claude/gardenofearthlysound'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg = await b.new_page(viewport={'width':1600,'height':1000}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8920/index.html'); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_timeout(1500)
        await pg.screenshot(path='/home/claude/shots/grass/1_world.png')
        await pg.evaluate("(()=>{const L=__map.LAY,b=L.bounds;__map.fitBox(b[0],L.ground-120,b[2],b[3],8)})()"); await pg.wait_for_timeout(1200)
        await pg.screenshot(path='/home/claude/shots/grass/2_field.png')
        await pg.evaluate("(()=>{const L=__map.LAY,c=L.nodes.commons;__map.fitBox(c.x-260,L.ground-60,c.x+260,c.y+20,8)})()"); await pg.wait_for_timeout(1200)
        await pg.screenshot(path='/home/claude/shots/grass/3_close.png')
        print('errors', errs); await b.close()
try: asyncio.run(main())
finally: srv.kill()
