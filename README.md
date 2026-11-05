# document-intelligence

Applied AI pipelines: OCR plus LLM extraction, per-field confidence, an eval harness, a review queue.

Status: v1.0 SHIPPED (2026-11-05, ROADMAP-V3-BATCH). Learn, Build, and Deep (compressed Deep) are built, tested, and measured below. The rest of the v2 Deep scope is the named v1.1 backlog in ROADMAP.md.
Project: P16. Fleet node: Dell R610. Wave: Wave 6. All levels were run on the Muse VM (CPU), not the Dell R610; see the level READMEs for the named deductions.

## Start here

1. Read SPEC.md for scope and acceptance criteria.
2. Read DOSSIER.md for the past, present, and future of this problem (v1).
3. Read NOVELTY.md for the proposed novelty (DRAFT, pending the Jev claim_check gate).
4. Start at level-1-learn/README.md, then level-2-build, then level-3-deep.

## Level map

- Level 1, Learn: the core idea, built small and clean, with a teaching path.
- Level 2, Build: a real working system other people can run.
- Level 3, Deep: benchmarks, optimization, evaluation, hard cases.

## Benchmarks

Measured 2026-11-05 with level-1-learn/run_learn.py on the Muse VM, Python 3.12. The documents are synthetic plain text: no OCR, no LLM, no real documents.

| Test | Result |
| --- | --- |
| Learn documents | 8 synthetic documents (7 invoices, 1 form), 5 fields each, 40 fields total |
| Fields correct | 38 of 40 (overall accuracy 0.9500) |
| Per-field accuracy | invoice_number 1.0000, date 0.8750, vendor 1.0000, total 0.8750, due_date 1.0000 |
| Mean confidence | 0.8800 (stated rule: 1.00 primary label, 0.80 alternate label, 0.60 fallback, 0.00 missing) |
| Review queue | 5 entries (3 missing, 2 low confidence) |
| Unit tests | 21 passed, plus the scaffold smoke test |
| Determinism | results_learn.json identical across two runs (hash verified) |

## Build benchmarks

Measured 2026-11-05 with level-2-build/run_build.py on the Muse VM, Python 3.12. The documents are synthetic plain text in the layout an OCR step would produce: no OCR, no LLM, no real documents. See level-2-build/README.md and level-2-build/BUILD-SPEC.md for method and the named substitutions.

| Test | Result |
| --- | --- |
| Build documents | 32 synthetic documents (16 invoices, 8 forms, 8 receipts), 2 layout variants per type |
| Fields correct | 158 of 160 (overall accuracy 0.9875) |
| Per-field accuracy | invoice_number 1.0000, date 0.9688, vendor 1.0000, total 0.9688, due_date 1.0000 |
| Mean confidence | 0.8688 (Learn route rule, not a calibrated probability) |
| Table extraction | 65 of 65 rows exactly correct, 260 of 260 cells correct, 0 extra rows |
| Cross-document QA | 15 of 16 labelled questions correct (accuracy 0.9375), answers from extracted records only, each citing its document ids |
| QA known failure | Total spend across all documents: answered 11758.50 against a gold 12108.50, because one document renders its total in words and the extractor misses it |
| Unit tests | 40 passed (19 Build, 21 Learn), plus the scaffold smoke test |
| Determinism | results_build.json identical across two runs (hash verified) |

## Deep benchmarks

Measured 2026-11-05 with level-3-deep/run_deep.py on the Muse VM, Python 3.12, over the unchanged Build eval (same 32 synthetic documents, 160 fields). No OCR, no LLM, no real documents. See level-3-deep/README.md and level-3-deep/DEEP-SPEC.md for method, the verdict, and the named substitutions.

| Test | Result |
| --- | --- |
| Calibration bands (stated confidence: accuracy) | 0.00: 0.8000 (8 of 10), 0.60: 1.0000 (4 of 4), 0.80: 1.0000 (47 of 47), 1.00: 1.0000 (99 of 99) |
| Expected calibration error | 0.1187 (weighted absolute gap formula in DEEP-SPEC.md); Brier score 0.0658 |
| Review queue (flag confidence below 0.60) | 10 of 160 fields flagged (burden 0.0625), 10 of 32 documents, both errors captured (2 of 2, capture rate 1.0000) |
| Learn queue rule (below 0.80) | 14 fields flagged (burden 0.0875), same 2 of 2 errors captured |
| Verdict | Confidence values are route labels, not trustworthy probabilities: every non-zero band is underconfident, and the 0.00 band pools 8 correct absences with the 2 errors |
| Unit tests | 52 passed (12 Deep, 19 Build, 21 Learn), plus the scaffold smoke test |
| Determinism | results_deep.json identical across two runs (hash verified) |

## Novelty

PROPOSED. See NOVELTY.md. The novelty text is a draft until the Jev claim_check gate passes on it.

## License

Code: Apache-2.0 (see LICENSE). Tutorials: CC BY 4.0. Ruled in D-V3-11, 2026-11-04.
