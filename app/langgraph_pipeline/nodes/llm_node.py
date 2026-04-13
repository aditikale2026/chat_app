from app.langgraph_pipeline.state import GraphState
from app.services.llm_service import get__llm, get_system_prompt
from app.utils.summarization_utility import map_reduce_summary
from app.langgraph_pipeline.nodes.answer_validator import validate_answer
from langchain_core.messages import HumanMessage, AIMessage
import re

MAX_CHARS = 80000
llm = get__llm()

def _format_messages(messages):
    if not messages:
        return "No previous conversation."
    formatted = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            formatted.append(f"User: {msg.content}")
        elif isinstance(msg, AIMessage):
            formatted.append(f"Assistant: {msg.content}")
    return "\n".join(formatted)

def _clean_markdown(text: str) -> str:
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[\*\-]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def llm_node(state: GraphState):
    context = state.get("context", "")
    query = state.get("query")
    mode = state.get("mode")
    messages = state.get("messages", [])
    system_prompt = get_system_prompt()
    history = _format_messages(messages)

    # ─── SUMMARY MODE ───────────────────────────────────────────────
    if mode == "summary":
        print(f"Context size: {len(context)} chars | Limit: {MAX_CHARS} chars")

        if len(context) > MAX_CHARS:
            response_text = map_reduce_summary(llm, context)
            response_text = _clean_markdown(response_text)
            updated_messages = list(messages) + [
                HumanMessage(content=query),
                AIMessage(content=response_text)
            ]
            return {"answer": response_text, "messages": updated_messages}

        # ✅ chain of thought for summary
        prompt = f"""{system_prompt}

Previous conversation:
{history}

Document Content:
{context}

User asked: {query}

Think through this step by step:
Step 1 - What is the main topic of this document?
Step 2 - What are the key points?
Step 3 - What conclusions does it reach?
Step 4 - Write a clean summary in plain text paragraphs.

Final Summary:
"""

    # ─── QA MODE ────────────────────────────────────────────────────
    elif mode == "qa":
        # ✅ few shot + chain of thought for qa
        prompt = f"""{system_prompt}

Here are examples of good answers:

Question: What is the revenue mentioned in the document?
Answer: The document states the revenue was 5 million dollars in Q3 2024.

Question: Who is the author?
Answer: The document does not mention an author.

Previous conversation:
{history}

Document Content:
{context}

Question: {query}

Think through this step by step:
Step 1 - Find relevant parts of the document
Step 2 - Check if the answer is actually there
Step 3 - Form a direct, precise answer

Final Answer:
"""

    # ─── WEB SEARCH MODE ────────────────────────────────────────────
    elif mode == "web_search":
        prompt = f"""{system_prompt}

Previous conversation:
{history}

Web Search Results:
{context}

Question: {query}

Think through this step by step:
Step 1 - Which search results are most relevant?
Step 2 - What is the most accurate answer?
Step 3 - Synthesize into a clean direct answer

Final Answer:
"""

    # ─── CHAT MODE ──────────────────────────────────────────────────
    else:
        prompt = f"""{system_prompt}

Previous conversation:
{history}

User: {query}

Response:
"""

    response_obj = llm.invoke(prompt)
    response_text = _clean_markdown(response_obj.content)

    # ✅ answer validation for qa and summary
    if mode in ["qa", "summary"]:
        is_valid = validate_answer(query, response_text, context, mode)
        if not is_valid:
            print("[llm_node] Answer failed validation → regenerating")
            # regenerate with stricter prompt
            strict_prompt = f"""{system_prompt}

Your previous answer was not accurate enough.
Answer ONLY using the document content below.
If the answer is not there, say so clearly.

Document Content:
{context}

Question: {query}

Accurate Answer:
"""
            response_obj = llm.invoke(strict_prompt)
            response_text = _clean_markdown(response_obj.content)

    updated_messages = list(messages) + [
        HumanMessage(content=query),
        AIMessage(content=response_text)
    ]

    return {
        "answer": response_text,
        "messages": updated_messages
    }