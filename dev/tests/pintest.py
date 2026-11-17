import asyncio, subprocess, time
from playwright.async_api import async_playwright
srv = subprocess.Popen(['python3','/home/claude/tools/serve.py','8913','/home/claude/gardenofearthlysound'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
O='/home/claude/shots/pin'
import os; os.makedirs(O, exist_ok=True)
ST="JSON.stringify({tkey:__map.tkey(), spot:__map.spot&&__map.spot(), pan:document.body.classList.contains('pan'), h1:(document.querySelector('#panel h1')||{}).textContent||'', pill:getComputedStyle(document.getElementById('hint')).display!=='none'?document.getElementById('hint').textContent:'', on:document.querySelectorAll('#map .fm.on').length, trail:[...document.querySelectorAll('#trail .tc')].map(c=>c.textContent.replace('×','')), traced:[...document.querySelectorAll('#map .fm.traced')].map(g=>g.dataset.id), tip:document.getElementById('tip').style.display==='block'?document.getElementById('tip').textContent:''})"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg = await b.new_page(viewport={'width':1600,'height':1000}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type=='error' and errs.append(m.text))
        await pg.goto('http://localhost:8913/index.html'); await pg.evaluate("localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(1500)
        async def st(label, shot=None):
            await pg.wait_for_timeout(600); print(label.ljust(24), await pg.evaluate(ST))
            if shot: await pg.screenshot(path=f'{O}/{shot}.png')
        seed = await pg.evaluate("(()=>{const c=document.querySelector('#map .fm.soil circle.hit').getBoundingClientRect();return [c.left+c.width/2,c.top+c.height/2]})()")
        # 1 click pins
        await pg.mouse.click(*seed); await st('click seed (pin)', '1_pinned')
        # 2 move off: web stays; trace along a link to its far end
        path = await pg.evaluate("""(()=>{const p=[...document.querySelectorAll('#map .lk')].find(p=>(p.dataset.a==='commons'||p.dataset.b==='commons')&&p.classList.contains('on')&&(p.dataset.b==='zarzuela'||p.dataset.a==='zarzuela'))||[...document.querySelectorAll('#map .lk.on')][5];const L=p.getTotalLength(),m=p.getScreenCTM();const pts=[];for(let i=0;i<=20;i++){const q=p.getPointAtLength(L*i/20);pts.push([m.a*q.x+m.c*q.y+m.e,m.b*q.x+m.d*q.y+m.f])}return {to:p.dataset.a==='commons'?p.dataset.b:p.dataset.a,pts}})()""")
        print('tracing toward', path['to'])
        for x,y in path['pts'][3:19]: await pg.mouse.move(x,y,steps=2)
        await st('traced to end', '2_trace')
        # 3 click on line travels
        mid = path['pts'][10]; await pg.mouse.move(*mid); await pg.wait_for_timeout(200); await pg.mouse.click(*mid); await st('click line = travel', '3_travel')
        # 4 click pinned lantern again opens card
        xy = await pg.evaluate("(()=>{const g=document.querySelector('#map .fm[data-id=\"'+__map.spot()+'\"] circle')||document.querySelector('#map .fm[data-id=\"'+__map.spot()+'\"]');const r=g.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()")
        await pg.mouse.click(*xy); await st('second click = card', '4_card')
        await pg.keyboard.press('Escape'); await st('Esc: back to pin')
        await pg.keyboard.press('Escape'); await st('Esc: released')
        # 5 shift hold quasimode
        g = await pg.evaluate("(()=>{const g=document.querySelector('#map .fm[data-id=\"opera\"]');const r=g.querySelector('circle').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()")
        await pg.mouse.move(*g); await pg.wait_for_timeout(300); await pg.keyboard.down('Shift'); await pg.wait_for_timeout(500)
        await pg.mouse.move(g[0]+60, g[1]-40, steps=6); await st('shift held, moved off')
        await pg.keyboard.up('Shift'); await st('shift released')
        # 6 tap toggle
        await pg.mouse.move(*g); await pg.wait_for_timeout(300); await pg.keyboard.press('Shift'); await pg.mouse.move(g[0]+60, g[1]-40, steps=4); await st('shift tapped: pinned')
        await pg.keyboard.press('Shift'); await st('tapped again: released')
        # 7 shift-click collect
        await pg.keyboard.down('Shift'); await pg.mouse.click(*g); await pg.keyboard.up('Shift'); await st('shift-click opera', '5_trail')
        # 8 star pin then open
        await pg.keyboard.press('Escape'); 
        sxy = await pg.evaluate("(()=>{const g=__map.STAR[Object.keys(__map.STAR)[0]];const r=g.querySelector('path').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()")
        await pg.mouse.click(*sxy); await st('star click: thread pinned')
        await pg.mouse.click(*sxy); await st('star again: card')
        # 9 persistence
        await pg.reload(); await pg.wait_for_timeout(1500); await st('after reload (trail kept)')
        # 10 search still opens card directly
        await pg.click('#q'); await pg.keyboard.type('sonata form', delay=15); await pg.keyboard.press('Enter'); await st('search Enter')
        print('errors', errs); await b.close()
try: asyncio.run(main())
finally: srv.kill()
