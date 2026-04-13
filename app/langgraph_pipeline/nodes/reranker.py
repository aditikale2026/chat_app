from app.services.llm_service import get__llm
from typing import List, Dict, Any

def rerank_chunks(query: str, chunks: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
    """Rerank retrieved chunks by relevance to query."""

    if not chunks or len(chunks) <= top_k:
        return chunks

    llm = get__llm(temperature=0.0)

    # score each chunk
    scored = []
    for i, chunk in enumerate(chunks):
        prompt = f"""
Query: {query}
Chunk: {chunk['content'][:500]}

How relevant is this chunk to the query?
Reply with only a number from 1 to 10.
"""
        result = llm.invoke(prompt)
        try:
            score = float(result.content.strip())
        except:
            score = 5.0

        scored.append((score, chunk))
        print(f"[reranker] Chunk {i+1} score: {score}")

    # sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)

    # return top_k
    reranked = [chunk for _, chunk in scored[:top_k]]
    print(f"[reranker] Kept {len(reranked)} of {len(chunks)} chunks")
    return reranked