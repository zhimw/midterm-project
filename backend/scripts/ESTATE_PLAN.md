# Estate & Trust Domain Enhancement Plan

## Objective

Expand the estate and trust knowledge corpus (`backend/data/corpus/estate_knowledge.jsonl`) with high-quality, structured documents covering trust types, estate and gift tax rules, probate, GST, powers of attorney, and healthcare directives. Target: **25–30 additional documents** (current corpus has est_001–est_012).

---

## Sources

| Source | Use | Notes |
|--------|-----|--------|
| **American Bar Association** | Estate planning guides, wills, trusts, POA, probate, healthcare directives | [Real Property, Trust & Estate Section](https://www.americanbar.org/groups/real_property_trust_estate/resources/estate-planning/), [Wills & Estates (public)](https://www.americanbar.org/groups/public_education/resources/law_issues_for_consumers/estate/) |
| **Nolo.com** | Trust explanations (revocable, irrevocable, ILIT, GRAT, CRT, Dynasty), probate avoidance, POA | Simple, consumer-friendly; good for definitions and mechanics |
| **Estate Planning Councils** | Best practices, planning frameworks | Often PDFs or member content; prefer manual curation or summaries |
| **Law school outlines / treatises** | Trusts & estates basics, GST, formal rules | Use for accuracy; may require manual extraction from PDFs or licensed content |

---

## Topics to Cover

### Trust types
- **Revocable** living trusts (control, probate avoidance, no estate tax benefit)
- **Irrevocable** trusts (estate removal, asset protection)
- **ILIT** (Irrevocable Life Insurance Trust)
- **GRAT** (Grantor Retained Annuity Trust)
- **CRT** (Charitable Remainder Trust), **CLT** (Charitable Lead Trust)
- **Dynasty** trusts (multi-generation, GST exemption)
- **QPRT** (Qualified Personal Residence Trust) — already referenced in est_003

### Estate & gift tax
- **Estate tax exemption** history (e.g., 2024: $13.61M per person; $27.22M married; **sunset after 2025** to ~$5M+ inflation)
- **Gift tax** rules: annual exclusion (e.g., $18,000/recipient 2024), lifetime exemption, present-interest requirement, direct tuition/medical
- **Portability** of unused exemption between spouses (election)

### Probate & administration
- **Probate** process (court-supervised, public, timeline)
- **Avoiding probate**: living trusts, TOD/POD, joint ownership, small-estate procedures

### Generation-skipping transfer tax (GST)
- GST tax rate (40%), exemption (aligned with estate exemption), skip persons, dynasty trust use

### Incapacity & directives
- **Power of attorney** types: durable financial POA, durable healthcare POA (proxy/surrogate)
- **Healthcare directives**: living will, advance directive, healthcare proxy; relationship to POA

### Optional / already in corpus
- Special needs trusts, guardianship, business succession (est_007–est_012) — add only if new sources add value.

---

## Extraction Method

1. **Web scraping**  
   - Use **BeautifulSoup** (and optionally **Selenium** for JS-heavy or login-walled pages).  
   - Script: `scrape_estate_sources.py` (or extend a shared scraper) reading from `estate_sources.yaml`.  
   - Same pattern as investment: fetch HTML, extract main content (e.g. article body), clean, chunk into ~300–500 word segments, append to `estate_knowledge.jsonl` with `doc_id` (est_013+), `category`, `source`, `url`, `text`.

2. **Manual curation**  
   - For PDFs (ABA forms, council white papers, law outlines), IRS publications, or paywalled content: summarize or extract key sections into 300–500 word JSONL entries.  
   - Use `ESTATE_CURATION.md` (see below) for schema and examples.

3. **Deduplication**  
   - Before appending, check that new text does not duplicate existing est_001–est_012 (e.g., by category + key terms).  
   - Prefer adding only when the new doc adds distinct rules, examples, or context.

---

## Target Output

- **Corpus file:** `backend/data/corpus/estate_knowledge.jsonl`
- **Schema (per line):**  
  `{"doc_id": "est_XXX", "category": "<topic>", "text": "...", "source": "aba|nolo|manual|...", "publication": "<title>", "url": "<optional>"}`
- **Categories:** Use existing and new as needed, e.g.  
  `revocable_trusts`, `irrevocable_trusts`, `ilit`, `grat`, `crt`, `dynasty_trust`, `estate_tax`, `gift_tax`, `probate`, `gst`, `power_of_attorney`, `healthcare_directive`, etc.
- **Count:** 25–30 additional documents so the estate corpus is comparable in depth to the investment corpus.

---

## Files to Create / Use

| File | Purpose |
|------|--------|
| `backend/scripts/estate_sources.yaml` | URL list and metadata for scrapable pages (ABA, Nolo, etc.) |
| `backend/scripts/scrape_estate_sources.py` | Scraper for estate_sources.yaml → estate_knowledge.jsonl (reuse or mirror scrape_investment_sources.py) |
| `backend/scripts/ESTATE_CURATION.md` | Instructions and schema for manual curation and PDF summarization |
| `backend/data/corpus/estate_knowledge.jsonl` | Final corpus (append new docs; existing est_001–est_012 kept) |

---

## Execution Order

1. Add `estate_sources.yaml` with URLs for ABA, Nolo (trusts, probate, POA, healthcare, gift/estate tax).
2. Implement or adapt scraper; run and validate on a few URLs; then full run.
3. Manually add 5–10 high-value items from PDFs or non-scrapable sources using ESTATE_CURATION.md.
4. Review corpus for duplicates and gaps; assign consistent categories; re-index RAG/vector store if applicable.
