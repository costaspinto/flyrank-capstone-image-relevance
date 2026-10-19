import re, math
from collections import Counter
from app.config import settings
STOP = {"a","an","the","and","or","of","in","on","to","for","with","is","are","this","that","about","how","what","why","from"}
def tokens(text):
    return [t for t in re.findall(r"[a-z0-9]+", (text or "").lower()) if t not in STOP]
def local_similarity(a, b):
    aa, bb = Counter(tokens(a)), Counter(tokens(b))
    if not aa or not bb: return 0.0
    vocab = set(aa) | set(bb)
    dot = sum(aa[t]*bb[t] for t in vocab)
    na = math.sqrt(sum(v*v for v in aa.values())); nb = math.sqrt(sum(v*v for v in bb.values()))
    score = dot/(na*nb) if na and nb else 0.0
    ta, tb = set(tokens(a)), set(tokens(b))
    for group in [{"fox","vulpes"},{"wolf","wolves"},{"dog","canine"},{"bear","ursine"},{"deer","stag","doe"}]:
        if ta & group and tb & group: score = max(score, 0.72)
    return min(1.0, score)
async def similarity(a, b):
    if settings.embedding_provider.lower() == "ollama":
        import httpx
        async with httpx.AsyncClient(timeout=45) as client:
            r1 = await client.post(f"{settings.ollama_base_url.rstrip('/')}/api/embeddings", json={"model":settings.ollama_embedding_model,"prompt":a})
            r1.raise_for_status()
            r2 = await client.post(f"{settings.ollama_base_url.rstrip('/')}/api/embeddings", json={"model":settings.ollama_embedding_model,"prompt":b})
            r2.raise_for_status()
            va, vb = r1.json()["embedding"], r2.json()["embedding"]
        dot=sum(x*y for x,y in zip(va,vb)); na=math.sqrt(sum(x*x for x in va)); nb=math.sqrt(sum(y*y for y in vb))
        return (dot/(na*nb) if na and nb else 0.0), "ollama"
    return local_similarity(a,b), "local-lexical"
