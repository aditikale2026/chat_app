from typing import List

def chunk_context(context: str, chunk_size: int = 20000) -> List[str]:
    chunks = []
    for i in range(0, len(context), chunk_size):
        chunks.append(context[i: i + chunk_size])
    return chunks

def map_reduce_summary(llm, context: str) -> str:
    import re

    chunks = chunk_context(context, chunk_size=20000)
    print(f"Map-Reduce: splitting into {len(chunks)} chunks")

    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        print(f"  Summarizing chunk {i + 1}/{len(chunks)}...")
        map_prompt = f"""
This is section {i + 1} of {len(chunks)} of a document.
Write a concise summary of the key points from this section only.
Do not add any information not present in the text.
Write in plain text only, no markdown, no bullet points, no asterisks.

Text:
{chunk}

Concise Summary:
"""
        response = llm.invoke(map_prompt)
        chunk_summaries.append(response.content)

    print("  Combining chunk summaries into final summary...")
    combined = "\n\n".join(
        [f"Section {i + 1}:\n{s}" for i, s in enumerate(chunk_summaries)]
    )
    reduce_prompt = f"""
Below are summaries of different sections of a document.
Combine them into one cohesive, well-structured final summary.
Capture all key points without repeating information.
Write in plain text only, no markdown, no bullet points, no asterisks.

Section Summaries:
{combined}

Final Summary:
"""
    final_response = llm.invoke(reduce_prompt)

    # clean any leftover markdown
    text = final_response.content
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[\*\-]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()