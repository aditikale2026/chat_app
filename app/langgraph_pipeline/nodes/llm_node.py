from app.langgraph_pipeline.state import GraphState
from app.services.llm_service import get__llm
from app.utils.summarization_utility import map_reduce_summary

MAX_CHARS = 80000
llm = get__llm()

def llm_node(state: GraphState):

    context = state.get("context")
    query = state.get("query")
    mode = state.get("mode")

    # ─── SUMMARY MODE ───────────────────────────────────────────────
    if mode == "summary":
        print(f"Context size: {len(context)} chars | Limit: {MAX_CHARS} chars")

        if len(context) > MAX_CHARS:
            print("Context too large → using map-reduce summarization")
            response_text = map_reduce_summary(llm, context)
            return {"answer": response_text}

        else:
            print("Context within limit → direct summarization")
            prompt = f"""
You are an expert document analyst. Your task is to produce a structured, 
insightful summary of the provided document content.

Instructions:
- Start with a 2-3 sentence overview of what the document is about
- Highlight the key topics, findings, or arguments
- Mention any important data, dates, names, or conclusions
- End with a 1 sentence takeaway
- Do NOT add any information not present in the document
- Use clear, professional language

Document Content:
{context}

Structured Summary:
"""

    # ─── QA MODE ────────────────────────────────────────────────────
    elif mode == "qa":
        prompt = f"""
You are a precise and reliable question-answering assistant working with document content.

Rules:
- Answer ONLY using the information present in the context below
- If the answer is partially present, provide what you can and clearly state what is missing
- If the answer is not in the context at all, respond with:
  "The provided document does not contain information about this topic."
- Never guess, assume, or use outside knowledge
- Keep your answer concise and directly address the question
- If relevant, mention which part of the document supports your answer

Context:
{context}

Question:
{query}

Answer:
"""

    # ─── WEB SEARCH MODE ────────────────────────────────────────────
    elif mode == "web_search":
        prompt = f"""
You are a knowledgeable assistant that answers questions using real-time web search results.

Instructions:
- Synthesize the search results into a clear, accurate answer
- Prioritize the most relevant and recent information
- Cite sources by mentioning the title or URL where relevant
- If search results are conflicting, mention the discrepancy
- If no relevant results were found, say so clearly
- Keep the answer focused and avoid unnecessary repetition

Web Search Results:
{context}

Question:
{query}

Answer:
"""

    # ─── CHAT / GENERAL MODE ────────────────────────────────────────
    else:
        prompt = f"""
You are a helpful, friendly, and knowledgeable conversational assistant 
integrated into a document-based chat application.

Instructions:
- Answer the user's question naturally and conversationally
- If the question seems related to documents or PDFs, 
  suggest the user upload a document for more accurate answers
- Be concise but complete
- If you are unsure, say so honestly

Question:
{query}

Answer:
"""

    response_obj = llm.invoke(prompt)
    response_text = response_obj.content

    return {"answer": response_text}