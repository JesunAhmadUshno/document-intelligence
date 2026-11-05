# Level 2, Build: document-intelligence

Status: DONE (2026-11-05). An end-to-end pipeline over 32
synthetic plain-text documents: field extraction reusing the
Learn extractor by import plus Build receipt patterns,
line-item table extraction, per-document records, and a
cross-document QA layer answering aggregate and lookup
questions from extracted records only, each answer citing the
document ids it used. An eval harness scores fields, table
rows and cells, and QA answers. Python standard library only.

## Honest scope line

There is NO OCR and NO LLM in this level, and both are named
substitutions (see BUILD-SPEC.md, written before the code).
No OCR engine is available on the Muse VM (`which tesseract`
returns nothing, checked 2026-11-05) and no LLM is available
either. The pipeline ingests synthetic plain-text documents
in the layout an OCR step would produce, and extraction is
rule-based (the Learn extractor plus receipt patterns), not
an LLM. No claim is made about images, scans, PDFs, or LLM
extraction. The assigned Dell R610 was unreachable for this
cycle, no live capture is claimed, and the run was on the
Muse VM: that costs a grade deduction below.

## Method

1. Corpus (corpus.py). 32 synthetic documents: 16 invoices,
   8 purchase forms, 8 receipts, in 2 layout variants per
   type (6 variants). Variant A uses pipe-separated tables
   and primary labels; variant B uses semicolon tables and
   alternate labels; receipts add Store, Receipt Number,
   Receipt No, and Paid labels. Every document carries a
   line-item table and ground truth for the 5 Learn fields
   plus its table rows. Authored arithmetic is exact: each
   line total is quantity times unit price, and each document
   total is the sum of its line totals (a test checks this
   for all 32 documents and all 65 rows).
2. Known hard cases. B15 renders its date in words and B16
   renders its total in words. The extractor is expected to
   miss both fields, as in Learn document D08. Receipts have
   no due date: ground truth is None, and a correctly
   detected absence counts as correct, as in Learn.
3. Table format (stated). A header row naming item, qty,
   unit price, and line total, separated by pipe or
   semicolon; each following row with the same delimiter and
   exactly 4 cells (item, integer quantity, dollar unit
   price, dollar line total) is a line item; the table ends
   at the first line without that delimiter.
4. Field extraction (pipeline.py). The Learn extractor is
   imported and reused. Build patterns for the receipt
   labels run first for invoice_number, vendor, and total,
   because the Learn vendor fallback would otherwise take
   the RECEIPT header line as a vendor. Confidence uses the
   Learn rule (1.00 primary, 0.80 alternate, 0.60 fallback,
   0.00 missing), with receipt primary labels at 1.00 and
   Paid at 0.80.
5. Records and QA (pipeline.py, qa.py). Each document
   becomes one record: extracted fields, confidences, and
   line items. Records carry no ground truth (a test checks
   this), so the QA layer can only answer from extracted
   values. Questions are structured dicts (type plus
   params), not natural language, because no LLM is
   available. Nine question types cover total spend per
   vendor, total spend overall and per kind, the largest
   document, counts by vendor and by kind, line items for a
   named invoice, the vendor of a named invoice, and
   documents over an amount. A record with a missed total
   contributes nothing to a spend sum and is not cited for
   it, so a missed field changes the answer visibly.
6. Eval harness (eval_build.py). Per-field accuracy over
   32 x 5 fields; table row accuracy (rows exactly correct,
   all 4 cells in authored order, over total rows) and cell
   accuracy (over rows x 4, a missing row scores 0 for its
   cells, extra rows counted separately); QA accuracy over
   16 labelled questions, where an answer counts as correct
   only when its value and its cited document ids both equal
   the gold. Gold QA answers are computed by independent
   aggregation code in eval_build.py over ground truth, and
   the tests add hand-computed expectations.

## Run it

    python level-2-build/run_build.py
    python -m unittest discover -s tests -v
    python tests/test_smoke.py

The runner writes level-2-build/results_build.json
deterministically: run twice, identical file (verified
2026-11-05, sha256
403cae1849d77462c0bd3a2973b49276eb9c4297501a4736d9a4f152ee63530a
on both runs).

## Results (measured 2026-11-05, Muse VM, Python 3.12)

| Measure | Result |
| --- | --- |
| Documents | 32 synthetic (16 invoices, 8 forms, 8 receipts), 2 variants per type |
| Fields correct | 158 of 160 (accuracy 0.9875) |
| Per-field accuracy | invoice_number 1.0000, date 0.9688, vendor 1.0000, total 0.9688, due_date 1.0000 |
| Mean confidence | 0.8688 (Learn route rule, not a calibrated probability) |
| Table rows | 65 of 65 exactly correct (row accuracy 1.0000), 0 extra rows |
| Table cells | 260 of 260 correct (cell accuracy 1.0000) |
| QA questions | 15 of 16 correct (accuracy 0.9375) |
| Unit tests | 40 passed (19 Build, 21 Learn), plus the scaffold smoke test |

