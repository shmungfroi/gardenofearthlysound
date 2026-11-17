import asyncio, subprocess, time
from playwright.async_api import async_playwright
srv = subprocess.Popen(['python3','/home/claude/tools/serve.py','8916','/home/claude/gardenofearthlysound'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
O='/home/claude/shots/f6'; U='http://localhost:8916/index.html'
ST="JSON.stringify({hash:location.hash, spot:__map.spot(), tkey:__map.tkey(), pan:document.body.classList.contains('pan'), h1:document.body.classList.contains('pan')?(document.querySelector('#panel h1')||{}).textContent:'', lens:[...__map.lens.on], n:__map.lens.n, trail:[...document.querySelectorAll('#trail .tc')].map(c=>c.textContent.replace('×','')), tl:(document.querySelector('#trail .tl')||{}).textContent||'', traced:[...document.querySelectorAll('#map .fm.traced')].map(g=>g.dataset.id), say:document.getElementById('say').textContent.slice(0,90)})"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        ctx = await b.new_context(viewport={'width':1600,'height':1000}); await ctx.grant_permissions(['clipboard-read','clipboard-write'], origin='http://localhost:8916')
        pg = await ctx.new_page(); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type=='error' and errs.append(m.text))
        async def st(label, shot=None, page=None):
            pp = page or pg; await pp.wait_for_timeout(700); print(label.ljust(26), await pp.evaluate(ST))
            if shot: await pp.screenshot(path=f'{O}/{shot}.png')
        # deep links
        await pg.goto(U+'#l=fugue&lens=w'); await st('link l=fugue lens=w', 'd1_card_link')
        await pg.click('#panel .share'); await pg.wait_for_timeout(300); print('clipboard:', await pg.evaluate('navigator.clipboard.readText()'))
        await pg.goto('about:blank'); await pg.goto(U+'#p=opera'); await st('link p=opera')
        await pg.keyboard.press(']'); await pg.wait_for_timeout(200); await pg.keyboard.press(']'); await st('] ] keyboard trace', 'd2_keytrace')
        await pg.keyboard.press('Enter'); await st('Enter travels')
        await pg.keyboard.press('Enter'); await st('Enter opens card')
        await pg.goto('about:blank'); await pg.goto(U+'#v=c-tan-dun'); await st('link v=c-tan-dun')
        await pg.goto('about:blank'); await pg.goto(U+'#n=r-t-quartet'); await st('link n=route')
        await pg.goto('about:blank'); await pg.goto(U+'#trail=zarzuela,opera,quartet,fugue'); await st('link trail', 'd3_shared_trail')
        await pg.click('#trail .tsh'); await st('keep as my trail')
        await pg.click('#trail .tsh >> text=Share'); await pg.wait_for_timeout(300); print('trail link:', await pg.evaluate('navigator.clipboard.readText()'))
        await pg.goto('about:blank'); await pg.goto(U+'#l=nonsense&lens=zz'); await st('bad link (ignored)')
        # phone
        m = await b.new_context(viewport={'width':390,'height':844}, is_mobile=True, has_touch=True, device_scale_factor=2)
        mp = await m.new_page(); mp.on('pageerror', lambda e: errs.append('M '+str(e)))
        await mp.goto(U); await mp.wait_for_timeout(1500); await mp.screenshot(path=f'{O}/m1_garden.png')
        await mp.evaluate("(()=>{const q=__map.LAY.nodes.opera;__map.fitBox(q.x-25,q.y-40,q.x+25,q.y+40,5)})()"); await mp.wait_for_timeout(1200)
        xy = await mp.evaluate("(()=>{const r=document.querySelector('#map .fm[data-id=opera] circle').getBoundingClientRect();return [r.left+r.width/2+6,r.top+r.height/2+5]})()")
        await mp.touchscreen.tap(*xy); await st('tap near opera (pin)', 'm2_pinned', mp)
        await mp.touchscreen.tap(*xy); await st('tap again (card)', 'm3_card', mp)
        await mp.evaluate("document.querySelector('#panel .x').click()"); await st('close: back to pin', None, mp)
        # hold then drag along a line
        path = await mp.evaluate("""(()=>{const here0=__map.spot();const ps=[...document.querySelectorAll('#map .lk')].filter(p=>p.dataset.a===here0||p.dataset.b===here0);const p=ps.find(p=>{const L=p.getTotalLength();const M0=p.getScreenCTM(),q=p.getPointAtLength(L*.6),x=M0.a*q.x+M0.c*q.y+M0.e,y=M0.b*q.x+M0.d*q.y+M0.f;return L>20&&x>10&&x<380&&y>60&&y<760})||ps[0];const L=p.getTotalLength(),M=p.getScreenCTM();const pts=[];for(let i=0;i<=24;i++){const q=p.getPointAtLength(L*i/24);pts.push([M.a*q.x+M.c*q.y+M.e,M.b*q.x+M.d*q.y+M.f])}const here=__map.spot();return {to:p.dataset.a===here?p.dataset.b:p.dataset.a,pts,start:p.dataset.a===here}})()""")
        pts = path['pts'] if path['start'] else path['pts'][::-1]
        await mp.evaluate("window.__pm=0;document.getElementById('map').addEventListener('pointermove',e=>{__pm++;__lastT=[e.pointerType,Math.round(e.clientX),Math.round(e.clientY),e.target.tagName+'.'+(e.target.getAttribute('class')||'')]})")
        cdp = await m.new_cdp_session(mp)
        tp = lambda x,y: [{'x':x,'y':y,'id':1}]
        await cdp.send('Input.dispatchTouchEvent', {'type':'touchStart','touchPoints':tp(*xy)}); await mp.wait_for_timeout(650)
        for x,y in pts[2:23]: await cdp.send('Input.dispatchTouchEvent', {'type':'touchMove','touchPoints':tp(x,y)}); await mp.wait_for_timeout(30)
        await st('hold + trace to '+path['to'], 'm4_trace', mp)
        print('DBG', await mp.evaluate("[window.__pm, window.__lastT]"), pts[2], pts[12], xy)
        await cdp.send('Input.dispatchTouchEvent', {'type':'touchEnd','touchPoints':[]})
        # pinch
        k0 = await mp.evaluate('__map.view.k')
        await cdp.send('Input.dispatchTouchEvent', {'type':'touchStart','touchPoints':[{'x':150,'y':400,'id':1},{'x':240,'y':400,'id':2}]})
        for i in range(1,8): await cdp.send('Input.dispatchTouchEvent', {'type':'touchMove','touchPoints':[{'x':150-i*12,'y':400,'id':1},{'x':240+i*12,'y':400,'id':2}]}); await mp.wait_for_timeout(20)
        await cdp.send('Input.dispatchTouchEvent', {'type':'touchEnd','touchPoints':[]}); await mp.wait_for_timeout(300)
        print('pinch k', round(k0,2), '->', round(await mp.evaluate('__map.view.k'),2))
        await mp.click('.rail button[data-sheet="guide"]'); await mp.wait_for_timeout(400); await mp.screenshot(path=f'{O}/m5_guide.png')
        print('rail visible buttons:', await mp.evaluate("[...document.querySelectorAll('.rail button')].filter(b=>{const r=b.getBoundingClientRect();return r.right<=innerWidth&&r.bottom<=innerHeight}).length"))
        print('errors', errs); await b.close()
try: asyncio.run(main())
finally: srv.kill()
