import argparse
import json
import os

from app.conversation.session import SaralSession
from app.generation.generator import GenerationRequest
from app.provenance.citation import (
    build_provenance,
    citation_coverage,
    format_provenance_report,
    split_into_claims,
)
from app.vector_store.chroma_store import get_retriever

EXAMPLE_RUNS_DIR = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    ),
    "example_runs",
)

def retrieve_chunks(query: str, source_file: str | None = None, k: int = 6,):
    retriever = get_retriever(search_kwargs={"k": k}, source_file=source_file,)
    return retriever.invoke(query)

def get_provenance(turn):
    lookup = {doc.metadata["chunk_id"]: doc for doc in turn.result.chunks_used}
    # claims = split_into_claims(turn.result.text)
    #For gemini changed the line
    claims = split_into_claims(turn.result.text[0]['text'])
    provenance = build_provenance(claims,lookup)
    coverage = citation_coverage(claims)

    return provenance, coverage

def print_turn(turn, show_diff=True):
    print("\n" + "=" * 70)
    print(f"USER: {turn.user_message}")
    print("-" * 70)

    #print(turn.result.text)
    #Changed for Gemini
    print(turn.result.text[0]['text'])

    if turn.reason:
        print(f"\nReason: {turn.reason}")

    if show_diff and turn.diff:
        print("\n--- DIFF vs PREVIOUS ---")
        print(turn.diff)

    provenance, coverage = get_provenance(turn)

    print(
        f"\n--- PROVENANCE "
        f"(citation coverage: {coverage:.0%}) ---"
    )

    print(format_provenance_report(provenance))

def turn_to_log_dict(turn):
    provenance, coverage = get_provenance(turn)

    request = turn.result.request

    return {
        "timestamp": turn.timestamp,
        "user_message": turn.user_message,
        "reason_for_change": turn.reason,
        "output": turn.result.text,
        "request": {
            "audience": request.audience,
            "format": request.fmt,
            "style": request.style,
            "length": request.length,
            "n_items": request.n_items,
        },
        "diff_vs_previous": turn.diff,
        "citation_coverage": coverage,
        "provenance": [
            {
                "claim": item.claim.text,
                "chunk_ids": item.claim.chunk_ids,
                "support_score": round(
                    item.support_score,
                    3,
                ),
                "sources": [
                    {
                        "source_file": doc.metadata["source_file"],
                        "page_start": doc.metadata["page_start"],
                        "page_end": doc.metadata["page_end"],
                    }
                    for doc in item.source_chunks
                ],
            }
            for item in provenance
        ],
    }

def run_demo_conversation():
    os.makedirs(EXAMPLE_RUNS_DIR, exist_ok=True)

    source_file = "1412.6980v9.pdf"
    query = "Adam optimizer bias correction and update rule"

    print(f"Query: {query}")
    print(f"Paper: {source_file}")

    chunks = retrieve_chunks(
        query,
        source_file=source_file,
        k=6,
    )

    print(f"Retrieved {len(chunks)} chunks.")

    session = SaralSession()

    turn1 = session.start(
        chunks,
        GenerationRequest(
            audience="students",
            fmt="bullets",
            style="technical",
            topic=query,
            n_items=6,
        ),
        (
            "Explain Adam optimizer in 6 technical bullets. "
            "Every bullet must cite the supporting chunk."
        ),
    )

    print_turn(turn1)

    turn2 = session.edit(
        (
            "Rewrite for undergraduate students. "
            "Keep all citations."
        ),
        chunks,
    )

    print_turn(turn2)

    turn3 = session.edit(
        (
            "Convert the explanation into a 90-second narration. "
            "Keep all citations."
        ),
        chunks,
    )

    print_turn(turn3)

    turn4 = session.edit(
        (
            "Make it more visual with an analogy of a ball "
            "rolling down a landscape. Keep all citations."
        ),
        chunks,
    )

    print_turn(turn4)

    log = {
        "paper": source_file,
        "retrieval_query": query,
        "turns": [
            turn_to_log_dict(turn)
            for turn in session.turns
        ],
    }

    output_path = os.path.join(
        EXAMPLE_RUNS_DIR,
        "demo_conversation.json",
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            log,
            file,
            indent=2,
        )

    print(
        f"\nConversation log saved to: "
        f"{output_path}"
    )

    return log

def interactive_chat():
    print("SARAL Chatbot")
    print("Commands:")
    print("  /paper  - switch paper")
    print("  /reset  - start a new conversation")
    print("  /quit   - exit\n")

    source_file = input(
        "Paper filename "
        "(blank = search all papers): "
    ).strip()

    source_file = source_file or None

    session = SaralSession()
    chunks = None

    while True:
        user_message = input("\nyou> ").strip()

        if user_message.lower() in {"/quit", "quit", "exit"}:
            print("Goodbye.")
            break

        if user_message.lower() == "/paper":
            source_file = input(
                "Paper filename (blank = search all papers): "
            ).strip() or None

            session = SaralSession()
            chunks = None

            print(
                f"Switched to: "
                f"{source_file or 'all papers'}"
            )

            continue

        if user_message.lower() == "/reset":
            session = SaralSession()
            chunks = None
            print("Conversation reset.")
            continue
        
        if not user_message:
            continue

        if session.current is None:
            audience = input(
                "Audience [general audience]: "
            ).strip()

            audience = audience or "general audience"

            fmt = input(
                "Format [script/bullets/tweet]: "
            ).strip()

            fmt = fmt or "bullets"

            style = input(
                "Style "
                "[technical/plain-English/press-release]: "
            ).strip()

            style = style or "technical"

            chunks = retrieve_chunks(
                user_message,
                source_file=source_file,
                k=4
            )

            request = GenerationRequest(
                audience=audience,
                fmt=fmt,
                style=style,
                topic=user_message,
            )

            turn = session.start(
                chunks,
                request,
                user_message,
            )
        else:
            turn = session.edit(
                user_message,
                chunks,
            )

        print_turn(turn)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="SARAL Chatbot CLI"
    )

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run the example conversation",
    )

    args = parser.parse_args()

    if args.demo:
        run_demo_conversation()
    else:
        interactive_chat()
