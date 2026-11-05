# DEEP-SPEC: Level 3, Deep: document-intelligence (P16)

Written first, before the Deep code, per the task order.
Compressed Deep under the December Compression Protocol:
the single hardest capability in the SPEC Deep scope,
built, tested, and measured. The rest of the v2 Deep scope
goes into the repo root ROADMAP.md as the named v1.1
backlog.

## Scope from SPEC.md

SPEC Deep text: Deep adds per-field confidence scores, an
eval harness, and a review queue for low-confidence items.
Learn shipped a stated confidence rule and a queue list, and
Build shipped the eval harness over 32 documents, but no
level has measured whether the confidence scores mean what
they claim. That measurement is the hardest capability and
is this level:

Per-field confidence calibration against the Build eval,
with the review queue measured.

## What is built

1. Calibration (calibration.py). The Build pipeline runs
   over its own 32-document eval, unchanged, so Deep numbers
   compare directly with Build numbers. Every extracted
   field (32 documents x 5 fields = 160) becomes one item:
   document id, field, stated confidence, extracted value,
   ground truth, and a correct flag (exact match; a
   correctly detected absence counts as correct, as in
   Learn and Build).
2. Bands. The confidence rule uses exactly four stated
   values, so the bands are those values: 0.00, 0.60, 0.80,
   and 1.00. No binning choice is hidden. Per band: count,
   correct count, accuracy, mean confidence (the band value
   itself), and the absolute gap |accuracy - confidence|.
   Per field: overall accuracy, and accuracy inside each
   band that field uses.
3. Calibration error. Expected calibration error (ECE)
   over the bands, stated formula:

       ECE = sum over bands b of (n_b / N) * |acc_b - conf_b|

   where n_b is the band count, N = 160, acc_b is the band
   accuracy, and conf_b is the band confidence value.
   A Brier score over the same items is reported as a
   secondary measure: mean of (confidence - outcome)^2,
   outcome 1 when correct and 0 when wrong.
4. Review queue, measured. A threshold sweep over the
   candidate flag rules (flag confidence below 0.60, below
   0.80 which is the Learn rule, and below 1.00). For each
   rule: fields flagged, review burden (fields flagged /
   160), documents flagged (any flagged field), errors
   captured, error capture rate (errors captured / total
   errors), and flagged-but-correct count. The recommended
   threshold is the lowest-burden rule in the sweep that
   captures every error, and the README verdict states what
   the evidence does and does not support.
5. Verdict. The Deep README carries a written verdict on
   whether the confidence scores are trustworthy as
   probabilities, grounded only in the measured tables.

## Named substitutions (honest, stated everywhere)

- No OCR engine is available on this VM (`which tesseract`
  returns nothing, checked 2026-11-05 at Build) and no LLM
  is available either. Both remain named substitutions from
  Build: the input is synthetic plain text in the layout an
  OCR step would produce, and extraction is rule-based. No
  claim is made about images, scans, PDFs, or LLM
  extraction, and Deep calibrates the rule-based scores
  only.
- Assigned node: the Dell R610. This level runs on the
  Muse VM (CPU, Python standard library only), as Learn
  and Build did, and that costs a grade deduction named in
  the level README. No live R610 capture is claimed.
- Documents are synthetic, authored for this project, with
  invented vendor names. No real document is used.
- The eval set is NOT extended. Extending corpus.py would
  change every Build number and break direct comparison
  with the Build eval, so Deep measures the same 32
  documents and 160 fields. The small error count that
  follows from this (2 errors) is named as a limit and a
  grade deduction, not hidden.

## Acceptance

- Full test suite passes: Learn tests, Build tests, the
  new Deep tests, and the scaffold smoke test. All prior
  tests (40) must still pass.
- results_deep.json is deterministic across two runs.
- Every number in the Deep README is recomputed from
  results_deep.json or by the calibration code, never hand
  typed from memory. The unit tests carry hand-computed
  expectations for the band table, the ECE, and the queue.
- Root README and DOSSIER.md are updated to Deep ship
  state, and ROADMAP.md at repo root carries the rest of
  the v2 Deep scope as the named v1.1 backlog.
- One exact main results claim paragraph in the Deep
  README goes through the Jev claim_check gate.
- No em dash in any touched file.
