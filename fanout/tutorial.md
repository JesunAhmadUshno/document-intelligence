# Tutorial: P16 document-intelligence, course module

Module: P16-document-intelligence
By Jesun Ahmad Ushno
Date: 2026-11-05
License for this tutorial: CC BY 4.0. Code in the repo: Apache-2.0.

## What you will do

You will clone the document-intelligence repo, run all three
levels, run the test suite for each level, and read your own
results against the recorded v1.0 numbers. Every command below
exists in the repo as shipped at v1.0 and was verified by running
it in this fan-out cycle. The pipeline needs Python 3.11 or 3.12
and uses the standard library only. No model, no API, and no
credential are needed.

Two scope facts govern every step. First, there is NO OCR and
NO LLM in this project: every document is a synthetic plain-text
fixture in the layout an OCR step would produce, and extraction
is rule-based. Second, the confidence values are route labels
from a stated rule (1.00 primary labelled match, 0.80 alternate
labelled match, 0.60 unlabelled fallback, 0.00 nothing matched).
They are not probabilities, and Deep exists to prove that point
with numbers.

## Step 0: Clone and enter the repo

```text
git clone https://github.com/JesunAhmadUshno/document-intelligence.git
cd document-intelligence
```

Optional smoke check, before the levels:

```text
python -m unittest tests.test_layout -v
```

Expected: a line that says the scaffold smoke test passed, with
8 files present.

## Step 1: Level 1, Learn, extraction with a confidence rule

Read the Learn stage of REPORT.md first. It defines the five fields,
the confidence rule, the eval harness, and the review queue rule
(flag confidence below 0.80 or a missing value).

Run the Learn evaluator:

```text
python src/run_learn.py
```

Run the Learn tests:

```text
python -m unittest tests.test_learn_extraction -v
```

Read your results:

- The runner prints one line per document and writes
  results/results_learn.json.
- Expected summary on the shipped set: 38 of 40 fields correct
  across 8 documents, accuracy 0.9500, mean confidence 0.8800,
  review queue 5 entries.
- Per field: invoice_number 1.0000, date 0.8750, vendor 1.0000,
  total 0.8750, due_date 1.0000.
- The 2 misses are both in D08: its date is written out in words
  and its total is written in words, and neither matches a
  supported pattern.
- Expected tests: 21 tests, all passing.

If your summary differs, open results_learn.json and check the
per-document field table first. Each entry shows the extracted
value, the confidence, and the correct flag against ground truth.

## Step 2: Level 2, Build, pipeline, tables, and cross-document QA

Read the Build stage of REPORT.md and the Build plan in PROPOSAL.md
first. They define the 32-document corpus (16 invoices, 8 forms,
8 receipts, 2 layout variants per type), the table formats, and
the 9 typed QA question forms. Remember: the input is plain text
in OCR layout, not OCR output, and QA answers come from extracted
records only.

Run the Build pipeline:

```text
python src/run_build.py
```

Run the Build tests:

```text
python -m unittest tests.test_build_pipeline -v
```

Read your results:

- The runner prints the field, table, and QA summaries and
  writes results/results_build.json.
- Expected: 158 of 160 fields correct, accuracy 0.9875, mean
  confidence 0.8688; tables 65 of 65 rows and 260 of 260 cells
  correct, 0 extra rows; QA 15 of 16 correct, accuracy 0.9375.
- The one failed question is Q07, total spend across all
  documents: answered 11758.50 against a gold of 12108.50. The
  difference is exactly one document (B16, 350.00) whose total
  is written in words and missed by the extractor.
- Expected tests: 19 Build tests, all passing (40 unit tests in
  total with Learn).

## Step 3: Level 3, Deep, calibration and the review queue

Read the Deep stage of REPORT.md and the Deep plan in PROPOSAL.md first.
They state the ECE formula, the four confidence bands, and the
threshold sweep before any code runs.

Run the Deep calibration:

```text
python src/run_deep.py
```

Run the Deep tests:

```text
python -m unittest tests.test_deep_calibration -v
```

Read your results:

- The runner prints the band table, the ECE and Brier score, and
  the queue sweep, and writes results/results_deep.json.
- Expected bands: 0.00 accuracy 0.8000 (8 of 10), 0.60 accuracy
  1.0000 (4 of 4), 0.80 accuracy 1.0000 (47 of 47), 1.00 accuracy
  1.0000 (99 of 99). ECE 0.1187, Brier score 0.0658.
- Expected queue at the recommended rule (flag confidence below
  0.60): 10 fields flagged, burden 0.0625, 10 documents flagged,
  both errors captured (2 of 2, capture rate 1.0000).
- Expected tests: 12 Deep tests, all passing (52 unit tests in
  total, plus the scaffold smoke test).
- One caution on exact values: the exact ECE is 0.11875 and the
  exact mean confidence is 0.86875, both on a 4-place rounding
  boundary, so a Python 3.11 run can print the mean as 0.8687
  where Python 3.12 prints 0.8688. The repo tests assert those
  two values with a tolerance for exactly this reason. The
  counts, band accuracies, and capture rates do not move.

## Step 4: Run the whole suite

```text
python -m unittest discover -s tests -v
python -m unittest tests.test_layout -v
```

Expected: 52 tests, all passing, plus the scaffold smoke test.

## What to try next (named v1.1 backlog, not built)

PROPOSAL.md (Next cycle) in the repo names the next steps honestly: a larger
and real document eval, an OCR path and an LLM extraction path
when a free route is verified, held-out threshold validation,
and a human review workflow with timing. None of that exists at
v1.0. If you extend this project, keep the discipline: state the
confidence rule first, report synthetic and real results
separately, and never call a route label a probability until a
calibration measurement on held-out data says you can.
