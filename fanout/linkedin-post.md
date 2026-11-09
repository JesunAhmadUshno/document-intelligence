# LinkedIn post draft: P16 document-intelligence v1.0

Status: DRAFT NOT POSTED. Prepared 2026-11-05 under the standing
platform rules. Posting is a separate step under those rules.
The repo link is carried in the first-comment line below, per
the LinkedIn rule (links go in the first comment).

---

Your extraction pipeline's confidence scores are probably not
probabilities. Mine were not, and I measured it.

I built document-intelligence in three levels, in the open:

Learn: rule-based extraction over 8 synthetic documents, 38 of
40 fields correct, with a stated confidence rule (1.00 primary
label match, 0.80 alternate, 0.60 fallback, 0.00 no match).

Build: 32 documents (invoices, forms, receipts), 158 of 160
fields correct (0.9875), all 65 table rows correct, 15 of 16
cross-document questions correct. The one failure is published,
not buried: a total written in words was missed, and the total
spend answer came out 11758.50 against a gold of 12108.50.

Deep: I calibrated those confidence values over the same 160
fields. Expected calibration error 0.1187. The 0.60 and 0.80
bands are underconfident (fields scored 0.80 were right 47 of 47
times); the 1.00 band is exact, 99 of 99.
The 0.00 band pools 8 correct absences with the 2 real errors.
The scores are route labels, not probabilities. But as a
ranking they work: flagging everything below 0.60 sends 10 of
160 fields to review and catches both errors.

Honest scope: no OCR and no LLM in this build. The documents are
synthetic plain text in OCR layout, extraction is rule-based,
and those substitutions are named in every README. The lesson
transfers anyway: never treat a confidence number as a
probability until a calibration table on your own eval says
you can.

52 unit tests, standard library only, every number reproducible
from the runners in the repo.

First comment (link, per the LinkedIn rule):
Full write-up, code, and measured results: https://github.com/JesunAhmadUshno/document-intelligence
