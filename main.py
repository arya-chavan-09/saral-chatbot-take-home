"""
main.py

Top-level entry point for the SARAL Chatbot prototype.

Usage:
    python main.py seed              # (re)build the vector store from
                                       app/ingestion/output/*.jsonl
    python main.py demo              # run the scripted demo conversation
                                       (saves example_runs/demo_conversation.json)
    python main.py eval              # run the 3-paper automatic evaluation
                                       (saves example_runs/eval_report.json)
    python main.py chat              # interactive REPL
"""
import argparse
import sys

from app.ingestion.seed_documents import load_all_documents
from app.vector_store.chroma_store import seed_vector_store

from dotenv import load_dotenv

load_dotenv()

def cmd_seed(args):
    documents = load_all_documents()
    seed_vector_store(documents, reset=args.reset)


def cmd_demo(_args):
    from app.chat.cli import run_demo_conversation
    run_demo_conversation()


def cmd_eval(_args):
    from app.evaluation.run_eval import run_eval
    run_eval()


def cmd_chat(_args):
    from app.chat.cli import interactive_chat
    interactive_chat()


def main():
    parser = argparse.ArgumentParser(description="SARAL Chatbot")
    subparsers = parser.add_subparsers(dest="command", required=True)

    seed_parser = subparsers.add_parser("seed", help="Build/update the vector store")
    seed_parser.add_argument("--reset", action="store_true", help="Drop existing collection first")
    seed_parser.set_defaults(func=cmd_seed)

    subparsers.add_parser("demo", help="Run scripted demo conversation").set_defaults(func=cmd_demo)
    subparsers.add_parser("eval", help="Run automatic evaluation").set_defaults(func=cmd_eval)
    subparsers.add_parser("chat", help="Interactive chat").set_defaults(func=cmd_chat)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    sys.exit(main())
