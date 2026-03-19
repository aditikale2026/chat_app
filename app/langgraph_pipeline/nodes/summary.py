from app.langgraph_pipeline.state import GraphState
from app.services.retrieval import RAGRetriver
from app.services.vector_store import Storing
from fastapi import Request
# vectorstore = Storing()
# retriever = RAGRetriver(vector_store=vectorstore)

def summary(state: GraphState):
    print("summary node----running")
    query=state["query"]
    store=state.get("store")
    active_doc=state.get("active_doc")
    retriever=state.get("retriever")
    current_doc =active_doc[0].metadata['doc_id']
    print(f"Doc id = {current_doc}")
    if not current_doc:
        return {"context": ""}
    # current_doc.append(doc_id[-1])
    fetch_all=True
    try:
        
        print("i am inside try")
        fetched_context =retriever.fetch(
        query=query,
        fetch_all=True,
        doc_ids=current_doc ,
        threshold=0              
)
    except Exception as e:
        print(f"exception = {e}")   
        
        
    context = "\n\n".join([doc["content"] for doc in fetched_context]) if fetched_context else ""
    
    print(f"context= {context}")
    if not context:
        return {"context": ""}

    return {
        **state,
        "context": context}
