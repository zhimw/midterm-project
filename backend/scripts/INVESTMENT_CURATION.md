# Investment Domain – Manual Curation

Use this when scraping fails or for PDFs (Vanguard/Fidelity white papers, CFA Institute). Each line you add must be valid JSON matching the corpus schema.

## Schema (one JSON object per line, append to `backend/data/corpus/investment_knowledge.jsonl`)

```json
{"doc_id": "inv_XXX", "category": "category_name", "text": "Your extracted or summarized content here (300–500 words per doc).", "source": "manual", "publication": "Title of paper or article"}
```

- **doc_id**: Use next number after the last in the file (e.g. if last is `inv_042`, use `inv_043`).
- **category**: One of: `equity_growth`, `equity_value`, `equity_small_cap`, `equity_international`, `bonds_government`, `bonds_corporate`, `bonds_municipal`, `bonds_duration`, `alternatives_reits`, `alternatives_commodities`, `alternatives_private_equity`, `risk_tolerance`, `asset_allocation`, `asset_location`, `modern_portfolio_theory`, `tax_loss_harvesting`, `portfolio_management`, or add new as needed.
- **text**: Plain text only; 300–500 words per document works well for retrieval. For long PDFs, split into multiple docs (e.g. one per section).
- **source**: e.g. `"manual"`, `"vanguard_whitepaper"`, `"cfa_institute"`.
- **publication**: Optional; full title of the source.

## Suggested manual sources (PDFs / when scrape fails)

| Topic | Source | Notes |
|-------|--------|--------|
| Asset allocation | Vanguard “Principles for investing success” | PDF; summarize key tables and allocation ranges |
| Risk tolerance | Fidelity / Vanguard risk tolerance questionnaires | Extract scoring rubrics and band descriptions |
| Tax-loss harvesting | Bogleheads wiki (if scrape fails) | Copy “Tax loss harvesting” and “Tax-efficient fund placement” text |
| MPT / portfolio basics | CFA Institute “Portfolio Management” readings | Summarize key definitions and formulas |
| Asset location | Vanguard “Asset location for tax-deferred and taxable accounts” | Tables: which assets in which account type |

### Vanguard / Fidelity white paper PDFs (asset allocation)

Use these with a PDF extraction script (e.g. pdfplumber like `process_irs_pubs.py`) or manual summarization:

- **Vanguard:** [The Vanguard Asset Allocation Model (PDF)](https://corporate.vanguard.com/content/dam/corp/research/pdf/the_vanguard_asset_allocation_model_an_investment_solution_for_active_passive_factor_portfolios.pdf)
- **Vanguard:** [Time-Varying Asset Allocation (PDF)](https://corporate.vanguard.com/content/dam/corp/research/pdf/time_varying_asset_allocation_vanguards_approach_to_dynamic_portfolios.pdf)
- **Vanguard:** [Constructing Return-Target Portfolios (PDF)](https://corporate.vanguard.com/content/dam/corp/research/pdf/constructing_return_target_portfolios.pdf)
- **Vanguard:** [Combining Active Managers (PDF)](https://corporate.vanguard.com/content/dam/corp/research/pdf/combining_active_managers_a_practical_approach.pdf)

## Append command (after creating a line in `new_inv_lines.jsonl`)

```bash
cd backend
cat scripts/new_inv_lines.jsonl >> data/corpus/investment_knowledge.jsonl
```

Then re-run your RAG/vector index step so the new documents are embedded.
