# Website page copy: document-intelligence (P16)

Status: DRAFT copy for Jesun's website project page. Not published
by this file. Date: 2026-11-05.

## Headline

Document intelligence, measured honestly: extraction, tables,
cross-document answers, and a confidence score that was
calibrated before it was trusted.

## Summary

document-intelligence is an applied AI pipeline project built in
three levels, in the open, with the Python standard library only.
It extracts five fields from invoices, forms, and receipts, pulls
line-item tables, answers questions across documents from the
extracted records, and then does the step most pipelines skip: it
calibrates its own per-field confidence scores and measures the
review queue those scores drive.

One scope line governs everything on this page: there is no OCR
and no LLM in the shipped code. The documents are synthetic plain
text in the layout an OCR step would produce, and extraction is
rule-based. Those are named substitutions, printed in every level
README, and the OCR and LLM paths are named v1.1 backlog, not
built work.

## Measured results (v1.0, 2026-11-05, Muse VM)

- Learn: 38 of 40 fields correct (accuracy 0.9500) over 8
  synthetic documents, with a 5-entry review queue.
- Build: 158 of 160 fields correct (accuracy 0.9875) over 32
  synthetic documents, 65 of 65 table rows and 260 of 260 cells
  correct, 15 of 16 cross-document QA questions correct.
- Deep: calibration over the same 160 fields gave an expected
  calibration error of 0.1187 and a Brier score of 0.0658. A
  review queue flagging confidence below 0.60 flags 10 of 160
  fields and captures both errors (capture rate 1.0000).
- Verdict: the confidence values are route labels, not
  probabilities. Every non-zero band is underconfident, and the
  0.00 band pools correct absences with real errors. As a ranking
  for human review, the labels work. As probabilities, they do
  not, and the project says so in its own README.
- Tests: 52 unit tests passing, plus the scaffold smoke test.
- Level grades (of 10,000): Learn 8,700, Build 7,650, Deep 7,450.

## Why it matters

Production document pipelines fail quietly: a missed total
silently lowers every spend sum built on it, exactly as the one
failed QA question in Build shows (11758.50 answered against a
gold of 12108.50). This project shows the working discipline:
an eval harness with ground truth, per-field accuracy, a
calibration table computed by a stated formula, and a review
queue measured as captures against burden before a threshold
is recommended.

## Links

- Repo: https://github.com/JesunAhmadUshno/document-intelligence
- Release v1.0: https://github.com/JesunAhmadUshno/document-intelligence/releases/tag/v1.0
- Docs: https://jesunahmadushno.github.io/document-intelligence/
