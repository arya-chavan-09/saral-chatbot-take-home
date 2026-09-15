import argparse
import json
import os
import re

from app.ingestion.pdf_parser import parse_pdf
from app.ingestion.section_detector import add_sections
from app.ingestion.chunker import chunk_document


DEFAULT_OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "output",
)

def clean_text(text: str) -> str:    
    text = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1\2", text)
    text = re.sub(r"^\s*\d{1,4}\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def process_pdf(pdf_path: str, min_tokens: int = 80, max_tokens: int = 180, overlap_tokens: int = 30):
    pages = parse_pdf(pdf_path)

    for page in pages:
        page["text"] = clean_text(page["text"])

    pages = add_sections(pages)

    chunks = chunk_document(
        pages,
        source_file=os.path.basename(pdf_path),
        min_tokens=min_tokens,
        max_tokens=max_tokens,
        overlap_tokens=overlap_tokens,
    )

    return chunks

def ingest_pdf(pdf_path: str, output_dir: str = DEFAULT_OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)

    chunks = process_pdf(pdf_path)

    filename = os.path.splitext(os.path.basename(pdf_path))[0]
    output_path = os.path.join(output_dir, f"{filename}.jsonl")

    with open(output_path, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk) + "\n")

    print(f"{filename}: {len(chunks)} chunks")
    return output_path

def ingest_directory(input_dir: str, output_dir: str = DEFAULT_OUTPUT_DIR):
    if not os.path.isdir(input_dir):
        raise FileNotFoundError(input_dir)

    pdf_files = [
        f for f in sorted(os.listdir(input_dir))
        if f.lower().endswith(".pdf")
    ]

    return [
        ingest_pdf(os.path.join(input_dir, filename), output_dir)
        for filename in pdf_files
    ]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ingest SARAL PDFs into JSONL chunks"
    )

    parser.add_argument(
        "--input-dir",
        required=True,
        help="Directory containing PDFs",
    )

    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSONL output",
    )

    args = parser.parse_args()

    ingest_directory(
        args.input_dir,
        args.output_dir,
    )
