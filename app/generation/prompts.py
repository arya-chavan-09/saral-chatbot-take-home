import json
from langchain_core.documents import Document

LENGTH_WORDS = {
    "30s": 75,
    "90s": 220,
    "5min": 800,
}

STYLE_DESCRIPTIONS = {
    "technical": "Use precise technical language.",
    "plain-English": "Use simple language and explain technical terms.",
    "press-release": (
        "Use concise, engaging language for a general audience."
    ),
}

SAFETY_RULES = """
RULES:

1. Use ONLY the SOURCE MATERIAL.
2. Do not use outside knowledge.
3. Do not invent facts, numbers, results, recommendations, or explanations.

CITATION RULES:

4. EVERY factual sentence MUST end with a citation.
5. The citation MUST appear immediately after the sentence it supports.
6. Never group citations at the end of a paragraph.
7. Never create a standalone citation section.
8. Never write '(Citation: ...)'.
9. Every claim must have at least one citation.

10. Copy citations EXACTLY as provided in the source material.
11. Use the exact citation string shown for the source chunk.
12. Citation format:
    [source_file.pdf::chunkXXXX]

13. If multiple sentences appear in a paragraph,
    each sentence must have its own citation.

CORRECT:

Adam is an optimization algorithm used in deep learning. [1412.6980v9.pdf::chunk0001]

Adam is computationally efficient. [1412.6980v9.pdf::chunk0002]

INCORRECT:

Adam is an optimization algorithm used in deep learning.

[1412.6980v9.pdf::chunk0001]

INCORRECT:

Adam is an optimization algorithm used in deep learning.

(Citation: [1412.6980v9.pdf::chunk0001])

14. Keep equations in LaTeX when they appear in the source.
15. Match the requested audience and style.
16. Return only the requested output.
"""

def render_chunks(chunks: list[Document]) -> str:
    parts = []

    for doc in chunks:
        source_file = doc.metadata.get(
            "source_file",
            "unknown.pdf",
        )

        chunk_id = doc.metadata["chunk_id"]

        parts.append(
            f"SOURCE FILE: {source_file}\n"
            f"CITATION: [{chunk_id}]\n"
            f"PAGE: {doc.metadata['page_start']}-"
            f"{doc.metadata['page_end']}\n"
            f"TEXT:\n{doc.page_content}"
        )

    return "\n\n".join(parts)

def build_generation_prompt(
    chunks,
    audience,
    fmt,
    style="technical",
    length=None,
    n_items=7,
    topic="",
    extra_instructions="",
):
    context = render_chunks(chunks)

    words = LENGTH_WORDS.get(length, 220)

    length_instruction = ""

    if length:
        length_instruction = (
            f"Target approximately {words} words."
        )

    system_prompt = f"""
You are SARAL, an assistant that converts research papers
into audience-adapted communication.

Audience: {audience}
Format: {fmt}
Style: {STYLE_DESCRIPTIONS.get(style, style)}
Target Length: {words} words
Number of Items: {n_items}

{length_instruction}

{SAFETY_RULES}

SOURCE MATERIAL:

{context}

IMPORTANT:

Every factual sentence must contain a citation.

Do not place citations at the end of sections.

Do not create a final bibliography.

Do not create a final citation block.

The citation must appear directly after the statement
that it supports.

Use the citation string exactly as shown in each source chunk.
"""

    request = {
        "format": fmt,
        "style": style,
        "n_items": n_items,
        "topic": topic,
    }

    user_prompt = (
        f"Generate the requested {fmt}.\n"
        f"Focus on: {topic}\n"
        f"{extra_instructions}\n\n"
        f"REQUEST:{json.dumps(request)}"
    )

    return system_prompt, user_prompt

def build_edit_prompt(
    chunks,
    previous_output,
    edit_instruction,
    audience,
    style,
    fmt,
    topic="",
    n_items=7,
):
    context = render_chunks(chunks)

    #Changed for Gemini
    previous_output = previous_output[0]['text']

    system_prompt = f"""
You are SARAL editing an existing research communication.

Audience: {audience}
Format: {fmt}
Style: {style}

{SAFETY_RULES}

SOURCE MATERIAL:

{context}

PREVIOUS OUTPUT:

{previous_output}

IMPORTANT:

Every factual sentence must contain a citation.

Preserve citations where possible.

Any new statement introduced during editing must
have a citation.

Do not create a trailing citation section.

Do not write '(Citation: ...)'.
"""

    user_prompt = f"""
Apply this user edit:

{edit_instruction}

Return the complete revised output.

Keep the same subject unless the user explicitly changes it.

Every factual sentence must contain a citation.
"""

    return system_prompt, user_prompt

