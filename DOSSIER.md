# DOSSIER: document-intelligence (P16)

Written under the documentation and publishing standard (past, present, future). Updated at ship time. v1 was 2026-11-04; this update is the v1.0 ship state, 2026-11-05.

## Past

Prior art for this project is named in NOVELTY.md (document AI services and OCR pipelines). The history of the problem, the key papers and systems, and what was tried before are recorded in the Roadmap v2 section text in SPEC.md and will be expanded with dated sources at the project's wave, before Build opens.

## Present

Current demand evidence: hiring value 4 of 5 (Mistral preferred, FDE roles at Mistral and OpenAI) [confirmed, fleet and scoring pass 2026-11-04; for P23 to P29, the decision pack 2026-11-04]. The Round 3 research (2026-11-04) found the market centre at post-training, evals, environments, and inference depth [confirmed as the research finding; the report is at ~/workspace/research_notes/roadmap-v3-revaluation-research-20261104-0949/report.md]. Tools and versions are pinned at Build time, not in this v1.

Ship state at v1.0 (2026-11-05, measured, Muse VM, Python 3.12, synthetic plain-text documents only, no OCR and no LLM at any level):

- Learn DONE: rule-based extraction over 8 synthetic documents, 38 of 40 fields correct (0.9500), review queue of 5 entries. Grade 8,700 of 10,000. See level-1-learn/README.md.
- Build DONE: pipeline over 32 synthetic documents (16 invoices, 8 forms, 8 receipts), 158 of 160 fields correct (0.9875), 65 of 65 table rows and 260 of 260 cells correct, 15 of 16 cross-document QA questions correct. Grade 7,650 of 10,000. Jev claim_check on the main Build claim: REVIEW (jev-1.13.0). See level-2-build/README.md.
- Deep DONE (compressed Deep, December Compression Protocol): per-field confidence calibration over the unchanged Build eval, with the review queue measured. Band accuracies: 0.8000 at confidence 0.00 (8 of 10), 1.0000 at 0.60 (4 of 4), 1.0000 at 0.80 (47 of 47), 1.0000 at 1.00 (99 of 99). Expected calibration error 0.1187, Brier score 0.0658. A review queue flagging confidence below 0.60 flags 10 of 160 fields (burden 0.0625) across 10 of 32 documents and captures both field errors (capture rate 1.0000). Verdict in level-3-deep/README.md: the confidence values are route labels, useful as a ranking for review, not trustworthy as probabilities; the 0.00 band pools 8 correctly detected absences with the 2 errors. Grade 7,450 of 10,000. Jev claim_check on the main Deep claim: REVIEW (jev-1.13.0, supported noul 0.36, 1,233 input tokens). Tests at ship: 52 unit tests passed plus the scaffold smoke test. See level-3-deep/README.md and level-3-deep/DEEP-SPEC.md.

Named substitutions carried at every level: no OCR engine and no LLM exist on this VM, so input is synthetic plain text in OCR layout and extraction is rule-based; no claim is made about images, scans, PDFs, or LLM extraction. All levels ran on the Muse VM, not the assigned Dell R610, and each level README names that deduction.

## Future

Open problems and the project's next steps sit in the Deep level scope in SPEC.md. Any forecast about this field is [unverified] unless a dated primary source is added here at the wave update.

The v1.1 backlog is ROADMAP.md at repo root: a larger and real document eval, OCR and LLM paths when a free route is verified, held-out threshold validation, a human review workflow with timing, per-kind calibration cuts, table and QA confidence, and a Dell R610 fleet run. Nothing in ROADMAP.md is built or claimed at v1.0.
