# Research workflow
1. `POST /api/research` normalises crop/district (aliases) and month.
2. Verified data check: sufficient if a verified season exists in scope and ≥5 verified guide sections.
3. Cache check (`research_cache`, TTL 30 days) – including "insufficient" outcomes, so failures are not re-bought.
4. Duplicate prevention: active job with same `crop:district:month` key is returned.
5. Budget check (daily Serper/OpenAI limits, monthly USD). Then job queued; worker runs it.
6. Serper: query 1 targets `site:agritech.tnau.ac.in`; query 2 (broader) runs only if query 1 produced no useful trusted document. Search-engine redirect links (google.com/goto, bit.ly…) are rejected. Processing stops after 2 useful trusted documents (max 4 extractions). Candidates prioritised by trusted domain (tnau.ac.in, icar.gov.in, *.gov.in, *.ac.in …); URLs/titles that look like success stories, news, schemes, prices are skipped.
7. Fetch via SSRF-safe client (certificates are always verified – sites with expired certs are skipped). HTML/PDF → text. Pages mentioning the crop <3 times are skipped.
8. GPT-4o-mini extracts JSON with a verbatim `evidence_quote` and `general_guidance` flag.
9. Validation (AI output alone is never verification): quote must appear in the fetched text; every number in the value must appear in the quote; `general_guidance` must be true; applicability (district/state) must match.
10. Status: trusted domain + validated → `verified`; untrusted → `review_required`; conflicting values across sources → `review_required` with note; a verified value is never downgraded and a conflicting new value flags review.
10b. Structured months: validated `sowing_seasons`/`harvest_seasons` text is parsed by a deterministic month parser ("May - June and November – December" → May–Jun, Nov–Dec) into calendar season rows with the same verification status. Harvest months are paired only when the counts match; otherwise left empty.
11. Evidence rows (quote, source, applicability, validated flag) and sources (URL, title, retrieval date, hash) are stored. Job result lists sources, rejected counts, missing sections.
Limitations: "verified" means *institution page + exact supporting quote*, not expert review. Spot-check important records.

## Manual batch research
`cd backend && python research_batch.py --crops okra brinjal --yes` (dry run without `--yes`). Capped by `--max`, budgets and cache; ~$0.005–0.02/crop. Never runs automatically.