Per-vendor spend from extracted records (QA answers, with
hand checks): Maple Office Supplies 2442.50 (215.00 + 387.00
+ 1660.00 + 150.00 + 30.50), Harbour Print Co 916.00, Cedar
Catering 1312.00 (385.00 + 702.00 + 120.00 + 105.00), Willow
Packaging 710.00, Aspen Travel 2175.00 (1380.00 + 480.00 +
225.00 + 90.00), Northwind Traders 1662.00. Largest document:
B12 at 1660.00. Documents over 1000.00: B06, B09, B12. Form
spend total: 1524.00.

The one failed question is Q07, total spend across all
documents: the answer is 11758.50 over 31 cited documents
against a gold of 12108.50 over 32 documents. The difference
is exactly B16 and its 350.00: B16 renders its total in
words, the extractor misses it, and the QA layer honestly
reports the spend of the records it could read.

## Main results claim (exact paragraph for the Jev gate)

Build of document-intelligence, 2026-11-05: over 32 synthetic plain-text documents (16 invoices, 8 forms, 8 receipts, 2 layout variants per type) in the layout an OCR step would produce, with no OCR and no LLM, the pipeline reused the Learn extractor plus receipt patterns and extracted 158 of 160 fields correctly (accuracy 0.9875, mean confidence 0.8688), extracted all 65 line-item table rows and all 260 cells correctly, and answered 15 of 16 cross-document questions correctly from extracted records only; the one failed question is total spend across all documents, answered 11758.50 against a gold 12108.50 because one document renders its total in words and the extractor misses it. The run was on the Muse VM, not the assigned Dell R610.

Jev gate on that paragraph: model jev-1.13.0, input tokens
1074, supported noul 0.82, route REVIEW (CLEAR at 0.85 or
above, BLOCK at or below 0.10). Spec and results:
hidden_files/jev-p16-build-claim-spec-2026-11-05.json and
jev-p16-build-claim-results-2026-11-05.json in the goal
workspace.

## Failure modes and limits

- Synthetic documents only: 32 authored documents with
  invented vendors. Real invoices add layout noise, stamps,
  handwriting, and wording variety that are not measured.
- No OCR and no LLM: the two headline capabilities of the
  SPEC text are substitutions here (plain-text input in OCR
  layout, rule-based extraction). Nothing in this level
  measures performance on scanned or photographed documents
  or with a language model in the loop.
- Fixed layouts: only the 6 authored variants and the 2
  stated table formats parse. A table with a different
  delimiter, merged cells, or columns in another order is
  not extracted, and no partial-credit table score is given.
- Unsupported field formats miss, and the miss propagates:
  a date or total written in words extracts as None (B15,
  B16), and a missed total silently lowers any spend sum
  that should include it, which is exactly how Q07 fails.
  The review queue idea from Learn is the mitigation, and
  wiring it to Build records is Deep scope.
- Table rows are matched by position: a parser that dropped
  a middle row would score the following rows wrong even if
  their text was read correctly. No alignment is attempted.
- QA is structured, not natural language: a question must be
  one of the 9 typed forms. Free-text questions, questions
  needing document text beyond the extracted fields and
  tables, and questions about a missed field cannot be
  answered.
- Confidence stays a route label, not a probability, and no
  calibration is measured at this level.
- Run on the Muse VM, not the assigned Dell R610 fleet
  node. That costs a grade deduction, named below.

## Grade

Grade: 7,650 of 10,000 for this Build level.

Deductions (they sum to 2,350):
- Synthetic documents only, 32 authored plain-text
  documents, no real documents: minus 700.
- No OCR and no LLM: the SPEC headline capabilities are
  named substitutions (plain-text input, rule-based
  extraction): minus 800.
- Run on the Muse VM, not the assigned Dell R610 fleet
  node: minus 200.
- Fixed layouts only: 6 authored variants and 2 stated
  table formats, nothing more general parses: minus 300.
- QA is structured typed questions, not natural-language
  question answering across documents: minus 200.
- Known field misses on unsupported formats (date and
  total in words) propagate into aggregate answers, as
  the failed total-spend question shows: minus 150.

## What Deep adds next

Per-field confidence work beyond the route label (a
calibration measure), the eval harness extended to the
review queue over Build records, and the queue itself
wired to the pipeline, per the SPEC Deep scope. OCR and a
real LLM path remain open until a free route for them is
verified; they are not claimed here.
