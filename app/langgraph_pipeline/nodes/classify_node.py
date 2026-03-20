from app.langgraph_pipeline.state import GraphState
from app.services.llm_service import get__llm

# CHANGED: removed duplicate llm init at module level — only init inside function
def classify_node(state: GraphState):
    query = state["query"]
    llm = get__llm()

    # CHANGED: stronger prompt with examples and stricter output rules
    prompt = f"""
You are a query classification engine for a document-based AI chat application.
Your job is to route the user's query to the correct processing pipeline.

Available pipelines and when to use them:

1. qa
   - User asks a specific question about document content
   - Examples: "What is the conclusion of the report?", 
               "Who is mentioned in chapter 3?",
               "What are the key findings?"

2. summary  
   - User wants an overview or summary of a document
   - Examples: "Summarize this document", 
               "Give me an overview of the PDF",
               "What is this document about?",
               "TLDR of the file"

3. web_search
   - Query requires current/real-time information not found in documents
   - Examples: "What is the latest news about AI?",
               "What is today's stock price of Tesla?",
               "Who won the election?"

4. chat
   - General conversation, greetings, or unrelated questions
   - Examples: "Hello", "How are you?", 
               "What can you do?", "Tell me a joke"

User Query:
{query}

Instructions:
- Return ONLY one word from: qa, summary, web_search, chat
- Do NOT explain your choice
- Do NOT return anything else
- If unsure between qa and summary, prefer qa

Classification:
"""

    result = llm.invoke(prompt)
    decision = result.content.strip().lower()

    # CHANGED: more precise matching — check exact word first, then fallback to substring
    if decision == "summary" or "summary" in decision:
        mode = "summary"
    elif decision == "qa" or "qa" in decision:
        mode = "qa"
    elif decision == "web_search" or "web_search" in decision:
        mode = "web_search"
    elif decision == "chat" or "chat" in decision:
        mode = "chat"
    else:
        # CHANGED: added fallback log so you know when LLM returned unexpected output
        print(f"[classify_node] Unexpected classification: '{decision}' → defaulting to 'chat'")
        mode = "chat"

    print(f"[classify_node] Query: '{query}' → Mode: '{mode}'")
    return {"mode": mode}