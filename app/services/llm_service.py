from langchain_groq import ChatGroq
import os 
from dotenv import load_dotenv
from langchain_core.prompts import MessagesPlaceholder , ChatPromptTemplate

load_dotenv()

def get__llm():
    api_key=os.getenv("GROQ_API_KEY")
    llm=ChatGroq(model="llama-3.1-8b-instant",
        api_key=api_key,
        temperature=0.9,
        max_tokens=2000)
    return llm 