from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader
from typing import List



class PDFProcessor:

    def __init__(self, pdf_directory):
        self.pdf_directory = Path(pdf_directory)
        self.all_documents = []

    def process_pdfs(self):
        if self.pdf_directory.is_file():
            pdf_files = [self.pdf_directory]
        elif self.pdf_directory.is_dir(): 
            pdf_files = list(self.pdf_directory.glob("**/*.pdf"))
        else:
            raise ValueError("Invalid path. Provide a PDF file or directory.")

        for pdf_file in pdf_files:
            loader = PyMuPDFLoader(str(pdf_file))
            documents = loader.load()
            for doc in documents:
                doc.metadata["source_file"] = pdf_file.name
                doc.metadata["file_type"] = "pdf"

            self.all_documents.extend(documents)
            
        
        return self.all_documents


