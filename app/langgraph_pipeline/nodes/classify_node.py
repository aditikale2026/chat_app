from app.langgraph_pipeline.state import GraphState
from app.services.llm_service import get__llm

llm=get__llm()
def classify_node(state: GraphState):
    query = state["query"]
    llm=get__llm()
    prompt = f"""
    You are a query classifier.

    Classify the user query into ONE of the following tasks:

    qa -> question answering from documents
    summary -> summarize documents
    chat -> general conversation
    web_search -> needs information from the internet
    Query:
    {query}

    Return ONLY one word:
    qa or summary or chat or web_search
    """

    result = llm.invoke(prompt)

    decision = result.content.strip().lower()

    if "summary" in decision:
        mode = "summary"

    elif "qa" in decision:
        mode= "qa"

    elif "web_search" in decision:
        mode="web_search"
    
    else:
        mode= "chat" 
   
    return {"mode": mode}