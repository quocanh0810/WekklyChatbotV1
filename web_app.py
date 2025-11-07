# web_app.py
import os, traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Trì hoãn import service để tránh crash khi kho chưa sẵn sàng
RAGAsk = None
rag_ask = None
rag_import_error = None

def _lazy_import_rag():
    global RAGAsk, rag_ask, rag_import_error
    if RAGAsk and rag_ask:
        return
    try:
        from rag.service import Ask as _Ask, ask as _ask  # noqa
        RAGAsk = _Ask
        rag_ask = _ask
        rag_import_error = None
    except Exception as e:
        rag_import_error = f"{e}\n{traceback.format_exc()}"

app = FastAPI(title="TMU Weekly Bot", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static
if not os.path.exists("web"):
    os.makedirs("web", exist_ok=True)

app.mount("/assets", StaticFiles(directory="web", html=False), name="assets")

@app.get("/")
def serve_index():
    index_path = os.path.join("web", "index.html")
    if not os.path.exists(index_path):
        return {"message": "Put your frontend in ./web (index.html, main.js, style.css)."}
    return FileResponse(index_path)

# ===== Health & Debug =====
@app.get("/health")
def health():
    _lazy_import_rag()
    if rag_import_error:
        return {"status": "degraded", "detail": "rag not ready", "error": rag_import_error}
    return {"status": "ok"}

# ===== API =====
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str

@app.post("/api/chat", response_model=ChatResponse)
def api_chat(req: ChatRequest):
    _lazy_import_rag()
    if rag_import_error:
        raise HTTPException(status_code=500, detail=f"RAG init failed: {rag_import_error}")

    msg = (req.message or "").strip()
    if not msg:
        raise HTTPException(status_code=400, detail="message is empty")

    try:
        res = rag_ask(RAGAsk(question=msg))  # dict {"answer": ..., "hits": ...}
        answer = (res.get("answer") or "").strip()
        if not answer:
            answer = "Mình không tìm thấy thông tin trong lịch tuần này."
        return ChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"internal_error: {e}")

# (Tùy chọn) Tương thích ngược với client_cli.py cũ (POST /ask)
class AskIn(BaseModel):
    question: str

@app.post("/ask")
def api_ask_compat(req: AskIn):
    _lazy_import_rag()
    if rag_import_error:
        raise HTTPException(status_code=500, detail=f"RAG init failed: {rag_import_error}")
    try:
        return rag_ask(RAGAsk(question=req.question))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"internal_error: {e}")