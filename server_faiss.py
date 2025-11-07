# server_faiss.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag.service import Ask, ask as rag_ask

app = FastAPI(title="TMU Weekly Bot (server_faiss)")

class AskIn(BaseModel):
    question: str

@app.post("/ask")
def api_ask(req: AskIn):
    try:
        return rag_ask(Ask(question=req.question))  # trả về dict {"answer": ..., "hits": ...}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"internal_error: {e}")