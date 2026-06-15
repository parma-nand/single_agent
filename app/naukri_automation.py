"""
naukri_automation.py
----------------------
Reusable async Playwright functions for Naukri:

  - login(page)
  - search_jobs(page, keyword, location, experience)
  - apply_freshness_filter(page, freshness)
  - get_job_listings(page, max_jobs)  -> structured records for Scout agent
  - apply_to_job(page, job_url, form_answers)  -> STUB, needs Apply selectors

Credentials are read from environment variables (set them in your .env):
    NAUKRI_EMAIL=...
    NAUKRI_PASSWORD=...
"""

import os
import asyncio
from dotenv import load_dotenv
from playwright.async_api import Page
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

NAUKRI_EMAIL = os.getenv("NAUKRI_EMAIL")
NAUKRI_PASSWORD = os.getenv("NAUKRI_PASSWORD")


async def login(page: Page) -> None:
    await page.goto("https://www.naukri.com/nlogin/login")
    await page.click("#login_Layer")
    await page.wait_for_selector("input[id='usernameField']", timeout=10000)
    await page.fill("input[id='usernameField']", NAUKRI_EMAIL)
    await page.fill("input[id='passwordField']", NAUKRI_PASSWORD)
    await page.click("button[type='submit']")
    await page.wait_for_load_state("networkidle", timeout=15000)

    if "login" in page.url.lower():
        raise RuntimeError("Naukri login failed — check credentials or CAPTCHA")


async def search_jobs(page: Page, keyword: str, location: str, experience: str) -> None:
    await page.click("div#ni-gnb-searchbar")
    await asyncio.sleep(1)

    keyword_input = page.locator(
        "input.suggestor-input[placeholder='Enter keyword / designation / companies']"
    )
    await keyword_input.click()
    await keyword_input.fill(keyword)
    await asyncio.sleep(1)

    await page.click("input#experienceDD")
    await asyncio.sleep(1)
    await page.locator(f"ul.dropdown li[title='{experience}']").click()
    await asyncio.sleep(1)

    location_input = page.locator("input.suggestor-input[placeholder='Enter location']")
    await location_input.click()
    await location_input.fill(location)
    await asyncio.sleep(1)

    await page.click("button.nI-gNb-sb__icon-wrapper")
    await page.wait_for_load_state("networkidle", timeout=15000)


async def apply_freshness_filter(page: Page, freshness: str = "Last 1 day") -> None:
    freshness_btn = page.locator("button#filter-freshness")
    await freshness_btn.scroll_into_view_if_needed()
    await asyncio.sleep(1)
    await freshness_btn.click()
    await asyncio.sleep(1)

    await page.wait_for_selector("ul[data-filter-id='freshness']", timeout=5000)
    await page.locator(f"//li[@title='{freshness}']").click()
    await page.wait_for_load_state("networkidle", timeout=15000)


async def get_job_listings(page: Page, max_jobs: int = 10) -> list[dict]:
    """
    Scrapes job cards from the current (filtered) search results page.

    Returns a list of dicts:
        {title, company, location, job_url, easy_apply}

    NOTE: selectors below match Naukri's current job-card layout
    (`div.srp-jobtuple-wrapper`). Verify with Playwright Inspector
    (`playwright codegen naukri.com`) if results come back empty —
    Naukri changes class names periodically.
    """
    cards = page.locator("div.srp-jobtuple-wrapper")
    count = min(await cards.count(), max_jobs)

    listings = []
    for i in range(count):
        card = cards.nth(i)

        title_el = card.locator("a.title")
        title = (await title_el.inner_text()).strip()
        job_url = await title_el.get_attribute("href")

        company = (await card.locator("a.comp-name").inner_text()).strip()

        try:
            location_txt = (await card.locator("span.locWdth").inner_text()).strip()
        except Exception:
            location_txt = ""

        easy_apply = await card.locator("text=Easy Apply").count() > 0

        listings.append(
            {
                "title": title,
                "company": company,
                "location": location_txt,
                "job_url": job_url,
                "easy_apply": easy_apply,
            }
        )

    return listings


async def apply_to_job(page: Page, job_url: str, form_answers: dict) -> dict:
    """
    STUB — opens a job's page and triggers the apply flow.

    Naukri has two apply paths:
      1. "Easy Apply" -> opens a modal on Naukri itself (extra questions,
         resume confirmation, then Submit)
      2. "Apply on company site" -> redirects to an external ATS
         (Lever, Greenhouse, Workday, etc.) — layout differs per company

    To finish this:
      - Run `playwright codegen https://www.naukri.com` while logged in,
        open a real job, click Apply, and record the modal's field
        selectors — map them to keys in `form_answers`.
      - For external ATS redirects, either build per-ATS handlers or
        fall back to "needs_manual_review" (as below) so a human finishes it.
    """
    await page.goto(job_url)
    await page.wait_for_load_state("networkidle", timeout=15000)

    apply_btn = page.locator("button:has-text('Apply')")
    if await apply_btn.count() == 0:
        return {"status": "no_apply_button", "job_url": job_url}

    await apply_btn.first.click()
    await asyncio.sleep(2)

    # TODO: if Easy Apply modal appears, fill its fields from `form_answers`
    # TODO: if redirected to an external ATS, handle per-provider or bail out

    screenshot_path = f"apply_{(job_url or 'job').split('/')[-1][:40]}.png"
    await page.screenshot(path=screenshot_path)

    return {
        "status": "needs_manual_review",
        "job_url": job_url,
        "screenshot_path": screenshot_path,
        "confirmation_message": (
            "Apply flow opened — modal/ATS field selectors still need to be filled in."
        ),
    }