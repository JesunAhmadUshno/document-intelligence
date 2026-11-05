# BUILD-SPEC: Level 2, Build: document-intelligence (P16)

Written first, before the Build code, per the task order.

## Scope from SPEC.md

SPEC v1 levels: OCR plus LLM extraction from invoices and forms;
table extraction and question answering across many documents.
Deep (later) adds per-field confidence, an eval harness, and a
review queue. Learn already ships basic confidence and a queue,
so Build must go beyond Learn in scale and in the two named
Build capabilities:

1. Table extraction: line-item rows from documents.
2. Cross-document question answering: aggregate and lookup
   questions answered from extracted records across the corpus.

Build closes when the system runs end to end, tests pass, and
one benchmark or result table with method is in the README.

## Named substitutions (honest, stated everywhere)

- No OCR engine is available on the Muse VM: `which tesseract`
  returns nothing (checked 2026-11-05). No LLM is available on
  the Muse VM either. Therefore OCR is a named substitution:
  the pipeline ingests synthetic plain-text documents in the
  layout an OCR step would produce (one text line per document
  line, tables as delimiter-separated rows), and says so in the
  README, the results file, and the code docstrings. No claim is
  made about extraction from images, scans, or PDFs.
- LLM extraction is a named substitution: extraction is the
  Learn rule-based extractor, reused by import, plus Build
  patterns for receipt labels. No claim is made about LLM
  extraction quality.
- Assigned node: the Dell R610 is unreachable for this cycle.
  No live capture is claimed. Build runs on the Muse VM (CPU,
  Python standard library only), and that costs a grade
  deduction named in the level README.
- Documents are synthetic, authored for this project, with
  invented vendor names. No real document is used.

## Corpus

32 synthetic plain-text documents in corpus.py:

- 16 invoices, 8 purchase forms, 8 receipts.
- At least 2 layout variants per type (6 variants total):
  invoices A (pipe table, primary labels) and B (semicolon
  table, alternate labels); forms A (pipe, primary labels) and
  B (semicolon, Invoice # and Supplier labels); receipts A
  (pipe, Store and Receipt Number labels) and B (semicolon,
  vendor as first line, Receipt No and Paid labels).
- Every document carries a line-item table and hand-labelled
  ground truth for the 5 Learn fields plus its table rows.
- Two documents carry known unsupported formats on purpose:
  B15 has its date written out in words, and B16 has its total
  written out in words. The extractor is expected to miss
  those two fields, as in Learn document D08.

## Table format (stated)

A table starts with a header row naming the four columns
(item, quantity, unit price, line total), separated by pipe
or by semicolon, matching the document variant. Each following
row with the same delimiter and exactly 4 cells is a line
item: item text, integer quantity, dollar unit price with two
decimals, dollar line total with two decimals. The table ends
at the first line without that delimiter. Line total must
equal quantity times unit price in the authored corpus, and
the document total equals the sum of its line totals.

## Pipeline

corpus.py (fixtures and ground truth) -> pipeline.py (field
extraction reusing the Learn extractor by import, plus Build
receipt patterns; table extraction; per-document records) ->
qa.py (cross-document questions answered from extracted
records only, each answer citing the document ids it used) ->
eval_build.py (per-field accuracy, table row and cell
accuracy, QA accuracy) -> run_build.py (writes
results_build.json deterministically; two runs identical).

Extracted records passed to the QA layer contain no ground
truth, so QA cannot read the answers. QA gold answers in the
eval are computed by independent aggregation code in
eval_build.py over the ground-truth records, and the unit
tests add hand-computed expectations for named questions.

## Eval harness

- Per-field accuracy: exact match against ground truth over
  32 documents x 5 fields, reported per field and overall.
  A correctly detected absence (receipt due_date) counts as
  correct, as in Learn.
- Table row accuracy: rows exactly correct (all 4 cells, in
  authored order) divided by total ground-truth rows.
- Table cell accuracy: correct cells divided by total
  ground-truth cells (rows x 4). A missing row scores 0 for
  its cells; extra extracted rows are counted and reported.
- QA accuracy: 16 labelled questions; an answer is correct
  when its value equals the independently computed gold value
  and its cited document ids equal the gold citation set.

## Acceptance

- Full test suite passes: Learn tests, Build tests, smoke.
- results_build.json is deterministic across two runs.
- Root README carries the measured Build result table and
  Status: Build DONE; the level README carries method,
  results, failure modes, the grade, and one exact main
  results claim paragraph for the Jev gate.
- No em dash in any touched file.
