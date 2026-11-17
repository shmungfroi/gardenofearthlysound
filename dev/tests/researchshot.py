import asyncio, subprocess, time
from playwright.async_api import async_playwright
srv = subprocess.Popen(['python3','/home/claude/tools/serve.py','8925','/home/claude/gardenofearthlysound'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg = await b.new_page(viewport={'width':1600,'height':1000}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8925/index.html#l=romlied'); await pg.wait_for_timeout(2000)
        await pg.evaluate("document.querySelector('#panel .research').scrollIntoView({block:'center'})"); await pg.wait_for_timeout(400)
        el = await pg.query_selector('#panel .research'); li = await el.evaluate_handle("e=>e.closest('li')")
        await li.as_element().screenshot(path='/home/claude/shots/stars/research.png')
        print('count', await pg.evaluate("document.querySelectorAll('#panel .research').length"), 'errors', errs); await b.close()
try: asyncio.run(main())
finally: srv.kill()
