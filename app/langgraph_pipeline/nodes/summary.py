from app.langgraph_pipeline.state import GraphState
# CHANGED: import get_service to fetch retriever and vectorstore from registry
from app.langgraph_pipeline.dependencies import get_service

def summary(state: GraphState):
    print("summary node----running")
    query = state["query"]

    # CHANGED: retriever and vectorstore now fetched from registry, not from state
    retriever = get_service("retriever")
    vectorstore = get_service("vectorstore")

    # CHANGED: active_doc fetched directly from vectorstore via registry
    active_docs = vectorstore.get_active_docs()
    if not active_docs:
        return {"context": ""}

    current_doc = active_docs[0].metadata["doc_id"]
    print(f"Doc id = {current_doc}")

    try:
        print("i am inside try")
        fetched_context = retriever.fetch(
            query=query,
            fetch_all=True,
            doc_ids=[current_doc],   # CHANGED: wrapped in list — fetch() expects List[str]
            threshold=0
        )
    except Exception as e:
        print(f"exception = {e}")
        return {"context": ""}

    context = "\n\n".join([doc["content"] for doc in fetched_context]) if fetched_context else ""
    print(f"context= {context}")

    if not context:
        return {"context": ""}

    # CHANGED: removed **state spread — only return what changed
    return {"context": context}