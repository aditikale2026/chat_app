def chunk_context(context: str, chunk_size: int = 20000) -> List[str]:
    """Split large context into smaller chunks by characters."""
    chunks = []
    for i in range(0, len(context), chunk_size):
        chunks.append(context[i: i + chunk_size])
    return chunks

def map_reduce_summary(llm, context: str) -> str:
    """Summarize large context using map-reduce approach."""

    chunks = chunk_context(context, chunk_size=20000)
    print(f"Map-Reduce: splitting into {len(chunks)} chunks")

    # --- MAP: summarize each chunk ---
    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        print(f"  Summarizing chunk {i + 1}/{len(chunks)}...")
        map_prompt = f"""
        This is section {i + 1} of {len(chunks)} of a document.
        Write a concise summary of the key points from this section only.
        Do not add any information not present in the text.

        Text:
        {chunk}

        Concise Summary:
        """
        response = llm.invoke(map_prompt)
        chunk_summaries.append(response.content)

    # --- REDUCE: combine all chunk summaries ---
    print("  Combining chunk summaries into final summary...")
    combined = "\n\n".join(
        [f"Section {i + 1}:\n{s}" for i, s in enumerate(chunk_summaries)]
    )
    reduce_prompt = f"""
    Below are summaries of different sections of a document.
    Combine them into one cohesive, well-structured final summary.
    Capture all key points without repeating information.

    Section Summaries:
    {combined}

    Final Summary:
    """
    final_response = llm.invoke(reduce_prompt)
    return final_response.content