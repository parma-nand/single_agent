import os
from fastapi import FastAPI, Query, HTTPException
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# .env lives one level above app/, at the project root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


app = FastAPI(title="LLM Query API", description="Send a query, get a response from GPT-4o-mini")

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