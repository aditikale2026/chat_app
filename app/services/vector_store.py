import os
from typing import List, Any
from app.services.embedding import embedding
from app.config import settings          # ← import settings
from langchain_chroma import Chroma
from langchain_core.documents import Document


class Storing:
    def __init__(
        self,
        collection_name: str = "pdf_documents",
        persist_directory: str | None = None,   # ← no more hardcoded default
    ):
        self.collection_name = collection_name
        # Use passed value → env var → relative default, in that priority order
        self.persist_directory = persist_directory or settings.CHROMA_PERSIST_DIR

        self.lc_docs = []
        self.active_doc = []

        os.makedirs(self.persist_directory, exist_ok=True)

        self.vectorstore = Chroma(
            collection_name=self.collection_name,
            embedding_function=embedding,
            persist_directory=self.persist_directory,
        )


    def add_documents(self, documents: List[Any], doc_id: str, filename: str, upload_time: Any, total_length: int):
        # CHANGED: use local current_docs so active_doc resets every upload
        # previously active_doc was appended forever causing re-adding old docs to vectorstore
        current_docs = []

        for doc in documents:
            metadata = dict(doc.metadata)
            metadata["doc_id"] = doc_id
            metadata["filename"] = filename
            metadata["upload_time"] = upload_time

            lc_doc = Document(page_content=doc.page_content, metadata=metadata)

            current_docs.append(lc_doc)       # current upload only
            self.lc_docs.append(lc_doc)       # all uploads ever

        # CHANGED: active_doc now only holds current upload, resets each time
        self.active_doc = current_docs

        # CHANGED: only add current_docs, not self.active_doc (which was growing forever)
        self.vectorstore.add_documents(current_docs)

        print(f"Added {len(current_docs)} documents to vector store.")

    def get_active_docs(self):
        return self.active_doc

    def delete_document_by_id(self, doc_id: str):
        """Delete all chunks belonging to a document from the vector store by doc_id."""
        try:
            # Use the underlying Chroma collection to delete by metadata filter
            # Chroma's delete method takes a where clause
            self.vectorstore._collection.delete(
                where={"doc_id": {"$eq": doc_id}}
            )
            print(f"Deleted doc_id={doc_id} from vector store.")
        except Exception as e:
            print(f"Warning: Failed to delete doc_id={doc_id} from vector store: {e}")
            # Don't raise — we still want to mark it inactive in DB even if vector store deletion fails