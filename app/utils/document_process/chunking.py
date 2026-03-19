from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.utils.document_process.pdf_loader import PDFProcessor
class splitting():
    def __init__(self,documents):
        self.documents=documents
        self.chunk=[]
        # print(self.documents)
    def split_documents (self,chunk_size=500,chunk_overlap=250):
        text_splitter=RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n","\n"," ",""]
            )
        split_docs=text_splitter.split_documents(self.documents)
        return split_docs
   


   