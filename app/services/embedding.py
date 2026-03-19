from sentence_transformers import SentenceTransformer
from langchain_huggingface import HuggingFaceEmbeddings
from app.utils.document_process.pdf_loader import PDFProcessor
from app.utils.document_process.chunking import splitting

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)