# Level 3, Deep: document-intelligence

Status: DONE (2026-11-05). Per-field confidence calibration
against the Build eval, with the review queue measured.
The Build pipeline runs over its own 32-document eval,
unchanged, and every one of the 160 extracted fields is
scored against ground truth and bucketed by its stated
confidence value. Calibration error is computed by a stated
formula, and a threshold sweep measures what the review
queue captures and what it costs. Python standard library
only. Compressed Deep under the December Compression
Protocol: this is the single hardest capability in the
SPEC Deep scope; the rest of the v2 Deep scope is the
named v1.1 backlog in the repo root ROADMAP.md.

## Honest scope line

There is NO OCR and NO LLM in this level, and both remain
named substitutions from Build (see DEEP-SPEC.md, written
before the code). No OCR engine is available on this VM
(`which tesseract` returns nothing, checked 2026-11-05 at
Build) and no LLM is available either. The input is
synthetic plain text in the layout an OCR step would
produce, and extraction is rule-based. Deep calibrates the
rule-based confidence scores only: no claim is made about
images, scans, PDFs, or LLM extraction, and no OCR or LLM
result is reported anywhere in this level. The assigned
Dell R610 was not used: the run was on the Muse VM, and
that costs a grade deduction below. The eval set is NOT
extended: extending the Build corpus would change every
Build number, so Deep measures the same 32 documents and
160 fields, and the small error count that follows (2
errors) is named as a limit below, not hidden.

## Method

1. Items (calibration.py). One item per extracted field:
   document id, field, stated confidence, extracted value,
   ground truth, correct flag (exact match; a correctly
   detected absence counts as correct, as in Learn and
   Build), and a missing flag.
2. Bands. The confidence rule uses exactly four stated
   values, so the bands are those values: 0.00, 0.60, 0.80,
   and 1.00. No binning choice is hidden. Per band: count,
   correct count, accuracy, and the absolute gap between
   accuracy and the band confidence value. Per field:
   overall accuracy and accuracy inside each band the
   field uses.
3. Calibration error. Expected calibration error over the
   bands, formula stated in DEEP-SPEC.md:

       ECE = sum over bands b of (n_b / N) * |acc_b - conf_b|

   with N = 160. The Brier score over the same items is a
   secondary measure: mean of (confidence - outcome)^2,
   outcome 1 when correct, 0 when wrong.
4. Review queue, measured. A sweep over three candidate
   flag rules: confidence below 0.60, below 0.80 (the
   Learn queue rule), and below 1.00. For each rule: fields
   flagged, review burden (fields flagged / 160),
   documents flagged (any flagged field), errors captured,
   error capture rate (errors captured / 2 total errors),
   and flagged-but-correct count. The recommended
   threshold is the lowest-burden rule that captures every
   error.
5. All arithmetic is computed by calibration.py and
   written to results_deep.json. Every number in this
   README is read from that file, and the unit tests carry
   hand-computed expectations for the band table, the ECE,
   the Brier score, and the queue.

## Run it

    python level-3-deep/run_deep.py
    python -m unittest discover -s tests -v
    python tests/test_smoke.py

The runner writes level-3-deep/results_deep.json
deterministically: run twice, identical file (verified
2026-11-05, sha256
c49f431c42abfcb1791bf03d03edb06d9a0ee1ffbc38cbc9932b75ac7882e7dc
on both runs).

## Results (measured 2026-11-05, Muse VM, Python 3.12)

Fields overall: 158 of 160 correct (accuracy 0.9875, the
Build result, unchanged), mean confidence 0.8688, total
errors 2 (B15 date and B16 total, both at confidence
0.00, both missing).

Calibration by confidence band:

| Band (stated confidence) | Fields | Correct | Accuracy | Gap |
| --- | --- | --- | --- | --- |
| 0.00 | 10 | 8 | 0.8000 | 0.8000 |
| 0.60 | 4 | 4 | 1.0000 | 0.4000 |
| 0.80 | 47 | 47 | 1.0000 | 0.2000 |
| 1.00 | 99 | 99 | 1.0000 | 0.0000 |

