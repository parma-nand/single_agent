"""
Naukri.com Login + Job Search + Freshness Filter Script
Usage:
    pip install playwright
    playwright install chromium
    python naukri_login.py
"""

import asyncio
from playwright.async_api import async_playwright


EMAIL    = "real.me.parma@gmail.com"   # <-- Replace
PASSWORD = "Thakur@123"       # <-- Replace

# Job search config
SEARCH_KEYWORD    = "machine learning engineer or ai engineer or llm engineer or genai engineer"
# <-- Replace
SEARCH_LOCATION   = "Pune"            # <-- Replace
# Options: "Fresher","1 year","2 years","3 years","4 years","5 years" ...
SEARCH_EXPERIENCE = "4 years"         # <-- Replace


async def login_naukri():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context()
        page    = await context.new_page()

        # ── STEP 1: Open Naukri ──────────────────────────────────────────
        print("Opening Naukri.com ...")
        await page.goto("https://www.naukri.com/nlogin/login")

        # ── STEP 2: Click Login button ───────────────────────────────────
        print("Clicking Login button ...")
        await page.click("#login_Layer")

        # ── STEP 3: Fill credentials ─────────────────────────────────────
        await page.wait_for_selector("input[id='usernameField']", timeout=10000)

        print("Entering email ...")
        await page.fill("input[id='usernameField']", EMAIL)

        print("Entering password ...")
        await page.fill("input[id='passwordField']", PASSWORD)

        # ── STEP 4: Submit login ─────────────────────────────────────────
        print("Submitting login ...")
        await page.click("button[type='submit']")

        await page.wait_for_load_state("networkidle", timeout=15000)
        print(f"URL after login: {page.url}")

        if "login" not in page.url.lower():
            print("✅ Login successful!")
        else:
            print("❌ Login failed. Check credentials or CAPTCHA.")
            await browser.close()
            return

        # ── STEP 5: Fill keyword ─────────────────────────────────────────
        print(f"Filling keyword: '{SEARCH_KEYWORD}' ...")
        await page.click("div#ni-gnb-searchbar")
        await asyncio.sleep(1)

        keyword_input = page.locator("input.suggestor-input[placeholder='Enter keyword / designation / companies']")
        await keyword_input.click()
        await keyword_input.fill(SEARCH_KEYWORD)
        await asyncio.sleep(1)

        # ── STEP 6: Select experience from dropdown ──────────────────────
        print(f"Selecting experience: '{SEARCH_EXPERIENCE}' ...")
        await page.click("input#experienceDD")
        await asyncio.sleep(1)

        exp_option = page.locator(f"ul.dropdown li[title='{SEARCH_EXPERIENCE}']")
        await exp_option.click()
        await asyncio.sleep(1)

        # ── STEP 7: Fill location ────────────────────────────────────────
        print(f"Filling location: '{SEARCH_LOCATION}' ...")
        location_input = page.locator("input.suggestor-input[placeholder='Enter location']")
        await location_input.click()
        await location_input.fill(SEARCH_LOCATION)
        await asyncio.sleep(1)

        # ── STEP 8: Click Search ─────────────────────────────────────────
        print("Clicking Search ...")
        await page.click("button.nI-gNb-sb__icon-wrapper")

        await page.wait_for_load_state("networkidle", timeout=15000)
        print(f"Search results URL: {page.url}")

        # ── STEP 9: Scroll down & apply Freshness = Last 1 day ──────────
        print("Scrolling to Freshness filter ...")

        # Scroll until the freshness filter button is visible
        freshness_btn = page.locator("button#filter-freshness")
        await freshness_btn.scroll_into_view_if_needed()
        await asyncio.sleep(1)

        # Click freshness button to open dropdown
        print("Opening Freshness dropdown ...")
        await freshness_btn.click()
        await asyncio.sleep(1)

        # Wait for the dropdown to appear and click "Last 1 day"
        await page.wait_for_selector("ul[data-filter-id='freshness']", timeout=5000)
        last_1_day = page.locator("//li[@title='Last 1 day']")
        await last_1_day.click()    
        print("✅ Freshness filter set to 'Last 1 day'!")

        await page.wait_for_load_state("networkidle", timeout=15000)
        print(f"Filtered results URL: {page.url}")

        # Screenshot of final results
        await page.screenshot(path="naukri_filtered_results.png")
        print("Screenshot saved as naukri_filtered_results.png")

        await asyncio.sleep(5)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(login_naukri())