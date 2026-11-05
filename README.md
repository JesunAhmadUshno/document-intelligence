# document-intelligence

Applied AI pipelines: OCR plus LLM extraction, per-field confidence, an eval harness, a review queue.

Status: Learn DONE (2026-11-05, ROADMAP-V3-BATCH). Level 1 is built, tested, and measured below. Build and Deep are not started.
Project: P16. Fleet node: Dell R610. Wave: Wave 6. Learn was run on the Muse VM (CPU), not the Dell R610; see the level README for the named deduction.

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

## Novelty

PROPOSED. See NOVELTY.md. The novelty text is a draft until the Jev claim_check gate passes on it.

## License

Code: Apache-2.0 (see LICENSE). Tutorials: CC BY 4.0. Ruled in D-V3-11, 2026-11-04.
