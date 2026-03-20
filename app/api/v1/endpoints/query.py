from app.models.schemas import RAGRequest, RAGResponse
from app.langgraph_pipeline.graph_builder import graph
from fastapi import APIRouter, Request, HTTPException

router = APIRouter(prefix="/rag")

@router.post("/query", response_model=RAGResponse)
async def rag_query_endpoint(request: RAGRequest, req: Request):
    # CHANGED: removed passing retriever, store, active_doc in initial_state
    # those objects are now fetched inside nodes via get_service()
    # only serializable fields go into state now
    try:
        config = {
            "configurable": {
                "thread_id": "rag_user"
            }
        }
        initial_state = {
            "query": request.query,
            "answer": "",
            "messages": [],
            # CHANGED: removed retriever, store, active_doc from here
        }

        final_state = graph.invoke(initial_state, config=config)

        if not final_state.get("answer") or final_state["answer"].strip() == "":
            raise HTTPException(
                status_code=404,
                detail="Content related to the query does not exist in the provided PDFs"
            )

        return {
            "query": final_state["query"],
            "answer": final_state["answer"],
            "mode": final_state["mode"]
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))