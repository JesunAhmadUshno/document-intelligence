# document-intelligence

Applied AI pipelines: OCR plus LLM extraction, per-field confidence, an eval harness, a review queue. Built in three levels with measured results at each level. Every level states plainly that there is no OCR and no LLM in the shipped code: the input is synthetic plain text in OCR layout and extraction is rule-based, and those are named substitutions, not hidden gaps.

- Learn: rule-based extraction over 8 synthetic documents (7 invoices, 1 form), 5 fields each, 40 fields total. 38 of 40 correct, accuracy 0.9500, mean confidence 0.8800, review queue 5 entries.
- Build: pipeline over 32 synthetic documents (16 invoices, 8 forms, 8 receipts), 158 of 160 fields correct, accuracy 0.9875, 65 of 65 table rows and 260 of 260 cells correct, 15 of 16 cross-document QA questions correct.
- Deep (compressed): per-field confidence calibration over the unchanged Build eval (32 docs, 160 fields, accuracy 0.9875), expected calibration error 0.1187, Brier score 0.0658, review queue below 0.60 flags 10 fields and captures both errors (capture 1.0000). Confidence values are route labels, not probabilities.

Grades on record (of 10,000): Learn 8,700, Build 7,650, Deep 7,450.

Every number above is already published in this repo (README.md level write-ups) and reproduced by the runners in this repo, checked in CI. The full write-ups are in the level folders: level-1-learn, level-2-build, level-3-deep.

Releases: https://github.com/JesunAhmadUshno/document-intelligence/releases
