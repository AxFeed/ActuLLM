import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import AzureOpenAI
from database import search, count
from prompting import build_rag_message, build_plain_message, SYSTEM_WITH_RAG, SYSTEM_WITHOUT_RAG
from RSS import ingest

load_dotenv()

app = FastAPI()

azure_client = AzureOpenAI(
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01"),
)

class QuestionRequest(BaseModel):
    question: str
    history: list[dict] = []

def call(messages: list[dict], system: str) -> str:
    full_messages = [{"role": "system", "content": system}] + messages
    response = azure_client.chat.completions.create(
        model=os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        messages=full_messages,
    )
    return response.choices[0].message.content

def ask_with_rag(question: str, history: list[dict] = None) -> tuple[str, list[dict]]:
    articles = search(question)
    user_message = build_rag_message(question, articles)
    messages = list(history or [])
    messages.append({"role": "user", "content": user_message})
    answer = call(messages, SYSTEM_WITH_RAG)
    return answer, articles

def ask_without_rag(question: str, history: list[dict] = None) -> str:
    messages = list(history or [])
    messages.append({"role": "user", "content": build_plain_message(question)})
    return call(messages, SYSTEM_WITHOUT_RAG)

# ── ROUTES ──────────────────────────────────────────────────────────────────

@app.post("/ask/rag")
def route_ask_with_rag(body: QuestionRequest):
    try:
        answer, articles = ask_with_rag(body.question, body.history)
        return {"answer": answer, "articles": articles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask/plain")
def route_ask_without_rag(body: QuestionRequest):
    try:
        answer = ask_without_rag(body.question, body.history)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
def route_ingest(reset: bool = False):
    try:
        isOk = ingest(reset=reset)
        return {"ingest": isOk, "count": count()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {
        "status": "ok",
        "deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        "news_count": count(),
    }