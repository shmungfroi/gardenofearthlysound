"""Search reaches every glossary term and dance (19 Nov 2026). Prints errors []."""
import asyncio, subprocess, time, json, sys
from playwright.async_api import async_playwright
PORT = 8937
async def main():
    srv = subprocess.Popen(['python3', '/home/claude/tools/serve.py', str(PORT), '/home/claude/gardenofearthlysound'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
    errs = []
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch(executable_path='/usr/bin/google-chrome')
            for vw in [(1280, 900), (390, 844)]:
                pg = await b.new_page(viewport={'width': vw[0], 'height': vw[1]}); pe = []; pg.on('pageerror', lambda e: pe.append(str(e)))
                await pg.goto(f'http://localhost:{PORT}/index.html'); await pg.wait_for_timeout(2500)
                miss = await pg.evaluate("""() => { const q = document.getElementById('q'), res = document.getElementById('res'), A = window.GX.ATLAS, out = [];
                  const cap = k => k.charAt(0).toUpperCase() + k.slice(1), go = v => { q.value = v; q.dispatchEvent(new Event('input')); return [...res.querySelectorAll('button')].map(b => b.firstChild.textContent); };
                  Object.keys(A.glossary).forEach(k => { if (!go(k).includes('❧ ' + cap(k))) out.push('term ' + k); });
                  A.dances.forEach(d => { if (!go(d.dance).includes('¾ ' + d.dance)) out.push('dance ' + d.dance); });
                  if (!go('Dance suite').includes('Dance suite')) out.push('lantern result lost');
                  if (!go('hemiola').some(t => /mentioned in/.test(t))) out.push('mentions row missing for hemiola');
                  q.value = ''; q.dispatchEvent(new Event('input')); return out; }""")
                errs += [f'{vw[0]}: {m}' for m in miss]
                # term page and its links
                await pg.fill('#q', 'sarabande'); await pg.wait_for_timeout(150)
                await pg.click('#res button.gres'); await pg.wait_for_timeout(250)
                t = await pg.inner_text('#sheet')
                for need in ['GLOSSARY', 'Sarabande', 'Listen for', 'Hear it in', 'Found in', 'Dances guide']:
                    if need.lower() not in t.lower(): errs.append(f'{vw[0]}: term page lacks {need}')
                await pg.screenshot(path=f'/home/claude/shots/search/term_{vw[0]}.png')
                await pg.click('#sheet button.tp-x'); await pg.wait_for_timeout(150)
                if await pg.evaluate("() => document.getElementById('sheet').classList.contains('open')"): errs.append(f'{vw[0]}: close button did not close the term page')
                await pg.fill('#q', 'sarabande'); await pg.wait_for_timeout(150); await pg.click('#res button.gres'); await pg.wait_for_timeout(250)
                await pg.click('#sheet button.tp-home'); await pg.wait_for_timeout(900)
                if not await pg.evaluate("() => !!document.querySelector('.gdef') && /slow, serious dance/.test(document.querySelector('.gdef').textContent)"): errs.append(f'{vw[0]}: Found-in did not open the definition in the card')
                await pg.screenshot(path=f'/home/claude/shots/search/card_{vw[0]}.png')
                await pg.keyboard.press('Escape'); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(200)
                # dance result
                await pg.fill('#q', 'sarab'); await pg.wait_for_timeout(150)
                await pg.screenshot(path=f'/home/claude/shots/search/results_{vw[0]}.png')
                await pg.click('#res button.dres'); await pg.wait_for_timeout(300)
                if not await pg.evaluate("() => { const o = document.querySelector('.dn.open .dn-n'); return o && o.textContent === 'Sarabande'; }"): errs.append(f'{vw[0]}: dance row not opened')
                await pg.screenshot(path=f'/home/claude/shots/search/dance_{vw[0]}.png')
                await pg.keyboard.press('Escape'); await pg.wait_for_timeout(200)
                # mentions
                await pg.fill('#q', 'hemiola'); await pg.wait_for_timeout(150)
                await pg.click('#res button.mres'); await pg.wait_for_timeout(250)
                if 'MENTIONED IN' not in await pg.inner_text('#sheet'): errs.append(f'{vw[0]}: mentions sheet not opened')
                await pg.screenshot(path=f'/home/claude/shots/search/mentions_{vw[0]}.png')
                # nothing found still says so
                await pg.keyboard.press('Escape'); await pg.fill('#q', 'zzqxv'); await pg.wait_for_timeout(150)
                if 'Nothing called' not in await pg.inner_text('#res'): errs.append(f'{vw[0]}: empty message missing')
                errs += [f'{vw[0]}: pageerror {e}' for e in pe]
                await pg.close()
            await b.close()
    finally: srv.terminate()
    print('errors', errs)
asyncio.run(main())
