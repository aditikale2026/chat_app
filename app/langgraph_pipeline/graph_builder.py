from app.langgraph_pipeline.state import GraphState
from app.langgraph_pipeline.nodes.classify_node import classify_node
from app.langgraph_pipeline.nodes.llm_node import llm_node
from app.langgraph_pipeline.nodes.question_answer import question_answer
from app.langgraph_pipeline.edges.routing import route_after_qa, route_request
from app.langgraph_pipeline.nodes.summary import summary
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import InMemorySaver
from app.langgraph_pipeline.nodes import web_search
from app.langgraph_pipeline.nodes.web_search import web_search
from app.langgraph_pipeline.edges.routing import route_after_qa 

memory = InMemorySaver()


build = StateGraph(GraphState)

build.add_node("summary", summary)
build.add_node("classify_node", classify_node)
build.add_node("question_answer", question_answer)
build.add_node("llm_node",llm_node)
build.add_node("web_search",web_search)

build.add_edge(START, "classify_node")

build.add_conditional_edges(
    "classify_node",
    route_request,
    {
        "summary": "summary",
        "question_answer": "question_answer",
        "llm_node": "llm_node",
        "web_search":"web_search"
    },
)

build.add_conditional_edges(
    "question_answer",
    route_after_qa,
    {
        "web_search":"web_search",
        "llm_node":"llm_node"        
    }
)
# build.add_edge("  ", "llm_node")

build.add_edge("summary", "llm_node")

build.add_edge("web_search", "llm_node")

build.add_edge("llm_node", END)

graph = build.compile(checkpointer=memory)