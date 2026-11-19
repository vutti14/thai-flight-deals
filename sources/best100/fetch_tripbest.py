import sys, asyncio, json
from playwright.async_api import async_playwright
async def main(urls):
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", headless=True, args=["--no-sandbox","--disable-blink-features=AutomationControlled"])
        ctx = await b.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36", locale="en-US", viewport={"width":1280,"height":900})
        pg = await ctx.new_page()
        for u,out in urls:
            await pg.goto(u, wait_until="domcontentloaded", timeout=60000)
            for _ in range(12):
                await pg.wait_for_timeout(2500)
                if "Challenge" not in await pg.title(): break
            await pg.wait_for_timeout(1500)
            n = await pg.evaluate("document.querySelectorAll('.lazyload').length")
            for i in range(n):
                await pg.evaluate(f"(()=>{{const e=document.querySelectorAll('.lazyload')[{i}]; if(e) e.scrollIntoView({{block:'center'}});}})()")
                await pg.wait_for_timeout(250)
            await pg.wait_for_timeout(1000)
            html = await pg.content(); text = await pg.inner_text("body")
            open(out+".html","w").write(html); open(out+".txt","w").write(text)
            print(out, n, len(html), flush=True)
        await b.close()
a=sys.argv[1:]; asyncio.run(main(list(zip(a[0::2],a[1::2]))))
