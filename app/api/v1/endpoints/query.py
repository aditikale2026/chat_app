from app.models.schemas import RAGRequest,RAGResponse
import fastapi
from app.langgraph_pipeline.graph_builder import graph
from fastapi import APIRouter,Request,HTTPException

router=APIRouter(prefix="/rag")
@router.post("/query",response_model=RAGResponse)
async def rag_query_endpoint(request:RAGRequest,req:Request):
    store= req.app.state.vectorstore
    doc=store.get_active_docs()
    print(doc)
    # doc_id = doc_id
    
    try:

        config = {
            "configurable":{
                "thread_id":"rag_user"
                           }
                }
        initial_state = {
            "query": request.query ,
            # "folder_link": request.folder_link,
            "answer": "",
            "messages":[],
            # "doc_id":doc_id
            "retriever" :req.app.state.retriever,
            "store":store,
            "active_doc":doc
            }

        final_state = graph.invoke(initial_state,config=config)
        if not final_state.get("answer") or final_state["answer"].strip() == "":
            raise HTTPException(
                status_code=404 ,
                detail="Content related to the query does not exist  in the provided PDFs"
                )

        checkpoints = list(graph.get_state_history(config))

        # for cp in checkpoints:
        #     print("Checkpoints:")
        #     print(cp)
        #     print("State Valuve : ", cp.values)
        #     print("Next Node : ", cp.next) 
        #     print("MetaData : ", cp.metadata)
        return {
            "query":final_state["query"],
            "answer":final_state["answer"],
            "mode":final_state["mode"]
        }
      
    except ValueError as e:
        raise HTTPException(status_code=400,detail=str(e))    
    except Exception as e:
        raise  HTTPException(status_code=500,detail=str(e))

