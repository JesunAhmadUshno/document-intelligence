# Level 1, Learn: document-intelligence

Status: DONE (2026-11-05). Rule-based field extraction from
synthetic plain-text invoice and form documents, with a per-field
confidence score, an eval harness against labelled ground truth,
and a review queue, built with the Python standard library only.

## Honest scope line

There is NO OCR and NO real documents and NO LLM in this level.
Every document is a synthetic plain-text fixture authored in
documents.py, with invented vendor names. The input is already
text, so nothing is scanned, photographed, or read from an image.
OCR plus LLM extraction is Build level scope.

## Method

1. Fixtures. Eight synthetic documents (seven invoices, one form),
   each with hand-labelled ground truth for five fields:
   invoice_number, date, vendor, total, and due_date. One field is
   genuinely absent (D04 due_date, ground truth None). D08 carries
   a date in an unsupported format and a total written in words:
   its ground truth holds the true values, and the extractor is
   expected to miss both.
2. Extractors. One regular expression extractor per field. Each
   tries, in order, a primary labelled pattern, alternate labelled
   patterns, and (for date and vendor) an unlabelled fallback.
   Money values are normalised by removing commas. Extracted
   values are strings, or None when nothing matched.
3. Confidence. A stated rule, the same for every field: 1.00 for a
   primary labelled match in the expected format, 0.80 for an
   alternate labelled match, 0.60 for an unlabelled fallback
   match, and 0.00 when nothing matched. The score describes the
   match route only. It is not a calibrated probability.
4. Eval harness. Each extraction is compared with ground truth
   for exact equality. A correctly detected absence counts as
   correct: D04 due_date is None in both the extraction and the
   ground truth. Accuracy is reported per field and overall.
5. Review queue. An extraction goes to the review queue when its
   confidence is below 0.80 or its value is None. The queue lists
   the document, the field, the confidence, the extracted value,
   and the reason (missing or low confidence), so a human checks
   exactly those fields first.

## Run it

    python level-1-learn/run_learn.py
    python -m unittest tests.test_learn_extraction -v
    python tests/test_smoke.py

The runner writes level-1-learn/results_learn.json deterministically:
run it twice and the file is identical (verified 2026-11-05:
sha256 cc9db96826004b9254f804b974b6c9672588a1e8f842bc6fea1a2869493e6c34
on both runs).

## Results (measured 2026-11-05, Muse VM, Python 3.12)

Per document (extracted value, with confidence in brackets):

| Doc | Kind | invoice_number | date | vendor | total | due_date | Correct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D01 | invoice | INV-1001 [1.00] | 2026-09-01 [1.00] | Maple Office Supplies [1.00] | 1250.00 [1.00] | 2026-10-01 [1.00] | 5/5 |
| D02 | invoice | INV-1002 [1.00] | 2026-09-03 [1.00] | Harbour Print Co [1.00] | 240.75 [1.00] | 2026-10-03 [1.00] | 5/5 |
| D03 | invoice | 8842 [0.80] | 2026-09-15 [1.00] | Cedar Catering [1.00] | 89.99 [1.00] | 2026-10-15 [0.80] | 5/5 |
| D04 | invoice | INV-1004 [1.00] | 2026-09-20 [1.00] | Elm Bookkeeping [1.00] | 600.00 [1.00] | none [0.00] | 5/5 |
| D05 | invoice | INV-1005 [1.00] | 2026-09-22 [1.00] | Northwind Traders [0.60] | 430.50 [0.80] | 2026-10-22 [1.00] | 5/5 |
| D06 | invoice | INV-1006 [1.00] | 2026-08-20 [0.60] | Birch Web Studio [1.00] | 975.25 [1.00] | 2026-09-20 [1.00] | 5/5 |
| D07 | form | INV-1007 [0.80] | 2026-10-02 [1.00] | Willow Packaging [0.80] | 312.40 [1.00] | 2026-11-02 [1.00] | 5/5 |
| D08 | invoice | INV-1008 [1.00] | none [0.00] | Aspen Travel [1.00] | none [0.00] | 2026-11-15 [1.00] | 3/5 |

