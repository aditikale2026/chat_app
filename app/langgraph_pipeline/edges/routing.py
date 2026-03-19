from app.langgraph_pipeline.state import GraphState

def route_request(state: GraphState):
    # print("routeee",state["mode"])
    if state["mode"] == "summary":
        return "summary"
    elif state["mode"] == "qa":
        return "question_answer"
    elif state["mode"]== "web_search":
        return "web_search"
    else:
        return "llm_node"
    
def route_after_qa(state:GraphState):
    """After question_answer if context is empty ,then use web search"""
    context=state.get("context","")
    if not context  or context.strip() =="":
        return "web_search"
    return "llm_node"



        