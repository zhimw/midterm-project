#!/usr/bin/env python3
"""
Process investment PDFs from raw/investment into investment_knowledge.jsonl format.
- Extracts text with pdfplumber (charts/graphs are not extracted; text only)
- Chunks into 300-500 word segments
- Adds metadata: doc_id, category, publication, section, source

Usage:
  python backend/scripts/process_investment_pubs.py
"""

import json
import re
import sys
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("Install pdfplumber: pip install pdfplumber")
    sys.exit(1)

# Paths relative to project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_INVESTMENT = PROJECT_ROOT / "raw" / "investment"
CORPUS_PATH = PROJECT_ROOT / "backend" / "data" / "corpus" / "investment_knowledge.jsonl"

# PDF filename (exact match under raw/investment) -> (publication title, category)
PUB_CONFIG = {
    "the-vanguard-asset-allocation-model.pdf": (
        "The Vanguard Asset Allocation Model",
        "asset_allocation",
    ),
    "2025_Diversification_Landscape.pdf": (
        "2025 Diversification Landscape (Morningstar)",
        "asset_allocation",
    ),
    "Fidelity- A strategic allocator's guide to productivity and profits.PDF": (
        "Fidelity: A Strategic Allocator's Guide to Productivity and Profits",
        "asset_allocation",
    ),
    "Fidelity - Capital market assumptions- A comprehensive global approach for the next 20 years.PDF": (
        "Fidelity Capital Market Assumptions (20-Year Global Approach)",
        "asset_allocation",
    ),
}

MIN_WORDS = 300
MAX_WORDS = 500
MAX_CHUNKS_PER_PUB = None

# Patterns to remove from extracted PDF text (common report metadata)
CLEAN_PATTERNS = [
    r"Page \d+ of \d+\s*",
    r"\d{2}:\d{2} - \d{2}-[A-Za-z]{3}-\d{4}\s*",
    r"©\d{4}.*?\.?\s*",
]


def clean_extracted_text(text: str) -> str:
    """Remove common PDF metadata and normalize whitespace."""
    for pat in CLEAN_PATTERNS:
        text = re.sub(pat, " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_text_from_pdf(pdf_path: Path) -> list[tuple[int, str]]:
    """Extract text per page. Returns list of (page_num, text). Charts/graphs are not extracted."""
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text and text.strip():
                text = clean_extracted_text(text)
                if text:
                    pages.append((i, text))
    return pages


def chunk_text(
    pages: list[tuple[int, str]],
    publication: str,
    min_words: int = MIN_WORDS,
    max_words: int = MAX_WORDS,
) -> list[tuple[str, str, str]]:
    """Split combined page text into 300-500 word chunks. Returns (chunk_text, section_label, page_range)."""
    word_count = 0
    page_word_ends = []
    for pn, text in pages:
        n = len(text.split())
        word_count += n
        page_word_ends.append((pn, word_count))

    words = []
    for _, text in pages:
        words.extend(text.split())
    total_words = len(words)

    chunks = []
    start = 0
    chunk_index = 0

    while start < total_words:
        end = min(start + max_words, total_words)
        segment = words[start:end]
        if len(segment) < min_words and end < total_words:
            end = min(start + min_words, total_words)
            segment = words[start:end]

        chunk_text_str = " ".join(segment)
        if not chunk_text_str.strip():
            start = end
            continue

        page_start = pages[0][0]
        page_end = pages[-1][0]
        for pn, cum in page_word_ends:
            if start < cum:
                page_start = pn
                break
        for pn, cum in page_word_ends:
            if end <= cum:
                page_end = pn
                break

        if page_start == page_end:
            section = f"Pages {page_start}"
        else:
            section = f"Pages {page_start}-{page_end}"

        chunks.append((chunk_text_str, section, f"Chunk {chunk_index + 1}"))
        chunk_index += 1
        start = end

    return chunks


def get_next_doc_id(corpus_path: Path) -> int:
    """Get next doc_id from existing investment corpus (e.g. 42 if last is inv_041)."""
    if not corpus_path.exists():
        return 1
    max_id = 0
    with open(corpus_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            doc_id = obj.get("doc_id", "")
            m = re.match(r"inv_(\d+)", doc_id)
            if m:
                max_id = max(max_id, int(m.group(1)))
    return max_id + 1


def process_pdf(
    pdf_path: Path,
    publication: str,
    category: str,
    start_doc_id: int,
) -> tuple[list[dict], int]:
    """Process one PDF; return list of doc dicts and next doc_id."""
    pages = extract_text_from_pdf(pdf_path)
    if not pages:
        return [], start_doc_id

    combined = " ".join(t[1] for t in pages)
    words = combined.split()
    if len(words) < MIN_WORDS:
        docs = [
            {
                "doc_id": f"inv_{start_doc_id:03d}",
                "category": category,
                "publication": publication,
                "section": f"Pages 1-{pages[-1][0]}",
                "source": "pdf",
                "text": combined,
            }
        ]
        return docs, start_doc_id + 1

    chunks = chunk_text(pages, publication)
    if MAX_CHUNKS_PER_PUB is not None:
        chunks = chunks[:MAX_CHUNKS_PER_PUB]
    docs = []
    for i, (text, page_range, chunk_label) in enumerate(chunks):
        docs.append({
            "doc_id": f"inv_{start_doc_id + i:03d}",
            "category": category,
            "publication": publication,
            "section": f"{chunk_label}; {page_range}",
            "source": "pdf",
            "text": text,
        })
    return docs, start_doc_id + len(docs)


def main():
    if not RAW_INVESTMENT.exists():
        print(f"Directory not found: {RAW_INVESTMENT}")
        return

    append = CORPUS_PATH.exists()
    next_id = get_next_doc_id(CORPUS_PATH)

    all_new = []
    for filename, (publication, category) in PUB_CONFIG.items():
        pdf_path = RAW_INVESTMENT / filename
        if not pdf_path.exists():
            print(f"Skip (not found): {filename}")
            continue
        print(f"Processing {filename} -> {publication} ...")
        docs, next_id = process_pdf(pdf_path, publication, category, next_id)
        print(f"  -> {len(docs)} chunks")
        all_new.extend(docs)

    if not all_new:
        print("No documents produced. Check raw/investment PDFs and PUB_CONFIG.")
        return

    mode = "a" if append else "w"
    with open(CORPUS_PATH, mode, encoding="utf-8") as f:
        for doc in all_new:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")

    print(f"Wrote {len(all_new)} new documents to {CORPUS_PATH} (total new: {len(all_new)})")


if __name__ == "__main__":
    main()
