from app.services.llm_service import get__llm
from langchain_core.messages import HumanMessage, AIMessage

def rewrite_query(query: str, messages: list) -> str:
    """Rewrite vague query into clear self-contained question."""

    if not messages:
        return query

    # format history
    history = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            history.append(f"User: {msg.content}")
        elif isinstance(msg, AIMessage):
            history.append(f"Assistant: {msg.content}")
    history_text = "\n".join(history)

    llm = get__llm(temperature=0.3)  # low temp for rewriting

    prompt = f"""
Previous conversation:
{history_text}

Original query: {query}

Rewrite the query to be completely clear and self-contained
without needing the conversation history.
If the query already is clear, return it as is.
Return ONLY the rewritten query, nothing else.

Rewritten query:
"""

    result = llm.invoke(prompt)
    rewritten = result.content.strip()
    print(f"[query_rewriter] '{query}' → '{rewritten}'")
    return rewritten