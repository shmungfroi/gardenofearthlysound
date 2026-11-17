import asyncio, subprocess, time
from playwright.async_api import async_playwright
srv = subprocess.Popen(['python3','/home/claude/tools/serve.py','8924','/home/claude/gardenofearthlysound'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg = await b.new_page(viewport={'width':1600,'height':1000}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8924/index.html#l=romlied'); await pg.wait_for_timeout(2000)
        print(await pg.evaluate("[...document.querySelectorAll('#panel a')].filter(a=>a.href.includes('W_NmN748b2w')||a.href.includes('jCXTFPHT1AQ')).map(a=>a.href+' | '+(a.closest('li,div')||a).innerText.slice(0,160).replace(/\\n/g,' / '))"))
        print('errors', errs); await b.close()
try: asyncio.run(main())
finally: srv.kill()
