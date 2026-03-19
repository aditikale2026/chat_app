from app.langgraph_pipeline.state import GraphState
from app.services.retrieval import RAGRetriver
from app.services.vector_store import Storing
from fastapi import Request

# vectorstore = Storing()
# retriever = RAGRetriver(vector_store=vectorstore)
def question_answer(state: GraphState):
    query = state["query"]
    retriever =state.get("retriever")
    # doc_id = state.get("doc_id")
    doc_id=["a5394101-9863-446e-a8b1-9f70cc70f910"]
    if not doc_id:
        return {"context": ""}
    # answer = llm_call.rag_simple(query, retriever)
    fetch_all=False
    # fetched_context = retriever.fetch(query, doc_id, fetch_all,top_k =3)
    fetched_context = retriever.fetch(
    query=query,
    fetch_all=False,
    doc_ids=doc_id,
    top_k=3
)   
    print(f"fetched_context -- {fetched_context}")
    context = "\n\n".join([doc["content"] for doc in fetched_context]) if fetched_context else ""
    if not context:
        return {"context":""}
    print(f"context - {context}")
    return {"context": context}