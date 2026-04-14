from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from app.langgraph_pipeline.state import GraphState
from app.langgraph_pipeline.nodes.classify_node import classify_node
from app.langgraph_pipeline.nodes.llm_node import llm_node
from app.langgraph_pipeline.nodes.question_answer import question_answer
from app.langgraph_pipeline.edges.routing import route_after_qa, route_request
from app.langgraph_pipeline.nodes.summary import summary
from app.langgraph_pipeline.nodes.web_search import web_search
from langgraph.graph import StateGraph, END, START

_build = StateGraph(GraphState)

_build.add_node("summary", summary)
_build.add_node("classify_node", classify_node)
_build.add_node("question_answer", question_answer)
_build.add_node("llm_node", llm_node)
_build.add_node("web_search", web_search)

_build.add_edge(START, "classify_node")

_build.add_conditional_edges(
    "classify_node",
    route_request,
    {
        "summary": "summary",
        "question_answer": "question_answer",
        "llm_node": "llm_node",
        "web_search": "web_search"
    },
)

_build.add_conditional_edges(
    "question_answer",
    route_after_qa,
    {
        "web_search": "web_search",
        "llm_node": "llm_node"
    }
)

_build.add_edge("summary", "llm_node")
_build.add_edge("web_search", "llm_node")
_build.add_edge("llm_node", END)


def compile_graph(checkpointer):
    """Called once from main.py lifespan after Redis is ready."""
    return _build.compile(checkpointer=checkpointer)