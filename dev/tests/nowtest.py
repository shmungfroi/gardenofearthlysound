import asyncio, subprocess, time
from playwright.async_api import async_playwright
srv = subprocess.Popen(['python3','/home/claude/tools/serve.py','8908','/home/claude/gardenofearthlysound'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
O='/home/claude/shots/now'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg = await b.new_page(viewport={'width':1600,'height':1000}, device_scale_factor=1); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type=='error' and errs.append(m.text))
        await pg.goto('http://localhost:8908/index.html'); await pg.wait_for_timeout(1500)
        print('stars', await pg.evaluate("document.querySelectorAll('#stars .st').length"), 'makers', await pg.evaluate("Object.values(window.GardenCard.VOICES).filter(V=>V.forms.some(f=>{const n=window.GX.DATA.nodes.find(x=>x.id===f.id);return n&&n.period==='contemporary'})).length"))
        await pg.screenshot(path=f'{O}/0_garden.png')
        await pg.evaluate("__map.fitBox(150,40,900,190,20)"); await pg.wait_for_timeout(1300); await pg.screenshot(path=f'{O}/1_now_left.png')
        await pg.evaluate("__map.fitBox(880,40,1560,190,20)"); await pg.wait_for_timeout(1300); await pg.screenshot(path=f'{O}/2_now_right.png')
        # zoom close on concerto now
        await pg.evaluate("(()=>{const p=__map.LAY.nodes.concertonow;__map.fitBox(p.x-30,p.y-20,p.x+30,p.y+20,20)})()"); await pg.wait_for_timeout(1300); await pg.screenshot(path=f'{O}/3_close.png')
        print('visible names', await pg.evaluate("[...document.querySelectorAll('#stars .stn')].filter(t=>getComputedStyle(t).display!=='none'&&t.getBoundingClientRect().width).length"))
        xy = await pg.evaluate("(()=>{const g=__map.STAR[Object.keys(__map.STAR).find(k=>__map.STAR[k]._V.name==='Tan Dun')];const r=g.querySelector('path').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()")
        await pg.mouse.move(*xy); await pg.wait_for_timeout(300); print('tip:', await pg.evaluate("document.getElementById('tip').textContent"))
        await pg.mouse.click(*xy); await pg.wait_for_timeout(1300); print('thread', await pg.evaluate("__map.tkey()"), await pg.evaluate("(document.querySelector('#panel h1')||{}).textContent"))
        await pg.screenshot(path=f'{O}/4_thread.png')
        print('foot', await pg.evaluate("document.getElementById('foot').textContent"))
        print(errs); await b.close()
try: asyncio.run(main())
finally: srv.kill()
