from app.langgraph_pipeline.state import GraphState
from ddgs import DDGS
import logging

logger = logging.getLogger(__name__)

def web_search(state:GraphState):
    query=state["query"]
    logger.info(f"[web_search_node] searching query {query}")
    try:
        with DDGS(timeout=10) as ddgs:
            result=list(ddgs.text(query,max_results=10))
        if not result:
            logger.warning(f"[web_search_node] No result found")
            return {"context":"","mode":"web_search"}
            
        context = "\n\n".join([
        f"Source: {r['href']}\nTitle: {r['title']}\n{r['body']}"
        for r in result
           ])   
            
        logger.info(f"[web_search_node] Got {len(result)} results")
        return {"context": context, "mode": "web_search"}
             
    except Exception as e:
        logger.error(f"[web_search_node] Error: {e}")
        return {"context": "", "mode": "web_search"}