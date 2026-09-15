import re
from dataclasses import dataclass
from langchain_core.documents import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

CITATION_RE = re.compile(r"\[\s*([A-Za-z0-9_.() /-]+::chunk\d+)\s*\]")

@dataclass
class Claim:
    text: str
    chunk_ids: list[str]

@dataclass
class ClaimProvenance:
    claim: Claim
    source_chunks: list[Document]
    support_score: float

def split_into_claims(text: str) -> list[Claim]:
    claims: list[Claim] = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        if line.startswith("#"):
            continue

        if line.lower().startswith(
            ("here's", "here is", "here are", "sure,", "certainly")
        ):
            continue

        chunk_ids = CITATION_RE.findall(line)

        if chunk_ids and not CITATION_RE.sub("", line).strip():
            if claims:
                claims[-1].chunk_ids.extend(chunk_ids)
            continue

        if (
            line.lower().startswith("(citation")
            and chunk_ids
            and claims
        ):
            claims[-1].chunk_ids.extend(chunk_ids)
            continue

        clean = re.sub(r"^[-*•]\s*", "", line)
        clean = CITATION_RE.sub("", clean).strip()

        if not clean:
            continue

        claims.append(
            Claim(
                text=clean,
                chunk_ids=chunk_ids,
            )
        )
    return claims
    
def citation_coverage(claims: list[Claim]) -> float:
    if not claims:
        return 0.0

    return sum(bool(c.chunk_ids) for c in claims) / len(claims)

def text_similarity(a: str, b: str) -> float:
    try:
        vectors = TfidfVectorizer().fit_transform([a, b])
        return float(cosine_similarity(vectors[0], vectors[1])[0][0])
    except ValueError:
        return 0.0

def build_provenance(claims: list[Claim], chunk_lookup: dict[str, Document]) -> list[ClaimProvenance]:
    results = []

    for claim in claims:
        sources = [
            chunk_lookup[cid]
            for cid in claim.chunk_ids
            if cid in chunk_lookup
        ]

        score = max(
            (
                text_similarity(claim.text, doc.page_content)
                for doc in sources
            ),
            default=0.0,
        )

        results.append(
            ClaimProvenance(
                claim=claim,
                source_chunks=sources,
                support_score=score,
            )
        )

    return results

def format_provenance_report(provenance: list[ClaimProvenance]) -> str:
    lines = []

    for i, item in enumerate(provenance, start=1):
        if item.source_chunks:
            sources = ", ".join(
                f"{doc.metadata.get('source_file', 'unknown')} "
                f"p.{doc.metadata.get('page_start', '?')}-"
                f"{doc.metadata.get('page_end', '?')}"
                for doc in item.source_chunks
            )

            flag = ""
            if item.support_score < 0.15:
                flag = " [WEAK SUPPORT]"

        else:
            sources = "NO CITATION FOUND"
            flag = " [UNSUPPORTED CLAIM]"

        claim_text = item.claim.text
        if len(claim_text) > 90:
            display = claim_text[:90] + "..."
        else:
            display = claim_text

        lines.append(
            f'{i}. "{display}" → {sources}{flag}'
        )

    return "\n".join(lines)