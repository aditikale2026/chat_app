def route_request(state:GraphState):
    if state["mode"]=="summary":
        return "summary"
    elif state["mode"]=="qa":
        return "retrieve_docs"
    else:
        return "chat_node"