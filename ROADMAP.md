# ROADMAP: document-intelligence (P16), v1.1 backlog

Status at v1.0 (2026-11-05): Learn, Build, and compressed
Deep are DONE. Compressed Deep (December Compression
Protocol) built the single hardest capability in the SPEC
Deep scope: per-field confidence calibration against the
Build eval, with the review queue measured. Everything in
the v2 Deep scope that compressed Deep did not build is
listed here as the named v1.1 backlog. Nothing below is
built, and nothing below is claimed.

## v1.1 backlog (named, not built)

1. Larger eval set. More documents per type, more layout
   variants, and more authored hard cases, so band counts
   and the error set are large enough for capture rates
   and band accuracies to carry weight. The Deep threshold
   recommendation rests on 2 errors at v1.0.
2. Real documents. A small set of real invoices, forms,
   and receipts with hand-labelled ground truth, handled
   under a stated privacy rule, to test whether errors
   stay in the lowest confidence band off the authored
   corpus.
3. OCR path. An OCR engine in the pipeline when a free
   route is verified, with the same eval harness scoring
   OCR output, and calibration measured on OCR confidence
   where the engine provides one. At v1.0 there is no OCR:
   it is a named substitution in every level.
4. LLM extraction path. An LLM extractor beside the rules
   when a free route is verified, scored by the same
   harness, with its confidence (stated or derived)
   calibrated the same way. At v1.0 there is no LLM: it
   is a named substitution in every level.
5. Held-out threshold validation. Split a larger eval
   into a selection set and a held-out set, choose the
   review threshold on the first, and report capture and
   burden on the second, removing the same-eval selection
   bias named in the Deep README.
6. Recalibration, only if the data supports it. A fitted
   map from route label to measured accuracy, validated
   on held-out data. At v1.0 no map is fitted: 160 fields
   with 2 errors cannot support one.
7. Human review workflow. The queue as a working review
   surface: a reviewer confirms or corrects flagged
   fields, corrections feed the record, and review time
   per field and reviewer accuracy are measured. At v1.0
   the queue is measured offline in fields and documents,
   not minutes.
8. Per-kind and per-variant calibration cuts. Calibration
   reported separately for invoices, forms, and receipts
   and for variants A and B, once the eval is large
   enough for the cuts to mean something.
9. Table and QA confidence. Confidence and calibration
   for table rows and QA answers, not only the 5 fields.
   At v1.0 tables and QA carry no confidence score.
10. Fleet run. The full pipeline and calibration run on
    the assigned Dell R610 with a live capture, closing
    the run-location deduction carried by all three
    levels at v1.0.

## Standing limits that v1.1 does not erase

- No OCR or LLM result may be reported until that path
  actually runs; the substitutions stay named until then.
- Synthetic results and real-document results are always
  reported separately, never pooled.
- The publicity and fan-out set for v1.0 is prepared
  under the documentation and publishing standard; social
  posting follows the standing platform gates and is not
  part of this repo.
