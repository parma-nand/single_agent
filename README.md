# Single Agent — Naukri Job Search & Apply Automation

A LangGraph-powered single agent that autonomously logs into Naukri.com, searches for relevant job listings, scores them against a resume, and generates a structured PDF report — all driven by an LLM with tool-use.

---

## 📁 Project Structure

```
single_agent/
│
├── app/
│   ├── apply_job_tool.py       # Tool: applies to a job listing on Naukri via Playwright
│   ├── llm_interaction.py      # LangGraph agent core — LLM reasoning + tool orchestration
│   ├── naukri_automation.py    # Playwright automation: login, search, scrape job listings
│   ├── pdf-generator.py        # Generates a structured PDF report of job results (ReportLab)
│   ├── scrapyex.py             # Scrapy/async scraping utilities for extracting job data
│   └── test.py                 # Quick smoke tests / manual runner
│
├── .gitignore
├── README.md
├── requirements.txt
└── resume_report.pdf           # Sample output — LLM-generated resume intelligence report
```

---

## 🤖 What the Agent Does

```
Agent Start
    │
    ▼
naukri_automation.py   →  Launches browser (async Playwright), logs into Naukri.com,
                           navigates to job search with configured keywords & filters
    │
    ▼
scrapyex.py            →  Scrapes job listing cards (title, company, experience, skills,
                           location, apply URL) from search results pages
    │
    ▼
llm_interaction.py     →  LangGraph ReAct agent reasons over listings, calls tools:
                           - Score listing against resume
                           - Decide to apply or skip
                           - Extract structured data per job
    │
    ▼
apply_job_tool.py      →  Tool invoked by agent to click "Apply" on selected listings
                           via Playwright browser automation
    │
    ▼
pdf-generator.py       →  Generates a PDF report (via ReportLab) summarising:
                           - Jobs applied to
                           - Match scores
                           - Skills gap analysis
```

---

## 🚀 Getting Started

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set environment variables
Create a `.env` file at the project root:
```env
NAUKRI_EMAIL=your_email@example.com
NAUKRI_PASSWORD=your_password
OPENAI_API_KEY=sk-...
```

### 3. Run the agent
```bash
python app/llm_interaction.py
```

Or use the test runner:
```bash
python app/test.py
```

---

## 🔑 Key Files Explained

### `naukri_automation.py`
Handles all browser interactions with Naukri.com using **async Playwright**:
- Login with credentials
- Keyword + location + experience-level search
- Navigating paginated results

### `scrapyex.py`
Async scraping layer that extracts structured job data from Naukri listing pages — title, company, required experience, key skills, and direct apply URL.

### `llm_interaction.py`
The **LangGraph ReAct agent** — the brain of the system:
- Receives scraped job listings as context
- Uses OpenAI tool-calling to invoke `apply_job_tool` selectively
- Scores each listing against a resume profile
- Maintains agent state across tool calls

### `apply_job_tool.py`
A LangGraph-compatible **tool** that accepts a job URL and uses Playwright to automate the application click flow on Naukri.

### `pdf-generator.py`
Uses **ReportLab** to produce a formatted PDF report (`resume_report.pdf`) containing:
- Applied jobs list with company, role, and match score
- Skills gap summary
- Timestamp and run metadata

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent Framework | LangGraph (ReAct pattern) |
| LLM | OpenAI GPT-4o-mini |
| Browser Automation | async Playwright |
| Web Scraping | Scrapy / async HTTP |
| PDF Generation | ReportLab |
| Language | Python 3.11 |

---

## 📌 Roadmap

This single-agent is **Phase 1** of a larger multi-agent pipeline:

```
Phase 1 (current) — Single Agent
    └── Login → Search → Score → Apply → PDF Report

Phase 2 (planned) — Multi-Agent (LangGraph)
    ├── Planner Agent    — decides search strategy
    ├── Scraper Agent    — bulk scraping via Scrapy
    ├── Applier Agent    — applies to shortlisted jobs
    └── Tracker Agent    — logs status to DB / dashboard
```

---

## ⚠️ Notes

- Use responsibly — bulk automated applying may trigger Naukri rate limits or CAPTCHA.
- Playwright requires browsers installed: `playwright install chromium`
- Agent runs headlessly by default; set `headless=False` in `naukri_automation.py` to watch it run.
