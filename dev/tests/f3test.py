import asyncio, subprocess, time
from playwright.async_api import async_playwright
srv = subprocess.Popen(['python3','/home/claude/tools/serve.py','8905','/home/claude/gardenofearthlysound'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
O='/home/claude/shots/f3'
ST="JSON.stringify({h1:(document.querySelector('#panel h1')||{}).textContent||'', glows:document.querySelectorAll('#reach .rl-glow').length, spots:document.querySelectorAll('#reachspots .spot').length, rib:document.querySelectorAll('#reach .rb-rib').length, list:document.querySelectorAll('#panel .reach li').length})"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg = await b.new_page(viewport={'width':1600,'height':1000}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type=='error' and errs.append(m.text))
        await pg.goto('http://localhost:8905/index.html'); await pg.wait_for_timeout(1200)
        async def st(label, shot=None):
            await pg.wait_for_timeout(1000); print(label.ljust(22), await pg.evaluate(ST))
            if shot: await pg.screenshot(path=f'{O}/{shot}.png')
        await pg.click('.rail button[data-sheet="styles"]'); await pg.wait_for_timeout(300)
        print('sheet rows', await pg.evaluate("document.querySelectorAll('#sheet button').length"), await pg.evaluate("[...document.querySelectorAll('#sheet button')].slice(0,3).map(b=>b.textContent)"))
        await pg.click('#sheet button >> nth=0'); await st('first style', '1_style')
        # hover a sun
        xy = await pg.evaluate("(()=>{const z=document.querySelector('#reachspots .spot .hitc');const r=z.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()")
        await pg.mouse.move(*xy); await pg.wait_for_timeout(300); print('tip:', (await pg.evaluate("document.getElementById('tip').textContent"))[:160]); await pg.screenshot(path=f'{O}/2_sun_hover.png')
        await pg.mouse.click(*xy); await st('click sun')
        await pg.evaluate("__map.choose('fugue', true)"); await st('fugue band', '3_fugue')
        await pg.click('#panel .reach .lk-b >> nth=1'); await st('card reach link')
        await pg.evaluate("__map.choose('sonataform', true)"); await st('sonata form', '4_sonata')
        await pg.evaluate("__map.choose('impressionism', true)"); await st('impressionism', '5_impress')
        await pg.keyboard.press('Escape'); await st('escape')
        print('errors', errs); await b.close()
try: asyncio.run(main())
finally: srv.kill()
