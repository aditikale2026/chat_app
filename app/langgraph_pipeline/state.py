from typing import TypedDict, Annotated, Any,List
from langgraph.graph.message import add_messages


class GraphState(TypedDict):
    query: str | None
    filename: str | None
    mode: str
    answer: str |None
    messages:List[Any]
    doc_id: List[str] | None  # new
    upload_time: str | None  # new
    context : str | None
    fetch_all :bool
    messages: Annotated[List[Any], add_messages]
    