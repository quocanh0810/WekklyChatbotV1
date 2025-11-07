import argparse, os, json, sqlite3, faiss, numpy as np
from sentence_transformers import SentenceTransformer

def chunk_text_fields(ev):
    fields = []
    for k in ("date","dow","start","end","location","participants","title"):
        if ev.get(k):
            fields.append(f"{k}: {ev[k]}")
    if ev.get("raw"):
        fields.append(f"raw: {ev['raw']}")
    return "\n".join(fields)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--jsonl", required=True, help="events jsonl from parse_schedule.py")
    ap.add_argument("--store-dir", required=True, help="directory for FAISS/SQLite")
    ap.add_argument("--local-emb", default="sentence-transformers/all-MiniLM-L6-v2")
    args = ap.parse_args()

    os.makedirs(args.store_dir, exist_ok=True)
    sqlite_path = os.path.join(args.store_dir, "chunks.sqlite")
    faiss_path = os.path.join(args.store_dir, "index.faiss")

    # Load events
    events = []
    with open(args.jsonl, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                events.append(json.loads(line))

    if not events:
        raise SystemExit("No events found in JSONL. Check parse step.")

    texts = [chunk_text_fields(ev) for ev in events]

    # Embedding bằng model local
    model = SentenceTransformer(args.local_emb)
    embs = model.encode(texts, normalize_embeddings=True)
    embs = np.asarray(embs, dtype="float32")

    # FAISS index
    index = faiss.IndexFlatIP(embs.shape[1])
    index.add(embs)
    faiss.write_index(index, faiss_path)

    # Save metadata to sqlite
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS chunks(
        id INTEGER PRIMARY KEY,
        text TEXT,
        date TEXT, dow TEXT, start TEXT, end TEXT,
        location TEXT, participants TEXT, title TEXT, raw TEXT
    )""")
    cur.execute("DELETE FROM chunks")
    for i, ev in enumerate(events):
        cur.execute("""INSERT INTO chunks(id,text,date,dow,start,end,location,participants,title,raw)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (i, texts[i], ev.get("date"), ev.get("dow"), ev.get("start"), ev.get("end"),
             ev.get("location"), ev.get("participants"), ev.get("title"), ev.get("raw")))
    conn.commit()
    conn.close()

    print("[OK] Stored", len(events), "chunks")
    print("[OK] FAISS:", faiss_path)
    print("[OK] SQLite:", sqlite_path)