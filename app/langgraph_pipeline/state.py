from typing import TypedDict, Annotated, Any,List


class GraphState(TypedDict):
    query: str | None
    filename: str | None
    mode: str
    answer: str |None
    # messages: Annotated[List[Any], add_messages]
    messages:List[Any]
    doc_id: List[str] | None  # new
    upload_time: str | None  # new
    context : str | None
    fetch_all :bool
    retriever:Any