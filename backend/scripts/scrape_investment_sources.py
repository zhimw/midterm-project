#!/usr/bin/env python3
"""
Scrape investment-domain content from Investopedia and Bogleheads Wiki.
Outputs documents in investment_knowledge.jsonl format (doc_id, category, text, source, url).
Target: 25-30 additional investment documents.

Usage:
  pip install beautifulsoup4 requests pyyaml
  python backend/scripts/scrape_investment_sources.py

Optional: --dry-run (print URLs only), --limit N (scrape first N sources), --delay SEC
"""

import json
import re
import sys
import time
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
    import yaml
except ImportError:
    print("Install: pip install beautifulsoup4 requests pyyaml")
    sys.exit(1)

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCES_PATH = Path(__file__).resolve().parent / "investment_sources.yaml"
CORPUS_PATH = PROJECT_ROOT / "backend" / "data" / "corpus" / "investment_knowledge.jsonl"

MIN_WORDS = 300
MAX_WORDS = 500
REQUEST_DELAY_SEC = 1.5
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def load_sources() -> list[dict]:
    with open(SOURCES_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("sources", [])


def get_next_doc_id(corpus_path: Path) -> int:
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


def clean_text(text: str) -> str:
    # Drop common page chrome
    for phrase in (
        "Table of Contents Expand Table of Contents ",
        "Table of Contents Expand ",
        "The Bottom Line ",
    ):
        text = text.replace(phrase, " ")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\n+", "\n", text)
    return text.strip()


def extract_investopedia(soup: BeautifulSoup) -> str:
    """Extract main article body from Investopedia (definition + sections, no TOC/author/sources)."""
    # Primary: the actual body content (terms pages use .article-body-content)
    selectors = [
        ".article-body-content",  # terms/articles: definition + sections only
        ".mntl-sc-page.article-body-content",
        "[data-article-body]",
        ".article-body",
        "#article-body",
        "main",
        "article",
    ]
    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            for tag in el.select("script, style, nav, .ad, .related, .mntl-sc-block-ad"):
                tag.decompose()
            t = el.get_text(separator=" ", strip=True)
            # Prefer content that has definition-style opening (e.g. "A growth stock is any share")
            if len(t.split()) >= 80:
                return clean_text(t)
    return ""


def extract_bogleheads(soup: BeautifulSoup) -> str:
    """Extract main content from Bogleheads MediaWiki."""
    content = soup.select_one("#mw-content-text .mw-parser-output") or soup.select_one("#bodyContent")
    if not content:
        return ""
    for tag in content.select("script, style, .navbox, .metadata, .reference, .mw-editsection"):
        tag.decompose()
    return clean_text(content.get_text(separator=" ", strip=True))


def extract_vanguard_fidelity(soup: BeautifulSoup) -> str:
    """Extract main content from Vanguard/Fidelity institutional pages."""
    for sel in ["main", "[role='main']", ".content-body", ".article-body", ".report-content", "article"]:
        el = soup.select_one(sel)
        if el:
            for tag in el.select("script, style, nav, header, footer, .ad, .related-links"):
                tag.decompose()
            t = el.get_text(separator=" ", strip=True)
            if len(t.split()) >= 40:
                return clean_text(t)
    return ""


def extract_cfainstitute(soup: BeautifulSoup) -> str:
    """Extract article body from CFA Institute insights/refresher readings."""
    for sel in ["main", "article", ".article-body", ".reading-content", "[role='main']", ".content"]:
        el = soup.select_one(sel)
        if el:
            for tag in el.select("script, style, nav, .sidebar, .related"):
                tag.decompose()
            t = el.get_text(separator=" ", strip=True)
            if len(t.split()) >= 40:
                return clean_text(t)
    return ""


def extract_body(url: str, soup: BeautifulSoup) -> str:
    if "investopedia.com" in url:
        return extract_investopedia(soup)
    if "bogleheads.org" in url:
        return extract_bogleheads(soup)
    if "vanguard.com" in url:
        return extract_vanguard_fidelity(soup)
    if "fidelity.com" in url:
        return extract_vanguard_fidelity(soup)
    if "cfainstitute.org" in url:
        return extract_cfainstitute(soup)
    # Generic: prefer main/article
    for sel in ["main", "article", "#content"]:
        el = soup.select_one(sel)
        if el:
            for tag in el.select("script, style, nav"):
                tag.decompose()
            t = el.get_text(separator=" ", strip=True)
            if len(t.split()) >= 50:
                return clean_text(t)
    return clean_text(soup.get_text(separator=" ", strip=True))


def chunk_text(text: str, min_words: int = MIN_WORDS, max_words: int = MAX_WORDS) -> list[str]:
    words = text.split()
    if len(words) <= max_words:
        return [text] if words else []
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + max_words, len(words))
        segment = words[start:end]
        if len(segment) < min_words and end < len(words):
            end = min(start + min_words, len(words))
            segment = words[start:end]
        chunks.append(" ".join(segment))
        start = end
    return chunks


def fetch_and_extract(url: str, session: requests.Session) -> str:
    try:
        r = session.get(url, timeout=15)
        r.raise_for_status()
        r.encoding = r.apparent_encoding or "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")
        return extract_body(url, soup)
    except Exception as e:
        print(f"  Error: {e}")
        return ""


def main():
    import argparse
    p = argparse.ArgumentParser(description="Scrape investment sources into investment_knowledge.jsonl")
    p.add_argument("--dry-run", action="store_true", help="Only list URLs")
    p.add_argument("--limit", type=int, default=None, help="Max number of sources to scrape")
    p.add_argument("--delay", type=float, default=REQUEST_DELAY_SEC, help="Delay between requests (sec)")
    args = p.parse_args()

    sources = load_sources()
    if args.limit:
        sources = sources[: args.limit]
    print(f"Loaded {len(sources)} sources from {SOURCES_PATH.name}")

    if args.dry_run:
        for s in sources:
            print(s["url"], "->", s["category"])
        return

    next_id = get_next_doc_id(CORPUS_PATH)
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    new_docs = []

    for i, src in enumerate(sources):
        url = src["url"]
        category = src["category"]
        title = src.get("title", "")
        if "investopedia.com" in url:
            domain = "investopedia"
        elif "bogleheads.org" in url:
            domain = "bogleheads"
        elif "vanguard.com" in url:
            domain = "vanguard"
        elif "fidelity.com" in url:
            domain = "fidelity"
        elif "cfainstitute.org" in url:
            domain = "cfainstitute"
        else:
            domain = "other"
        print(f"[{i+1}/{len(sources)}] {url[:60]}...")
        text = fetch_and_extract(url, session)
        time.sleep(args.delay)

        if not text or len(text.split()) < 30:
            print("  -> Skipped (too little text)")
            continue

        chunks = chunk_text(text)
        for j, chunk in enumerate(chunks):
            doc = {
                "doc_id": f"inv_{next_id:03d}",
                "category": category,
                "source": domain,
                "publication": title,
                "url": url,
                "text": chunk,
            }
            new_docs.append(doc)
            next_id += 1
        print(f"  -> {len(chunks)} doc(s)")

    if not new_docs:
        print("No documents extracted. Check network and selectors.")
        return

    append = CORPUS_PATH.exists()
    mode = "a" if append else "w"
    with open(CORPUS_PATH, mode, encoding="utf-8") as f:
        for doc in new_docs:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")
    print(f"Wrote {len(new_docs)} documents to {CORPUS_PATH} (append={append})")


if __name__ == "__main__":
    main()
