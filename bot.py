import asyncio
import os
import random
import time
from playwright.async_api import async_playwright
import playwright_stealth

# --- ANSI COLOR PALETTE ---
G, R, C, W, B, RST = "\033[1;32m", "\033[1;31m", "\033[1;36m", "\033[1;37m", "\033[1m", "\033[0m"

# --- CONFIGURATION ---
MAX_CONCURRENT_TASKS = 4  # Adjust based on your RAM
AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
]

def banner():
    os.system('clear')
    print(f"""{G}
  ██╗  ██╗██╗████████╗     ███╗   ███╗ █████╗ ██╗██╗     
  ██║  ██║██║╚══██╔══╝     ████╗ ████║██╔══██╗██║██║     
  ███████║██║   ██║  █████╗██╔████╔██║███████║██║██║     
  ██╔══██║██║   ██║  ╚════╝██║╚██╔╝██║██╔══██║██║██║     
  ██║  ██║██║   ██║        ██║ ╚═╝ ██║██║  ██║██║███████╗
  ╚═╝  ╚═╝╚═╝   ╚═╝        ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚══════╝
           {W}VERSION: 3.0 | {G}MADE BY: CXBED{RST}""")
    print(f"{W}{'-' * 55}{RST}")

async def sign_up(semaphore, context, url, email):
    async with semaphore:
        page = await context.new_page()
        try:
            # Apply Stealth for every new tab
            try:
                await playwright_stealth.stealth_async(page)
            except: pass
            
            print(f"{B}[{W}PROCESS{RST}{B}] -> {W}{url[:50]}...{RST}")
            
            # Navigate
            await page.goto(url, timeout=35000, wait_until="domcontentloaded")
            
            # Handle Cookie Banners/Popups
            for btn_text in ["Accept", "Agree", "Allow", "OK", "Dismiss", "Close"]:
                try:
                    btn = page.get_by_role("button", name=btn_text, exact=False)
                    if await btn.is_visible(timeout=500):
                        await btn.click()
                except: pass

            # Locate Email Input
            selectors = [
                'input[type="email"]', 'input[name*="email"]', 
                '#email', '[placeholder*="email" i]', '[aria-label*="email" i]'
            ]
            
            target_field = None
            for s in selectors:
                try:
                    el = page.locator(s).first
                    if await el.is_visible(timeout=2000):
                        target_field = el
                        break
                except: continue

            if target_field:
                await target_field.scroll_into_view_if_needed()
                # Human-like typing
                await target_field.type(email, delay=random.randint(50, 150))
                await page.keyboard.press("Enter")
                
                # Wait for response and log success
                await asyncio.sleep(4)
                with open("results.txt", "a") as log:
                    log.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] SUCCESS: {url}\n")
                
                print(f"{B}[{G} SUCCESS {RST}{B}] FORM SUBMITTED: {url[:30]}...")
            else:
                print(f"{B}[{R} FAILED  {RST}{B}] NO FIELD: {url[:30]}...")
                
        except Exception:
            print(f"{B}[{R} ERROR   {RST}{B}] TIMEOUT: {url[:30]}...")
        finally:
            await page.close()

async def main():
    banner()
    print(f"{B}[{G}?{RST}{B}] TARGET EMAIL:{RST}")
    target_email = input(f"{G}>> {RST}").strip()
    
    if "@" not in target_email:
        print(f"{R}[!] INVALID EMAIL FORMAT{RST}")
        return

    print(f"{B}[{G}?{RST}{B}] RUN IN BACKGROUND? (y/n):{RST}")
    mode = input(f"{G}>> {RST}").lower()
    headless_mode = True if mode == 'y' else False

    async with async_playwright() as p:
        # Launching Kali's Chromium
        browser = await p.chromium.launch(executable_path="/usr/bin/chromium", headless=headless_mode)
        
        # Setup Browser Context with Random Agent
        context = await browser.new_context(
            user_agent=random.choice(AGENTS),
            viewport={'width': 1280, 'height': 720}
        )

        try:
            with open("targets.txt", "r") as f:
                urls = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"{R}[!] targets.txt NOT FOUND!{RST}")
            return

        print(f"{B}[{G}*{RST}{B}] LOADED {C}{len(urls)}{RST}{B} TARGETS. STARTING ENGINE...{RST}\n")

        # Set the concurrency limit
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)
        
        tasks = [sign_up(semaphore, context, url, target_email) for url in urls]
        await asyncio.gather(*tasks)

        print(f"\n{W}{'-' * 55}{RST}")
        print(f"{B}[{G} FINISHED {RST}{B}] RESULTS SAVED TO results.txt{RST}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