Per field:

| Field | Correct | Total | Accuracy |
| --- | --- | --- | --- |
| invoice_number | 8 | 8 | 1.0000 |
| date | 7 | 8 | 0.8750 |
| vendor | 8 | 8 | 1.0000 |
| total | 7 | 8 | 0.8750 |
| due_date | 8 | 8 | 1.0000 |

Review queue (5 entries):

| Doc | Field | Confidence | Extracted | Reason |
| --- | --- | --- | --- | --- |
| D04 | due_date | 0.00 | none | missing |
| D05 | vendor | 0.60 | Northwind Traders | low confidence |
| D06 | date | 0.60 | 2026-08-20 | low confidence |
| D08 | date | 0.00 | none | missing |
| D08 | total | 0.00 | none | missing |

Summary: Learn ran rule-based extraction over 8 synthetic plain-text documents with 5 fields each on the Muse VM: 38 of 40 fields correct (accuracy 0.9500), per-field accuracy 1.0000 for invoice_number, vendor and due_date and 0.8750 for date and total, mean confidence 0.8800, and a 5-entry review queue, with 21 unit tests passing plus the scaffold smoke test.

Hand checks: correct fields are 5 + 5 + 5 + 5 + 5 + 5 + 5 + 3 = 38,
and 38 / 40 = 0.9500. Per field, correct counts sum the same way:
8 + 7 + 8 + 7 + 8 = 38. D08 loses exactly 2: its date is written
as 15 October 2026 (ground truth 2026-10-15) and its total is
written in words (ground truth 100.00); neither matches a
supported pattern. Confidence sums per document are 5.0 + 5.0 +
4.6 + 4.0 + 4.4 + 4.6 + 4.6 + 3.0 = 35.2, and 35.2 / 40 = 0.8800
mean confidence. The review queue count is hand-counted from the
rule: 1 missing in D04, 1 low confidence in D05, 1 low confidence
in D06, and 2 missing in D08 = 5.

## Failure modes and limits

- Synthetic text only: eight small authored documents. Real
  invoices vary in layout, wording, and noise, and none of that
  variation is measured here.
- No OCR and no LLM: the input is already clean plain text. Image
  documents, scans, and PDFs are out of scope for this level, and
  no claim is made about extraction from them.
- Narrow formats: dates are supported in ISO form only, money
  only as a dollar amount with two decimals, and only the named
  label variants are recognised. D08 shows the cost: a written-out
  date and a total in words are both missed.
- Fallbacks can mislead: the vendor fallback takes the first
  plain line of the document, and the date fallback takes the
  first ISO date outside a due date line. Both are right on these
  fixtures at 0.60 confidence, and the review queue exists
  because that route is not trustworthy in general.
- Confidence is a route label, not a probability: a 1.00 match
  can still be wrong on a document whose label is used for a
  different meaning, and no calibration is measured at this level.
- Correct absence counts as correct: D04 due_date is absent in
  the document, so extracting None is right, and it still goes
  to the review queue so a human confirms the absence.
- No table extraction, no question answering across documents,
  and no review workflow beyond the queue list. Those are Build
  and Deep scope.
- This level was run on the Muse VM (CPU), not on its assigned
  fleet node, the Dell R610. That costs a grade deduction, named
  in the grade.

## Grade

Grade: 8,700 of 10,000 for this Learn level.

Deductions (they sum to 1,300):
- Small synthetic set, eight authored plain-text documents only:
  minus 500.
- Rule-based extraction only, with no OCR, no LLM, and no real
  documents: minus 400.
- Run on the Muse VM, not the assigned Dell R610 fleet node:
  minus 200.
- Supported formats are narrow (ISO dates and a few label
  variants only, so written-out dates and totals in words miss):
  minus 100.
- No table extraction, no cross-document question answering, and
  no human review workflow beyond the queue list: minus 100.

## What Build adds next

OCR so real scanned documents become text, an LLM extraction
path beside the rules with the same eval harness scoring both,
and table extraction. See the root README level map.
