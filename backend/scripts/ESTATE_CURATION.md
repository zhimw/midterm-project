# Estate & Trust Domain – Manual Curation

Use this when scraping is not possible (PDFs, paywalled content, ABA/law outlines) or to add high-value summaries. Each new line must be valid JSON matching the corpus schema. Append to `backend/data/corpus/estate_knowledge.jsonl`.

## Schema (one JSON object per line)

```json
{"doc_id": "est_XXX", "category": "category_name", "text": "Your extracted or summarized content (300–500 words).", "source": "manual", "publication": "Title of source"}
```

- **doc_id**: Next number after the last in the file (e.g. if last is est_020, use est_021).
- **category**: One of: `revocable_trusts`, `irrevocable_trusts`, `ilit`, `grat`, `crt`, `charitable_trusts`, `dynasty_trust`, `estate_tax`, `gift_tax`, `probate`, `gst`, `power_of_attorney`, `healthcare_directive`, `estate_planning_basics`, `testamentary_trusts`, or add new as needed.
- **text**: Plain text only; 300–500 words per document. For long PDFs, split by section.
- **source**: e.g. `"manual"`, `"aba"`, `"estate_council"`, `"law_outline"`.
- **publication**: Full title of the source (e.g. "ABA Guide to Wills and Estates").

## Suggested manual sources (PDFs / non-scrapable)

| Topic | Source | Notes |
|-------|--------|--------|
| Estate tax exemption & sunset | IRS Pub 559, or law firm summaries | 2024 $13.61M; sunset after 2025 to ~$5M+ |
| GST tax | IRS materials or law outline | 40% rate, exemption = estate exemption, skip persons |
| GRAT / ILIT mechanics | ABA RPTE, PLI, or outline | Formal requirements, Crummey, valuation |
| Estate planning best practices | Local Estate Planning Council white papers | Summarize key recommendations |
| Healthcare directives by state | State bar or aging agency PDFs | State-specific forms and rules |

## Append command (after creating `new_estate_lines.jsonl`)

```bash
cd backend
cat scripts/new_estate_lines.jsonl >> data/corpus/estate_knowledge.jsonl
```

Then re-run your RAG/vector index step so the estate module picks up the new documents.
