import re

NUMBERED_HEADER_RE = re.compile(r"^(\d{1,2}(?:\.\d{1,2})?)\.?\s+([A-Z][A-Za-z][A-Za-z0-9\s:,'’\-]{2,60})$")
KNOWN_HEADER_WORDS = {
    "abstract", "references", "acknowledgments", "acknowledgements",
    "appendix", "supplementary material", "conclusion",
}

def detect_section(text: str):
    text = text.strip()

    match = NUMBERED_HEADER_RE.match(text)
    if match:
        return f"{match.group(2)} {match.group(2).strip()}"

    if text.lower() in KNOWN_HEADER_WORDS:
        return text.title()

    return None

def add_sections(pages):
    current_section = None

    for page in pages:
        for line in page["text"].splitlines():
            section = detect_section(line)

            if section:
                current_section = section

        page["section"] = current_section

    return pages

if __name__ == "__main__":
    tests = [
        "1 INTRODUCTION",
        "2.1 ADAM’S UPDATE RULE",
        "3 INITIALIZATION BIAS CORRECTION",
        "Abstract",
        "References",
        "This is just a normal sentence with 2 apples in it.",
        "10.1 CONVERGENCE PROOF",
    ]
    for t in tests:
        print(f"{t!r:55} -> {detect_section(t)}")
