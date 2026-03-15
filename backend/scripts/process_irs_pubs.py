#!/usr/bin/env python3
"""
Process IRS publication PDFs from raw/tax into tax_knowledge.jsonl format.
- Extracts text with pdfplumber
- Chunks into 300-500 word segments
- Adds metadata: doc_id, category, publication, section
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
RAW_TAX = PROJECT_ROOT / "raw" / "tax"
CORPUS_PATH = PROJECT_ROOT / "backend" / "data" / "corpus" / "tax_knowledge.jsonl"

# PDF filename -> (publication title, category)
PUB_CONFIG = {
    "p17.pdf": ("IRS Pub 17 (Your Federal Income Tax)", "federal_income"),
    "p550.pdf": ("IRS Pub 550 (Investment Income & Expenses)", "capital_gains"),
    "p590a.pdf": ("IRS Pub 590-A (IRA Contributions)", "retirement_accounts"),
    "p590b.pdf": ("IRS Pub 590-B (IRA Distributions)", "retirement_accounts"),
    "p523--2025.pdf": ("IRS Pub 523 (Selling Your Home)", "real_estate"),
    "p526.pdf": ("IRS Pub 526 (Charitable Contributions)", "charitable_giving"),
}

MIN_WORDS = 300
MAX_WORDS = 500
# Set to a positive int to cap chunks per PDF (e.g. 6 for ~30-40 total docs); None = use full publication
MAX_CHUNKS_PER_PUB = None

# Patterns to remove from extracted PDF text (IRS production metadata)
CLEAN_PATTERNS = [
    r"Userid:.*?Print\s*",
    r"Fileid:.*?\d{4}\s*",
    r"The type and rule above prints on all proofs.*?MUST be removed before printing\.\s*",
    r"Page \d+ of \d+\s*",
    r"\d{2}:\d{2} - \d{2}-[A-Za-z]{3}-\d{4}\s*",
]


def clean_extracted_text(text: str) -> str:
    """Remove common IRS PDF metadata and normalize whitespace."""
    for pat in CLEAN_PATTERNS:
        text = re.sub(pat, " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_text_from_pdf(pdf_path: Path) -> list[tuple[int, str]]:
    """Extract text per page. Returns list of (page_num, text)."""
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
    """
    Split combined page text into 300-500 word chunks.
    Returns list of (chunk_text, section_label, page_range).
    """
    # Build word index boundaries per page: (page_num, word_count_after_this_page)
    word_count = 0
    page_word_ends = []  # (page_num, cumulative_word_count)
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

        # Page range from word indices: which pages contain chunk's first and last word
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
    """Get next doc_id number from existing corpus (e.g. 13 if last is tax_012)."""
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
            m = re.match(r"tax_(\d+)", doc_id)
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
        # Single short doc
        docs = [
            {
                "doc_id": f"tax_{start_doc_id:03d}",
                "category": category,
                "publication": publication,
                "section": f"Pages 1-{pages[-1][0]}",
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
            "doc_id": f"tax_{start_doc_id + i:03d}",
            "category": category,
            "publication": publication,
            "section": f"{chunk_label}; {page_range}",
            "text": text,
        })
    return docs, start_doc_id + len(docs)


def main():
    append = CORPUS_PATH.exists()
    next_id = get_next_doc_id(CORPUS_PATH)

    all_new = []
    for filename, (publication, category) in PUB_CONFIG.items():
        pdf_path = RAW_TAX / filename
        if not pdf_path.exists():
            print(f"Skip (not found): {filename}")
            continue
        print(f"Processing {filename} -> {publication} ...")
        docs, next_id = process_pdf(pdf_path, publication, category, next_id)
        print(f"  -> {len(docs)} chunks")
        all_new.extend(docs)

    if not all_new:
        print("No documents produced. Check raw/tax PDFs.")
        return

    # Append to corpus
    mode = "a" if append else "w"
    with open(CORPUS_PATH, mode, encoding="utf-8") as f:
        for doc in all_new:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")

    print(f"Wrote {len(all_new)} new documents to {CORPUS_PATH} (total new: {len(all_new)})")


if __name__ == "__main__":
    main()
