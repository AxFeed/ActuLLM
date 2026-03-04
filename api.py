import os
import requests
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
    provider: str = "ollama"  # "ollama" ou "azure"

def call(messages: list[dict], system: str, provider: str) -> str:
    full_messages = [{"role": "system", "content": system}] + messages

    if provider == "azure":
        response = azure_client.chat.completions.create(
            model=os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
            messages=full_messages,
        )
        return response.choices[0].message.content

    else:
        payload = {
            "model": os.environ.get("OLLAMA_MODEL"),
            "messages": full_messages,
            "stream": False,
        }
        response = requests.post(f"{os.environ.get('OLLAMA_URL')}/api/chat", json=payload)
        response.raise_for_status()
        return response.json()["message"]["content"]


def ask_with_rag(question: str, history: list[dict] = None, provider: str = "ollama") -> tuple[str, list[dict]]:
    articles = search(question)
    user_message = build_rag_message(question, articles)
    messages = list(history or [])
    messages.append({"role": "user", "content": user_message})
    answer = call(messages, SYSTEM_WITH_RAG, provider)
    return answer, articles


def ask_without_rag(question: str, history: list[dict] = None, provider: str = "ollama") -> str:
    messages = list(history or [])
    messages.append({"role": "user", "content": build_plain_message(question)})
    return call(messages, SYSTEM_WITHOUT_RAG, provider)

# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.post("/ask/rag")
def route_ask_with_rag(body: QuestionRequest):
    try:
        answer, articles = ask_with_rag(body.question, body.history, body.provider)
        return {"answer": answer, "articles": articles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask/plain")
def route_ask_without_rag(body: QuestionRequest):
    try:
        answer = ask_without_rag(body.question, body.history, body.provider)
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
        "model": os.environ.get("OLLAMA_MODEL"),
        "news count": count(),
    }