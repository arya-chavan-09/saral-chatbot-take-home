import re

SENTENCE_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")
CHARS_PER_TOKEN = 4

def count_tokens(text):
    return max(1, round(len(text) / CHARS_PER_TOKEN)) if text else 0

def split_sentences(text):
    return [
        sentence.strip()
        for sentence in SENTENCE_RE.split(text)
        if sentence.strip()
    ]

def make_chunk(index, source_file, sentences):
    text = " ".join(
        sentence
        for sentence, _, _ in sentences
    )

    pages = [
        page
        for _, page, _ in sentences
    ]

    sections = [
        section
        for _, _, section in sentences
        if section
    ]

    return {
        "chunk_id": f"{source_file}::chunk{index:04d}",
        "source_file": source_file,
        "page_start": min(pages),
        "page_end": max(pages),
        "section": sections[-1] if sections else None,
        "text": text,
        "token_count": count_tokens(text),
    }

def get_overlap(sentences, overlap_tokens):
    result = []
    tokens = 0

    for sentence, page, section in reversed(sentences):
        size = count_tokens(sentence)

        if tokens + size > overlap_tokens and result:
            break

        result.append(
            (sentence, page, section)
        )

        tokens += size

    return list(reversed(result))

def chunk_document(pages, source_file, min_tokens=150, max_tokens=300, overlap_tokens=50):
    sentences = []

    for page in pages:
        for sentence in split_sentences(page["text"]):
            sentences.append(
                (
                    sentence,
                    page["page_num"],
                    page.get("section"),
                )
            )

    chunks = []
    current = []
    current_tokens = 0

    for sentence, page, section in sentences:
        size = count_tokens(sentence)

        # Keep a very large sentence as its own chunk.
        if size > max_tokens:
            if current:
                chunks.append(
                    make_chunk(
                        len(chunks),
                        source_file,
                        current,
                    )
                )

                current = []
                current_tokens = 0

            chunks.append(
                make_chunk(
                    len(chunks),
                    source_file,
                    [(sentence, page, section)],
                )
            )

            continue

        if (
            current
            and current_tokens >= min_tokens
            and current_tokens + size > max_tokens
        ):
            chunks.append(
                make_chunk(
                    len(chunks),
                    source_file,
                    current,
                )
            )

            current = get_overlap(
                current,
                overlap_tokens,
            )

            current_tokens = sum(
                count_tokens(sentence)
                for sentence, _, _ in current
            )

        current.append(
            (sentence, page, section)
        )

        current_tokens += size

    if current:
        chunks.append(
            make_chunk(
                len(chunks),
                source_file,
                current,
            )
        )

    return chunks