import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from openai import OpenAI
from pydantic import BaseModel

# .env lives one level above app/, at the project root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI(title="LLM Query API", description="GPT-4o-mini query + form-answer generation")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@app.get("/")
def root():
    return {"message": "Server is up. Try /ask?query=your+question or visit /docs"}


@app.get("/ask")
def ask(query: str = Query(..., description="Your question for the LLM")):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query},
            ],
        )
        answer = response.choices[0].message.content
        return {"query": query, "response": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── New: structured form-answer generation for the Applier agent ──────────────

class FormAnswers(BaseModel):
    cover_letter: str
    why_fit: str
    expected_ctc: str
    notice_period: str


class GenerateFormAnswersRequest(BaseModel):
    job_description: str
    candidate_profile: dict


@app.post("/generate_form_answers", response_model=FormAnswers)
def generate_form_answers(payload: GenerateFormAnswersRequest):
    """
    Drafts application-form content (cover letter, "why fit", expected CTC,
    notice period) tailored to a specific JD + candidate profile.
    Uses OpenAI structured outputs so the response always matches FormAnswers.
    """
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You draft concise, specific job-application answers "
                        "tailored to the given job description and candidate profile. "
                        "Avoid generic filler."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Job Description:\n{payload.job_description}\n\n"
                        f"Candidate Profile:\n{payload.candidate_profile}"
                    ),
                },
            ],
            response_format=FormAnswers,
        )
        return completion.choices[0].message.parsed
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))