"""
test_apply.py
---------------
Minimal LangGraph runner to test apply_to_job_tool end-to-end.

Prereqs:
  - Terminal 1: `uvicorn llm_interaction:app --reload --port 8000`
  - .env has OPENAI_API_KEY, NAUKRI_EMAIL, NAUKRI_PASSWORD, LLM_SERVICE_URL
"""

from langgraph.prebuilt import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from langchain_openai import ChatOpenAI

from apply_job_tool import apply_to_job_tool

# This LLM is the *agent's own reasoning model* — separate from the
# gpt-4o-mini call that happens inside apply_to_job_tool via the FastAPI service.
llm = ChatOpenAI(model="gpt-4o-mini")

agent = create_agent(llm, tools=[apply_to_job_tool], checkpointer=MemorySaver())

config = {"configurable": {"thread_id": "test-1"}}

job_description = "GenAI Engineer — RAG pipelines, LangGraph, LLM fine-tuning, Python, FastAPI. 3-5 yrs exp."
candidate_profile = {
    "current_role": "Associate Consultant (GenAI Engineer), Capgemini",
    "experience_years": 4,
    "skills": ["LangGraph", "RAG", "LangChain", "FastAPI", "Python", "Qdrant"],
    "expected_ctc": "18 LPA",
    "notice_period": "30 days",
}

prompt = (
    f"Apply to this job: GenAI Engineer at ExampleCorp, "
    f"URL https://www.naukri.com/job-listings-example, "
    f"JD: {job_description}, "
    f"my profile: {candidate_profile}"
)

# Step 1 — agent decides to call apply_to_job; execution pauses at interrupt()
result = agent.invoke({"messages": [("user", prompt)]}, config=config)
print("PAUSED FOR REVIEW:")
print(result["__interrupt__"])

# Step 2 — after reviewing form_answers above, resume:
#   True              -> approve as-is
#   {"cover_letter": "..."} -> approve with edits
#   False             -> skip this application
result = agent.invoke(Command(resume=True), config=config)
print("FINAL RESULT:")
print(result["messages"][-1].content)