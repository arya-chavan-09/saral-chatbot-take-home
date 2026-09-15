import json
import os

from app.generation.generator import GenerationRequest, SaralGenerator
from app.evaluation.metrics import evaluate_generation, format_eval_report
from app.vector_store.chroma_store import get_retriever

_HERE = os.path.dirname(os.path.abspath(__file__))
_APP_ROOT = os.path.dirname(os.path.dirname(_HERE))

TEST_CASES = [
    {
        "source_file": "1412.6980v9.pdf",
        "query": "Adam optimizer bias correction and update rule",
        "audience": "graduate students",
        "fmt": "bullets",
        "style": "technical",
        "n_items": 5,
        "reference_text": (
            "Adam computes individual adaptive learning rates for different "
            "parameters from estimates of first and second moments of the "
            "gradients. It corrects for initialization bias in these moment "
            "estimates. The method is well suited for problems with large "
            "data or parameters, non-stationary objectives, and noisy or "
            "sparse gradients."
        ),
    },
    {
        "source_file": "buolamwini18a.pdf",
        "query": "accuracy disparities darker females gender classification",
        "audience": "policymakers",
        "fmt": "bullets",
        "style": "plain-English",
        "n_items": 5,
        "reference_text": (
            "Commercial gender classification systems from Microsoft, IBM, "
            "and Face++ perform worst on darker-skinned women, with error "
            "rates up to 34.7%, compared to under 1% for lighter-skinned "
            "men. Existing benchmark datasets are overwhelmingly composed "
            "of lighter-skinned subjects, which the authors address with a "
            "new, more balanced dataset called PPB."
        ),
    },
    {
        "source_file": "1607_06450v1.pdf",
        "query": "layer normalization recurrent neural networks batch size",
        "audience": "graduate students",
        "fmt": "bullets",
        "style": "technical",
        "n_items": 5,
        "reference_text": (
            "Layer normalization computes normalization statistics from all "
            "summed inputs to neurons in a single layer, for a single "
            "training case, rather than across a mini-batch. This makes it "
            "usable with batch size 1 and straightforward to apply to "
            "recurrent neural networks, unlike batch normalization."
        ),
    },
]

def run_eval():
    generator = SaralGenerator()
    report_rows = []

    for case in TEST_CASES:
        retriever = get_retriever(search_kwargs={"k": 6}, source_file=case["source_file"])
        chunks = retriever.invoke(case["query"])

        request = GenerationRequest(
            audience=case["audience"],
            fmt=case["fmt"],
            style=case["style"],
            n_items=case["n_items"],
            topic=case["query"],
        )
        result = generator.generate(chunks, request)
        chunk_lookup = {d.metadata["chunk_id"]: d for d in result.chunks_used}
        eval_result = evaluate_generation(
            result.text[0]["text"], chunk_lookup, reference_text=case["reference_text"]
        )

        print(f"\n{'=' * 70}")
        print(f"Paper: {case['source_file']}")
        print(f"Query: {case['query']}")
        print(f"{'-' * 70}")
        print(result.text[0]["text"][:400] + ("..." if len(result.text) > 400 else ""))
        print(f"{'-' * 70}")
        print(format_eval_report(eval_result))

        report_rows.append({
            "source_file": case["source_file"],
            "query": case["query"],
            "citation_coverage": eval_result.citation_coverage,
            "factuality_proxy": eval_result.factuality_proxy,
            "unsupported_claim_fraction": eval_result.unsupported_claim_fraction,
            "rouge1_f": eval_result.rouge1_f,
            "rouge2_f": eval_result.rouge2_f,
            "rougeL_f": eval_result.rougeL_f,
        })

    out_path = os.path.join(_APP_ROOT, "example_runs", "eval_report.json")
    with open(out_path, "w") as f:
        json.dump(report_rows, f, indent=2)

    print(f"\n\nFull eval report saved to {out_path}")

    avg_coverage = sum(r["citation_coverage"] for r in report_rows) / len(report_rows)
    avg_factuality = sum(r["factuality_proxy"] for r in report_rows) / len(report_rows)
    print(f"\nAcross {len(report_rows)} papers:")
    print(f"  Mean citation coverage:  {avg_coverage:.0%}")
    print(f"  Mean factuality proxy:   {avg_factuality:.3f}")

    return report_rows


if __name__ == "__main__":
    run_eval()
