# Weekly Schedule Chatbot (Self-hosted RAG with FAISS + SQLite)

## Mô tả

Weekly Schedule Chatbot là hệ thống chatbot hỏi–đáp về lịch tuần, xây dựng theo kiến trúc RAG (Retrieval-Augmented Generation) và có thể tự lưu trữ hoàn toàn.  
Hệ thống cho phép tải lên file lịch tuần (.docx), tự động trích xuất dữ liệu, sinh embedding, lưu vector vào FAISS và metadata vào SQLite, rồi dùng OpenAI để trả lời chính xác các câu hỏi liên quan đến lịch.

---

## Technical Stack

| Thành phần | Công nghệ | Vai trò |
|-----------|-----------|---------|
| Frontend | HTML / CSS / JavaScript | Giao diện người dùng + giao diện quản trị |
| Backend API | FastAPI (Python) | Server API, ingest, xác thực, truy vấn lịch |
| RAG Engine | OpenAI Embeddings + FAISS | Lưu vector + tìm kiếm Top-K |
| Metadata Store | SQLite | Lưu chunk metadata + log ingest |
| Document Parser | python-docx + regex | Tách bảng lịch từ file .docx |
| Auth | Token-based (custom mini JWT) | Đăng nhập admin + session |
| Storage | FAISS Index + SQLite + uploads/ | Lưu index, metadata và file tải lên |

---

## Cài đặt nhanh

```bash
python -m venv .venv && source .venv/bin/activate   # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt

cp .env.example .env
# Mở .env và điền OPENAI_API_KEY=sk-...

# Chạy Web

uvicorn backend.main:app --reload --port 8000

#Tạo tài khoản, thêm biến sau trong .evn:
ADMIN_USER=...
ADMIN_PASS=...
```

![Weekly Chatbot Screenshot](./doc/OverviewModel.png)