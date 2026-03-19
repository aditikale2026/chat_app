from app.langgraph_pipeline.state import GraphState
from app.services.llm_service import get__llm
MAX_CHARS = 80000
llm = get__llm()
def llm_node(state: GraphState):
    
    context = state.get("context")
    query = state.get("query")
    mode = state.get("mode")

    if mode == "summary":
        print(f"Context size: {len(context)} chars | Limit: {MAX_CHARS} chars")

        # If context exceeds safe limit → use map-reduce
        if len(context) > MAX_CHARS:
            print("Context too large → using map-reduce summarization")
            response_text = map_reduce_summary(llm, context)

        # If context is within limit → direct summary
        else:
            print("Context within limit → direct summarization")
            prompt = f"""
            You are a helpful assistant. Read the following text and generate a concise, clear summary:

            Context:
            {context}

            Answer:
            """
            
       
        
    elif mode == "qa":
        prompt = f"""
        You are a helpful assistant. Answer the user's question using ONLY the information provided in the context below.
        If the answer is not found in the context, respond with: "I don't have enough information to answer this question."
        Do not use any outside knowledge or make assumptions beyond what is explicitly stated in the context.

        Context:
        {context}

        Question:
        {query}

        Answer:
        """
        
    elif mode == "web_search":
         prompt = f"""
    You are a helpful assistant. Answer the user's question using the web search 
    results provided below. Cite sources where relevant.

    Web Search Results:
    {context}

    Question:
    {query}

    Answer:
    """
       
    else:
        prompt = f"""
        You are a helpful and friendly assistant.
        
        Question:
        {query}
        
        Answer:
        """
    
    response_obj = llm.invoke(prompt)  # AIMessage object
    response_text = response_obj.content  # string
    
    return {"answer": response_text}