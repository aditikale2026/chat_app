from app.services.vector_store import Storing
import traceback
from typing import List, Any, Dict

class RAGRetriver:

    def __init__(self, vector_store: Storing):
        self.vector_store_obj = vector_store
        
        self.lc_store = self.vector_store_obj.vectorstore
        # Raw ChromaDB collection — has .get() and .query(), but NOT similarity_search
        self._chroma_col = self.vector_store_obj.vectorstore._collection
 
    def fetch(self, query: str, fetch_all: bool, doc_ids: List[str],
              top_k: int = 10, threshold: float = 0.7) -> List[Dict[str, Any]]:
        print(f"received doc id {doc_ids}")
        try:
            if query:
                n_results = 9999 if fetch_all else top_k

                #  similarity_search_with_score lives on self.lc_store, NOT _chroma_col
                results = self.lc_store.similarity_search_with_score(
                    query=query,          
                    k=n_results,
                    filter={"doc_id": {"$in": doc_ids}}  # 'filter' not 'where'
                )

                retrieved_doc = []
                for rank, (doc, score) in enumerate(results, start=1):
                    similarity = 1 / (1 + score)
                    if similarity >= threshold:
                        retrieved_doc.append({
                            "id": doc.metadata.get("id", ""),
                            "content": doc.page_content,
                            "metadata": doc.metadata,
                            "similarity_score": float(similarity),
                            "distance": float(score),
                            "rank": rank
                        })

            else:
                # .get() is fine on _chroma_col — no embedding needed
                all_docs = self._chroma_col.get(
                    where={"doc_id": {"$in": doc_ids}},
                    include=["documents", "metadatas", "ids"]
                )
                docs  = all_docs["documents"][:top_k]
                metas = all_docs["metadatas"][:top_k]
                ids   = all_docs["ids"][:top_k]

                retrieved_doc = [
                    {
                        "id": id_,
                        "content": doc,
                        "metadata": meta,
                        "similarity_score": 1.0,
                        "distance": 0.0,
                        "rank": i + 1
                    }
                    for i, (id_, doc, meta) in enumerate(zip(ids, docs, metas))
                ]

            return retrieved_doc

        except Exception as e:
            print(f"Error during retrieval: {e}")
            traceback.print_exc()
            return []


# if __name__ == "__main__":
#     store = Storing()
#     obj = RAGRetriver(store)
#     print(obj.fetch(
#         query="summary the document",
#         fetch_all=True,
#         doc_ids=["a5394101-9863-446e-a8b1-9f70cc70f910"],
        
#     ))