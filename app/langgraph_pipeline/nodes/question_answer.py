from app.langgraph_pipeline.state import GraphState
from app.langgraph_pipeline.dependencies import get_service
from app.langgraph_pipeline.nodes.reranker import rerank_chunks  # ✅ reranking

def question_answer(state: GraphState):
    query = state["query"]
    retriever = get_service("retriever")
    vectorstore = get_service("vectorstore")

    active_docs = vectorstore.get_active_docs()
    if not active_docs:
        return {"context": ""}

    doc_id = [active_docs[0].metadata["doc_id"]]

    # ✅ fetch more chunks then rerank
    fetched_context = retriever.fetch(
        query=query,
        fetch_all=False,
        doc_ids=doc_id,
        top_k=10   # fetch 10, rerank to top 3
    )

    print(f"[question_answer] Fetched {len(fetched_context)} chunks")

    #  rerank chunks
    reranked = rerank_chunks(query, fetched_context, top_k=3)

    context = "\n\n".join([doc["content"] for doc in reranked]) if reranked else ""

    if not context:
        return {"context": ""}

    return {"context": context}