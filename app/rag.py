import os
from pathlib import Path
import httpx
try:
    import chromadb
    from sentence_transformers import SentenceTransformer
except Exception:
    chromadb = None
    SentenceTransformer = None

ROOT = Path(__file__).resolve().parents[2]
CHROMA_DIR = ROOT / "rag" / "chroma"

_embedder = None
_client = None
_collection = None

def get_collection():
    global _embedder, _client, _collection
    if chromadb is None or SentenceTransformer is None:
        return None
    if _client is None:
        _client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _collection = _client.get_or_create_collection("mentzer_knowledge")
    if _embedder is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _collection

def retrieve(query, k=5):
    col = get_collection()
    if not col or col.count() == 0:
        return []
    emb = _embedder.encode([query]).tolist()
    res = col.query(query_embeddings=emb, n_results=k)
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    return [{"text":d,"meta":m or {}} for d,m in zip(docs,metas)]

async def answer(query):
    chunks = retrieve(query)
    context = "\n\n".join(f"SOURCE: {c['meta'].get('source','Mentzer material')}\n{c['text']}" for c in chunks)
    api_key = os.getenv("AI_API_KEY")
    base = os.getenv("AI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("AI_MODEL", "gpt-4.1-mini")
    if api_key and context:
        system = ("You are Be2Gen2, an evidence-aware bodybuilding coach. "
                  "Use the retrieved Mentzer source material as the basis for historical Mentzer claims. "
                  "Clearly distinguish source-derived Mentzer recommendations from calculations or modern safety context. "
                  "Do not diagnose medical conditions. Never invent citations.")
        payload={"model":model,"messages":[{"role":"system","content":system},{"role":"user","content":f"Retrieved material:\n{context}\n\nQuestion: {query}"}],"temperature":0.2}
        async with httpx.AsyncClient(timeout=45) as client:
            r=await client.post(f"{base}/chat/completions",headers={"Authorization":f"Bearer {api_key}"},json=payload)
            r.raise_for_status()
            text=r.json()["choices"][0]["message"]["content"]
        return {"answer":text,"sources":[c["meta"] for c in chunks]}
    if chunks:
        return {"answer":"I found relevant material in the Mentzer knowledge base. Add an AI_API_KEY to enable synthesized RAG answers.\n\n" + chunks[0]["text"][:1800],"sources":[c["meta"] for c in chunks]}
    return {"answer":"The RAG knowledge base is not indexed yet. Run `python ../rag/ingest.py` from the backend directory after placing the supplied PDFs in rag/source/.","sources":[]}