Expected calibration error: 0.1187. Hand check:
(10/160) x 0.8000 + (4/160) x 0.4000 + (47/160) x 0.2000
+ (99/160) x 0.0000 = 0.0500 + 0.0100 + 0.05875 + 0
= 0.11875, rounded to 0.1187 by the code. No band is
overconfident on this eval, so the ECE also equals the
overall accuracy minus the mean confidence:
0.9875 - 0.8688 = 0.1187. Brier score: 0.0658.

Per field, overall and by band:

| Field | Accuracy | By band (confidence: correct/count = accuracy) |
| --- | --- | --- |
| invoice_number | 1.0000 (32/32) | 0.80: 16/16 = 1.0000; 1.00: 16/16 = 1.0000 |
| date | 0.9688 (31/32) | 0.00: 0/1 = 0.0000; 1.00: 31/31 = 1.0000 |
| vendor | 1.0000 (32/32) | 0.60: 4/4 = 1.0000; 0.80: 12/12 = 1.0000; 1.00: 16/16 = 1.0000 |
| total | 0.9688 (31/32) | 0.00: 0/1 = 0.0000; 0.80: 11/11 = 1.0000; 1.00: 20/20 = 1.0000 |
| due_date | 1.0000 (32/32) | 0.00: 8/8 = 1.0000; 0.80: 8/8 = 1.0000; 1.00: 16/16 = 1.0000 |

Review queue threshold sweep:

| Flag rule | Fields flagged | Burden | Documents flagged | Errors captured | Capture rate | Flagged but correct |
| --- | --- | --- | --- | --- | --- | --- |
| confidence below 0.60 | 10 | 0.0625 | 10 | 2 of 2 | 1.0000 | 8 |
| confidence below 0.80 (Learn rule) | 14 | 0.0875 | 10 | 2 of 2 | 1.0000 | 12 |
| confidence below 1.00 | 61 | 0.3812 | 21 | 2 of 2 | 1.0000 | 59 |

Recommended queue (confidence below 0.60, which on this
four-value scale flags exactly the 0.00 fields): 10
entries, B15 date (missing, wrong), B16 total (missing,
wrong), and the due_date of all 8 receipts (B25 to B32,
extracted None, correct absences). A reviewer working
this queue sees both real errors and 8 absences to
confirm.

Unit tests: 52 passed (12 Deep, 19 Build, 21 Learn),
plus the scaffold smoke test.

## Verdict: are the confidence scores trustworthy?

No, not as probabilities, and the tables show why in
three separate ways.

1. Every non-zero band is underconfident. Fields scored
   0.60 are right 4 of 4 times, fields scored 0.80 are
   right 47 of 47 times, and fields scored 1.00 are right
   99 of 99 times. Read as probabilities, 0.60 and 0.80
   both understate the measured accuracy by a wide
   margin, and the ECE of 0.1187 is entirely this
   underconfidence: the gap between 0.9875 accuracy and
   0.8688 mean confidence.
2. The 0.00 band pools two opposite meanings. At field
   level, confidence 0.00 on due_date is 8 of 8 correct
   (receipts genuinely have no due date), while
   confidence 0.00 on date and total is 0 of 2 correct
   (real values the extractor missed). The pooled band
   accuracy of 0.8000 describes neither case. The value
   0.00 means "nothing matched", and whether that is an
   error depends on whether the field should exist, which
   the score itself does not say.
3. The scores are still useful as a ranking. Both errors
   sit at the lowest value, no error sits at 0.60 or
   above, and accuracy is monotone in the score on this
   eval. As route labels that sort fields for review,
   they work. As probabilities of correctness, they do
   not.

Threshold the evidence supports: flag confidence below
0.60. It captures both errors (capture rate 1.0000) at
the lowest burden in the sweep, 10 of 160 fields
(0.0625) across 10 of 32 documents. The Learn rule
(below 0.80) adds 4 reviews and captures no extra error,
and flagging below 1.00 adds 51 more reviews and still
captures no extra error. The honest limit on this
recommendation: it rests on 2 errors total. With so few
errors, the sweep cannot show that a 0.60 or 0.80 field
is never wrong; it only shows none was wrong here. The
threshold is the best supported by this eval, not a
proven safe line, and it should be re-measured on a
larger eval before it is trusted in production.

## Main results claim (exact paragraph for the Jev gate)

