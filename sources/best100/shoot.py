import sys, asyncio
from playwright.async_api import async_playwright
async def main(url, out, w, h, full):
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", headless=True, args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": w, "height": h}, device_scale_factor=2 if w < 500 else 1)
        await pg.goto(url, wait_until="networkidle"); await pg.wait_for_timeout(800)
        await pg.screenshot(path=out, full_page=full); await b.close()
a = sys.argv; asyncio.run(main(a[1], a[2], int(a[3]), int(a[4]), a[5] == "1"))
