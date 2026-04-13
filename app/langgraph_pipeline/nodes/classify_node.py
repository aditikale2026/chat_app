from app.langgraph_pipeline.state import GraphState
from app.services.llm_service import get__llm
from app.langgraph_pipeline.nodes.query_rewriter import rewrite_query
from langchain_core.messages import HumanMessage, AIMessage

def classify_node(state: GraphState):
    query = state["query"]
    messages = state.get("messages", [])
    llm = get__llm(temperature=0.0)  # zero temp for classification

    #  rewrite query first
    rewritten_query = rewrite_query(query, messages)

    # format history
    history = ""
    if messages:
        formatted = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                formatted.append(f"User: {msg.content}")
            elif isinstance(msg, AIMessage):
                formatted.append(f"Assistant: {msg.content}")
        history = "\n".join(formatted)

    prompt = f"""
You are a query classification engine.

Previous conversation:
{history if history else "No previous conversation."}

Available pipelines:
1. qa          - specific question about document content
2. summary     - wants overview or summary of document
3. web_search  - needs current or real-time information
4. chat        - general conversation or follow up questions

Current Query: {rewritten_query}

Instructions:
- If query refers to previous conversation topic → chat
- Return ONLY one word: qa, summary, web_search, chat

Classification:
"""

    result = llm.invoke(prompt)
    decision = result.content.strip().lower()

    if "summary" in decision:
        mode = "summary"
    elif "qa" in decision:
        mode = "qa"
    elif "web_search" in decision:
        mode = "web_search"
    else:
        mode = "chat"

    print(f"[classify_node] '{query}' → '{rewritten_query}' → mode: '{mode}'")

    # save rewritten query into state
    return {"mode": mode, "query": rewritten_query}