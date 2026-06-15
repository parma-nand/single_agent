"""
apply_job_tool.py
------------------
LangGraph tool for the "Applier" agent.

- Calls the FastAPI LLM service's /generate_form_answers endpoint (GPT-4o-mini)
- Pauses for human review (interrupt) before triggering the apply flow
- Uses naukri_automation.py (Playwright) to open the job and trigger Apply

Env vars expected:
    LLM_SERVICE_URL=http://localhost:8000   (default if unset)
    NAUKRI_EMAIL, NAUKRI_PASSWORD           (used inside naukri_automation.login)
"""

import os
from typing import Union

import httpx
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langgraph.types import interrupt
from playwright.async_api import async_playwright

from naukri_automation import login, apply_to_job

LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://localhost:8000")


class ApplyJobInput(BaseModel):
    job_url: str = Field(..., description="Direct apply URL for the job posting")
    job_title: str = Field(..., description="Job title, e.g. 'GenAI Engineer'")
    company: str = Field(..., description="Company name")
    job_description: str = Field(..., description="Full JD text — used to tailor answers")
    candidate_profile: dict = Field(
        ..., description="Structured profile data: skills, experience, CTC, notice period, etc."
    )


@tool("apply_to_job", args_schema=ApplyJobInput)
async def apply_to_job_tool(
    job_url: str,
    job_title: str,
    company: str,
    job_description: str,
    candidate_profile: dict,
) -> dict:
    """
    End-to-end job application:
      1. Calls the LLM service to draft cover letter / form answers
      2. Pauses for human review before anything is opened/submitted
      3. Uses Playwright (naukri_automation) to open the job and trigger Apply
    """

    # 1) Get drafted answers from the LLM service ---------------------------
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{LLM_SERVICE_URL}/generate_form_answers",
            json={"job_description": job_description, "candidate_profile": candidate_profile},
        )
        resp.raise_for_status()
        form_answers = resp.json()

    # 2) Human-in-the-loop checkpoint ----------------------------------------
    decision: Union[bool, dict, None] = interrupt(
        {
            "type": "review_application",
            "job_title": job_title,
            "company": company,
            "form_answers": form_answers,
            "message": "Review the drafted answers before I open the apply flow.",
        }
    )

    if decision is False or decision is None:
        return {"status": "skipped", "job_title": job_title, "company": company}

    if isinstance(decision, dict):
        form_answers.update(decision)

    # 3) Playwright: login + open job + trigger apply -------------------------
    # NOTE: launching a fresh browser per application is simple but slow.
    # Once apply_to_job() is fully implemented, consider keeping a single
    # logged-in browser/context alive across multiple tool calls.
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context()
        page = await context.new_page()

        await login(page)
        result = await apply_to_job(page, job_url, form_answers)

        await browser.close()

    return {
        "status": result.get("status", "unknown"),
        "job_title": job_title,
        "company": company,
        "screenshot_path": result.get("screenshot_path"),
        "confirmation_message": result.get("confirmation_message"),
    }