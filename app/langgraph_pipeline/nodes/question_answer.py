from app.langgraph_pipeline.state import GraphState
# CHANGED: import get_service to fetch retriever from registry instead of state
from app.langgraph_pipeline.dependencies import get_service

def question_answer(state: GraphState):
    query = state["query"]

    # CHANGED: retriever now fetched from registry, not from state
    # state no longer holds non-serializable objects
    retriever = get_service("retriever")
    vectorstore = get_service("vectorstore")

    # CHANGED: doc_id now dynamically fetched from active_doc instead of hardcoded
    active_docs = vectorstore.get_active_docs()
    if not active_docs:
        return {"context": ""}

    doc_id = [active_docs[0].metadata["doc_id"]]

    fetched_context = retriever.fetch(
        query=query,
        fetch_all=False,
        doc_ids=doc_id,
        top_k=3
    )

    print(f"fetched_context -- {fetched_context}")
    context = "\n\n".join([doc["content"] for doc in fetched_context]) if fetched_context else ""

    if not context:
        return {"context": ""}

    print(f"context - {context}")
    return {"context": context}