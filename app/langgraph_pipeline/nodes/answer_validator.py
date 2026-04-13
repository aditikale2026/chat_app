from app.services.llm_service import get__llm

def validate_answer(query: str, answer: str, context: str, mode: str) -> bool:
    """Check if answer actually addresses the question."""

    # only validate qa and document modes
    if mode not in ["qa", "summary"]:
        return True

    if not context:
        return True

    llm = get__llm(temperature=0.0)  # zero temp for validation

    prompt = f"""
Question: {query}
Answer: {answer}
Context: {context}

Does this answer correctly address the question using the context?
Reply only YES or NO.
"""

    result = llm.invoke(prompt)
    decision = result.content.strip().upper()
    is_valid = "YES" in decision
    print(f"[answer_validator] Valid: {is_valid}")
    return is_valid