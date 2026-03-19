import uuid
import os
from typing import List, Any
from app.services.embedding import embedding
from chromadb.api.types import Documents, Embeddings, EmbeddingFunction
from langchain_chroma import Chroma
from langchain_core.documents import Document

# embedding = embedding()

class Storing:
    def __init__(
        self,
        collection_name: str = "pdf_documents",
        persist_directory: str = "/home/my/Desktop/Chatapp/app/Storage",
    ):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.lc_docs=[]
        self.active_doc=[]

        os.makedirs(self.persist_directory, exist_ok=True)
        self.vectorstore = Chroma(
            collection_name=self.collection_name,
            embedding_function=embedding,  # your function
            persist_directory=self.persist_directory
        )


    def add_documents(self, documents: List[Any], doc_id: str,filename:str,upload_time:Any,total_length:int):
        """
        Add documents to Chroma vectorstore.
        Each document will store its doc_id in metadata for retrieval filtering.
        """
        active_doc = []  
        # Convert to LangChain Document objects
    
        
        for doc in documents:
            metadata = dict(doc.metadata)
            metadata["doc_id"] = doc_id 
            metadata["filename"]=filename
            metadata["upload_time"]=upload_time
            self.lc_docs.append(
                Document(
                    page_content=doc.page_content,
                    metadata=metadata
                )
            )
            self.active_doc.append(Document(
                page_content=doc.page_content,  # same content
                metadata={
                    "doc_id": doc_id,
                    "filename": filename,
                    "upload_time": upload_time
                    # baaki metadata nahi chahiye, sirf identifiers
                }
            ))

        # Add all documents at once
        self.vectorstore.add_documents(self.active_doc)

        print(f"Added {len(self.active_doc)} documents to vector store.")
     
    def get_active_docs(self):
        return self.active_doc
                   