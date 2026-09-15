from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from rouge_score import rouge_scorer

from app.provenance.citation import (
    build_provenance,
    citation_coverage,
    split_into_claims,
)

@dataclass(slots=True)
class EvalResult:
    citation_coverage: float
    factuality_proxy: float
    unsupported_claim_fraction: float

    rouge1_f: Optional[float] = None
    rouge2_f: Optional[float] = None
    rougeL_f: Optional[float] = None

    @property
    def has_reference_metrics(self) -> bool:
        return self.rouge1_f is not None

def evaluate_generation(
    generated_text: str,
    chunk_lookup: dict,
    reference_text: str | None = None,
) -> EvalResult:
    claims = split_into_claims(generated_text)

    if not claims:
        return EvalResult(
            citation_coverage=0.0,
            factuality_proxy=0.0,
            unsupported_claim_fraction=1.0,
        )

    provenance = build_provenance(claims, chunk_lookup)

    coverage = citation_coverage(claims)

    support_scores = [
        p.support_score
        for p in provenance
    ]

    factuality_proxy_score = (
        sum(support_scores) / len(support_scores)
        if support_scores
        else 0.0
    )

    unsupported_fraction = (
        sum(
            1
            for p in provenance
            if not p.source_chunks
        )
        / len(provenance)
    )

    result = EvalResult(
        citation_coverage=coverage,
        factuality_proxy=factuality_proxy_score,
        unsupported_claim_fraction=unsupported_fraction,
    )

    if reference_text:
        _populate_rouge_metrics(
            result=result,
            reference_text=reference_text,
            generated_text=generated_text,
        )

    return result

def _populate_rouge_metrics(
    result: EvalResult,
    reference_text: str,
    generated_text: str,
) -> None:
    scorer = rouge_scorer.RougeScorer(
        ["rouge1", "rouge2", "rougeL"],
        use_stemmer=True,
    )

    scores = scorer.score(reference_text, generated_text)

    result.rouge1_f = scores["rouge1"].fmeasure
    result.rouge2_f = scores["rouge2"].fmeasure
    result.rougeL_f = scores["rougeL"].fmeasure

def semantic_similarity_scorer(
    text_a: str,
    text_b: str,
) -> float:
    raise NotImplementedError(
        "Install sentence-transformers and implement a semantic "
        "similarity backend."
    )

def format_eval_report(result: EvalResult) -> str:
    report = [
        "=== Evaluation Report ===",
        "",
        f"Citation coverage        : {result.citation_coverage:.1%}",
        f"Factuality proxy         : {result.factuality_proxy:.3f}",
        f"Unsupported claim rate   : {result.unsupported_claim_fraction:.1%}",
    ]

    if result.has_reference_metrics:
        report.extend(
            [
                "",
                "Reference Comparison",
                f"ROUGE-1 F1              : {result.rouge1_f:.3f}",
                f"ROUGE-2 F1              : {result.rouge2_f:.3f}",
                f"ROUGE-L F1              : {result.rougeL_f:.3f}",
            ]
        )

    return "\n".join(report)