Deep of document-intelligence, 2026-11-05: over the same 32 synthetic plain-text documents and 160 fields as the Build eval, unchanged, with no OCR and no LLM, per-field confidence calibration by the four stated confidence values gave band accuracies of 0.8000 at 0.00 (8 of 10), 1.0000 at 0.60 (4 of 4), 1.0000 at 0.80 (47 of 47), and 1.0000 at 1.00 (99 of 99), an expected calibration error of 0.1187 by the stated weighted absolute gap formula, and a Brier score of 0.0658; a review queue flagging confidence below 0.60 flagged 10 of 160 fields (burden 0.0625) across 10 of 32 documents and captured both field errors (2 of 2, capture rate 1.0000), while the 0.00 band pools 8 correctly detected receipt due date absences with the 2 errors, so the confidence values are route labels and not trustworthy probabilities. The run was on the Muse VM, not the assigned Dell R610.

Jev gate on that paragraph: model jev-1.13.0, input tokens
1233, supported noul 0.36, route REVIEW (claim_check bands:
clear at 0.85 or above, block at or below 0.10). Spec and
results: hidden_files/jev-p16-deep-claim-spec-2026-11-05.json
and jev-p16-deep-claim-results-2026-11-05.json in the goal
workspace.

## Failure modes and limits

- Synthetic documents only: the same 32 authored
  documents as Build, with invented vendors. Real
  documents add layout noise and wording variety that
  could move errors into higher confidence bands, which
  this eval cannot see.
- No OCR and no LLM: the SPEC headline capabilities
  remain named substitutions (plain-text input in OCR
  layout, rule-based extraction). Calibration of a real
  OCR engine score or an LLM self-reported confidence is
  a different measurement and is not claimed.
- Only 2 errors: every capture rate and every low-band
  accuracy rests on tiny counts. The 0.60 band has 4
  fields and the error set has 2 items, so a capture rate
  of 1.0000 is a statement about this eval, not a bound
  on future errors.
- Four discrete route values, not a probability model:
  the calibration measures the Learn route rule (1.00
  primary, 0.80 alternate, 0.60 fallback, 0.00 missing).
  There is no learned scorer to recalibrate here; a
  recalibration map fitted on 160 fields with 2 errors
  would be curve fitting to noise, so none is fitted.
- The 0.00 band confound: pooled band accuracy mixes
  correct absences with real misses. Any consumer of the
  band table alone, without the per-field split, would
  misread the lowest band in both directions.
- Correct absence counts as correct: this follows Learn
  and Build, and it is what makes receipt due_date score
  1.0000 at confidence 0.00. Under a convention where an
  absence is not scored, the 0.00 band would read 0 of 2
  and the ECE would change. The convention is stated,
  not hidden.
- The queue is measured offline only: no human review
  workflow, review time, or reviewer accuracy is
  measured. Burden is counted in fields and documents,
  not minutes.
- Threshold fitted and tested on the same eval: the
  recommended threshold is chosen from the sweep over
  the same 160 fields it is then reported on. There is
  no held-out set, so the recommendation carries
  selection bias, named here rather than hidden.
- Run on the Muse VM, not the assigned Dell R610 fleet
  node. That costs a grade deduction, named below.

## Grade

Grade: 7,450 of 10,000 for this Deep level.

Deductions (they sum to 2,550):
- Synthetic documents only, the same 32 authored
  plain-text documents as Build, no real documents:
  minus 700.
- No OCR and no LLM: the SPEC headline capabilities are
  named substitutions, and Deep calibrates rule-based
  scores only: minus 800.
- Run on the Muse VM, not the assigned Dell R610 fleet
  node: minus 200.
- Only 2 errors and small bands (0.60 band has 4 fields):
  capture rates and band accuracies rest on tiny counts:
  minus 400.
- Confidence is four discrete route labels, not a
  learned probability: calibration is of the route rule,
  and no recalibration is fitted or validated: minus 300.
- Review queue measured offline only: no human review
  workflow, timing, or reviewer accuracy measured:
  minus 150.

## What remains (v1.1)

The rest of the v2 Deep scope sits in the repo root
ROADMAP.md as the named v1.1 backlog: a larger and real
document eval, calibration of OCR or LLM confidence when
a free route for either is verified, a held-out threshold
validation, and a human review workflow with timing.
