import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg = await b.new_page(viewport={'width':900,'height':1300})
        html=open('/home/claude/shots/journey/sheet.html').read().replace('https://shmungfroi.github.io/gardenofearthlysound/fonts/','file:///home/claude/gardenofearthlysound/fonts/').replace('http://localhost:8918/fonts/','file:///home/claude/gardenofearthlysound/fonts/')
        open('/tmp/sheet_local.html','w').write(html); await pg.goto('file:///tmp/sheet_local.html'); await pg.wait_for_timeout(800)
        await pg.screenshot(path='/home/claude/shots/journey/8_sheet.png', full_page=True)
        await pg.pdf(path='/home/claude/shots/journey/journey_sheet.pdf', format='A4', print_background=True); await b.close()
asyncio.run(main())
