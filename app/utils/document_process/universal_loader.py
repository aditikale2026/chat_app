"""
Single entry-point for loading any supported document type.
Each loader returns a list of LangChain Documents.
"""
from pathlib import Path
from typing import List
from langchain_core.documents import Document


def load_document(file_path: str) -> List[Document]:
    path = Path(file_path)
    ext  = path.suffix.lower()
    name = path.name

    if ext == ".pdf":
        from langchain_community.document_loaders import PyMuPDFLoader
        loader = PyMuPDFLoader(file_path)

    elif ext in (".txt", ".md"):
        from langchain_community.document_loaders import TextLoader
        loader = TextLoader(file_path, encoding="utf-8")

    elif ext == ".docx":
        from langchain_community.document_loaders import Docx2txtLoader
        loader = Docx2txtLoader(file_path)

    elif ext == ".csv":
        from langchain_community.document_loaders import CSVLoader
        loader = CSVLoader(file_path)

    else:
        raise ValueError(f"No loader available for '{ext}'")

    documents = loader.load()

    for doc in documents:
        doc.metadata["source_file"] = name
        doc.metadata["file_type"]   = ext.lstrip(".")

    return documents