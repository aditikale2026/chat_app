from app.models.schemas import RAGRequest, RAGResponse
from app.langgraph_pipeline.graph_builder import graph
from fastapi import APIRouter, Request, HTTPException, Depends
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import UserORM

router = APIRouter(prefix="/rag")

@router.post("/query", response_model=RAGResponse)
async def rag_query_endpoint(
    request: RAGRequest,
    req: Request,
    current_user: UserORM = Depends(get_current_user)
):
    try:
        config = {
            "configurable": {
                "thread_id": current_user.username  # ✅ unique memory per user
            }
        }

        # ✅no messages here — checkpointer loads them automatically
        initial_state = {
            "query": request.query,
            "answer": "",
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