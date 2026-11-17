import asyncio, subprocess, time
from playwright.async_api import async_playwright
srv = subprocess.Popen(['python3','/home/claude/tools/serve.py','8892','/home/claude/gardenofearthlysound'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
O='/home/claude/shots/card'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg = await b.new_page(viewport={'width':1600,'height':1000}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type=='error' and errs.append(m.text))
        await pg.goto('http://localhost:8892/index.html'); await pg.wait_for_timeout(1200)
        S = "(()=>{const a=document.getElementById('panel');return {h3:[...a.querySelectorAll('h3,details.sec>summary')].map(x=>x.textContent),works:a.querySelectorAll('.plist li').length,listen:a.querySelectorAll('.acts a').length,qs:a.querySelectorAll('.qs>li').length,notices:a.querySelectorAll('.cnotice,.pnotice').length,els:a.querySelectorAll('.els>button').length,kw:a.querySelectorAll('button.kw').length,title:a.querySelector('h1').textContent}})()"
        async def open_(q, shot):
            await pg.click('#q'); await pg.keyboard.type(q, delay=25); await pg.keyboard.press('Enter'); await pg.wait_for_timeout(1100); await pg.evaluate("(()=>{const h=document.getElementById('hint');if(getComputedStyle(h).display!=='none')h.click()})()"); await pg.wait_for_timeout(900)
            print(q.ljust(18), await pg.evaluate(S)); await pg.screenshot(path=f'{O}/{shot}.png')
        import os; os.makedirs(O, exist_ok=True)
        await open_('sonata form', '1_sonata')
        await pg.click('#panel .els>button >> nth=0'); await pg.wait_for_timeout(300); print('element card open:', await pg.evaluate("!!document.querySelector('#panel .ecard')"))
        await pg.evaluate("document.querySelector('#panel .ecard').scrollIntoView({block:'center'})"); await pg.screenshot(path=f'{O}/2_element.png')
        kw = await pg.query_selector('#panel .brief button.kw')
        if kw: await kw.click(); await pg.wait_for_timeout(300); print('glossary open:', await pg.evaluate("!!document.querySelector('#panel .gdef')"))
        await pg.click('#panel .qs details summary >> nth=0'); print('hint open:', await pg.evaluate("document.querySelector('#panel .qs details').open"))
        await pg.click('#panel details.nsw summary'); await pg.wait_for_timeout(200); await pg.evaluate("document.querySelector('#panel details.nsw').scrollIntoView({block:'start'})"); await pg.screenshot(path=f'{O}/3_nsw.png')
        print('nsw rows:', await pg.evaluate("document.querySelectorAll('#panel .nsw-in > p').length"))
        await pg.click('#panel .conn-g .lk-b >> nth=0'); await pg.wait_for_timeout(1000); print('followed to:', await pg.evaluate("document.querySelector('#panel h1').textContent"))
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)
        await open_('Aboriginal and Torres Strait Islander composers', '4_atsi')
        await open_('the commons', '5_commons')
        await open_('generative', '6_modern')
        await pg.evaluate("document.querySelector('#panel details.nsw').open=true; document.querySelector('#panel details.nsw').scrollIntoView({block:'start'})"); await pg.screenshot(path=f'{O}/7_modern_nsw.png')
        print('errors', errs); await b.close()
try: asyncio.run(main())
finally: srv.kill()
