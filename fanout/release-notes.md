# Release notes: document-intelligence

Compiled 2026-11-05 for the written fan-out set. Release links
verified with gh release list on 2026-11-05. Every number below
is from the level READMEs and results files in this repo.

## v1.0: document-intelligence (Learn, Build, Deep)

Release: https://github.com/JesunAhmadUshno/document-intelligence/releases/tag/v1.0
Date: 2026-11-05

Compressed Deep: per-field confidence calibration over the
unchanged Build eval (32 synthetic documents, 160 fields,
accuracy 0.9875), with the review queue measured.

- Band accuracies: 0.8000 at confidence 0.00 (8 of 10), 1.0000
  at 0.60 (4 of 4), 1.0000 at 0.80 (47 of 47), 1.0000 at 1.00
  (99 of 99).
- Expected calibration error 0.1187, Brier score 0.0658.
- Review queue below 0.60: 10 of 160 fields flagged (burden
  0.0625), 10 of 32 documents, both errors captured (2 of 2,
  capture rate 1.0000).
- Verdict: confidence values are route labels, not trustworthy
  probabilities. The 0.00 band pools 8 correct receipt due-date
  absences with the 2 errors.
- Tests: 52 unit tests passing (12 Deep, 19 Build, 21 Learn),
  plus the scaffold smoke test.
- Grade: Deep 7,450 of 10,000, with named deductions (synthetic
  documents only, no OCR and no LLM, Muse VM run, only 2
  errors, four discrete route labels, offline queue only).
- Scope: no OCR, no LLM, synthetic plain text only. The rest
  of the v2 Deep scope is the v1.1 backlog in ROADMAP.md.

## v0.5: P16 Build

Release: https://github.com/JesunAhmadUshno/document-intelligence/releases/tag/v0.5
Date: 2026-11-05

Pipeline over 32 synthetic documents (16 invoices, 8 forms, 8
receipts, 2 layout variants per type), in the layout an OCR step
would produce. No OCR, no LLM.

- Fields: 158 of 160 correct, accuracy 0.9875, mean confidence
  0.8688 (route rule, not a calibrated probability).
- Per-field accuracy: invoice_number 1.0000, date 0.9688,
  vendor 1.0000, total 0.9688, due_date 1.0000.
- Tables: 65 of 65 rows exactly correct, 260 of 260 cells
  correct, 0 extra rows.
- Cross-document QA: 15 of 16 questions correct (0.9375),
  answers from extracted records only, each citing document ids.
- Known failure: total spend across all documents answered
  11758.50 against a gold of 12108.50, because one document
  renders its total in words and the extractor misses it.
- Tests: 40 unit tests passing (19 Build, 21 Learn), plus the
  scaffold smoke test.
- Grade: Build 7,650 of 10,000.

## v0.1 Learn: document-intelligence

Release: https://github.com/JesunAhmadUshno/document-intelligence/releases/tag/v0.1
Date: 2026-11-05

Rule-based field extraction from synthetic plain-text documents,
with a per-field confidence score, an eval harness, and a review
queue. No OCR, no real documents, no LLM.

- Documents: 8 synthetic (7 invoices, 1 form), 5 fields each,
  40 fields total.
- Fields: 38 of 40 correct, accuracy 0.9500.
- Per-field accuracy: invoice_number 1.0000, date 0.8750,
  vendor 1.0000, total 0.8750, due_date 1.0000.
- Mean confidence 0.8800 (stated route rule, not a calibrated
  probability).
- Review queue: 5 entries (3 missing, 2 low confidence).
- Tests: 21 unit tests passing, plus the scaffold smoke test.
- Grade: Learn 8,700 of 10,000.
