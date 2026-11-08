# A Confidence Score That Is Not a Probability: Calibrating Document Extraction

By Jesun Ahmad Ushno
Date: 2026-11-05
Status: DRAFT, written fan-out for P16 document-intelligence v1.0. Not posted.

## The problem

Document extraction systems attach a confidence score to every
field they pull out of an invoice or a form, and downstream code
treats that number as a probability: above a threshold, trust it;
below it, send it to a human. That treatment is only safe if the
score is calibrated. A score of 0.80 should be right about 80
percent of the time. This project builds a small extraction
pipeline, then does the part that is usually skipped: it measures
whether its own confidence scores mean what they appear to mean.
The answer is no, and the measurement is the point.

This project, P16 in Roadmap v3, builds that discipline in three
levels: rule-based extraction with a stated confidence rule, a
pipeline with tables and cross-document questions, then a
calibration study over the pipeline output with a measured review
queue. All code is in the open, runs with the Python standard
library only, and needs no model, no API, and no credential.

Repository: https://github.com/JesunAhmadUshno/document-intelligence

## Honest scope, stated first

There is NO OCR and NO LLM in any level of this project. Every
document is a synthetic plain-text fixture with invented vendor
names, written in the layout an OCR step would produce. Extraction
is rule-based (regular expressions per field). No number in this
post describes extraction from images, scans, or PDFs, and no
number describes an LLM extractor. Those are named substitutions
in every level README, and the OCR and LLM paths are v1.1 backlog
items in ROADMAP.md, not built work.

The confidence values are route labels from a stated rule: 1.00
for a primary labelled match, 0.80 for an alternate labelled
match, 0.60 for an unlabelled fallback match, and 0.00 when
nothing matched. Deep measures those labels. It does not turn
them into probabilities, and this post never calls them
probabilities.

## Past, present, future (the dossier, condensed)

Past: document AI services and OCR pipelines already exist. The
prior art and the history of the problem are recorded in
DOSSIER.md and NOVELTY.md in the repo. The novelty text there
stays marked PROPOSED. This post makes no novelty claim beyond
the measured work below.

Present: v1.0 closes three levels on 2026-11-05. Learn ran
rule-based extraction over a small synthetic set with an eval
harness and a review queue. Build scaled the pipeline to three
document kinds with table extraction and cross-document QA.
Compressed Deep calibrated the per-field confidence values over
the unchanged Build eval and measured what a review queue
captures and what it costs.

Future: the rest of the v2 Deep scope is named in ROADMAP.md in
the repo as the v1.1 backlog. It includes a larger and real
document eval, an OCR path and an LLM extraction path when a
free route is verified, held-out threshold validation, a human
review workflow with timing, and per-kind calibration cuts.
None of that is done, and none of it is claimed here.

## Main results claim

At v1.0, measured on the Muse VM on 2026-11-05 with synthetic plain-text documents only and no OCR and no LLM: Learn extracted 38 of 40 fields correctly (accuracy 0.9500) over 8 documents; Build extracted 158 of 160 fields correctly (accuracy 0.9875) over 32 documents, with 65 of 65 table rows and 260 of 260 cells correct and 15 of 16 cross-document QA questions correct; Deep calibrated the Build confidence values over the same 160 fields and found band accuracies of 0.8000 at 0.00 (8 of 10), 1.0000 at 0.60 (4 of 4), 1.0000 at 0.80 (47 of 47), and 1.0000 at 1.00 (99 of 99), an expected calibration error of 0.1187 and a Brier score of 0.0658, and a review queue flagging confidence below 0.60 flagged 10 of 160 fields and captured both errors (2 of 2, capture rate 1.0000), so the confidence values are route labels, not trustworthy probabilities, with 52 unit tests in total.

Every number in that claim comes from a run recorded in the level
READMEs and the three results files in the repo. Read the limits
section below before quoting any of it.

## Results by level

### Level 1, Learn (release v0.1)

Eight synthetic documents (7 invoices, 1 form), five fields each:
invoice_number, date, vendor, total, due_date.

| Measure | Result |
| --- | --- |
| Fields correct | 38 of 40, accuracy 0.9500 |
| Per-field accuracy | invoice_number 1.0000, date 0.8750, vendor 1.0000, total 0.8750, due_date 1.0000 |
| Mean confidence | 0.8800 (route rule, not a calibrated probability) |
| Review queue | 5 entries (3 missing, 2 low confidence) |
| Tests | 21, plus the scaffold smoke test |

The two misses are one document whose date is written out in
words and whose total is written in words. Neither matches a
supported pattern, and both are named in the Learn README.

### Level 2, Build (release v0.5)

Thirty-two synthetic documents (16 invoices, 8 forms, 8 receipts),
two layout variants per type, with line-item tables and a
cross-document QA layer that answers from extracted records only
and cites its document ids.

| Measure | Result |
| --- | --- |
| Fields correct | 158 of 160, accuracy 0.9875 |
| Per-field accuracy | invoice_number 1.0000, date 0.9688, vendor 1.0000, total 0.9688, due_date 1.0000 |
| Mean confidence | 0.8688 (route rule, not a calibrated probability) |
| Table extraction | 65 of 65 rows exactly correct, 260 of 260 cells correct, 0 extra rows |
| Cross-document QA | 15 of 16 questions correct, accuracy 0.9375 |
| Tests | 40 in total (19 Build, 21 Learn), plus the scaffold smoke test |

The one failed question is total spend across all documents:
answered 11758.50 against a gold of 12108.50, because one
document renders its total in words and the extractor misses it.
The QA layer reports the spend of the records it could read, and
the failure is published in the Build README, not buried.

### Level 3, Deep, compressed (release v1.0)

Deep runs the Build pipeline over its own eval, unchanged: the
same 32 documents and 160 fields. Every field is bucketed by its
stated confidence value. The bands are the four values the rule
uses, so no binning choice is hidden.

| Band (stated confidence) | Fields | Correct | Accuracy | Gap |
| --- | --- | --- | --- | --- |
| 0.00 | 10 | 8 | 0.8000 | 0.8000 |
| 0.60 | 4 | 4 | 1.0000 | 0.4000 |
| 0.80 | 47 | 47 | 1.0000 | 0.2000 |
| 1.00 | 99 | 99 | 1.0000 | 0.0000 |

Expected calibration error: 0.1187. Brier score: 0.0658.

Review queue sweep:

| Flag rule | Fields flagged | Burden | Documents flagged | Errors captured | Capture rate |
| --- | --- | --- | --- | --- | --- |
| confidence below 0.60 | 10 | 0.0625 | 10 | 2 of 2 | 1.0000 |
| confidence below 0.80 (Learn rule) | 14 | 0.0875 | 10 | 2 of 2 | 1.0000 |
| confidence below 1.00 | 61 | 0.3812 | 21 | 2 of 2 | 1.0000 |

Three findings carry the verdict. First, every non-zero band is
underconfident: fields scored 0.60 and 0.80 are right every time
on this eval, so the ECE of 0.1187 is entirely underconfidence
(overall accuracy 0.9875 minus mean confidence 0.8688). Second,
the 0.00 band pools two opposite meanings: 8 correctly detected
receipt due-date absences and the 2 real errors, so its pooled
accuracy of 0.8000 describes neither case. Third, the scores
still work as a ranking: both errors sit at the lowest value,
and flagging below 0.60 captures both at the lowest burden in
the sweep. As route labels that sort fields for review, they
work. As probabilities of correctness, they do not.

Tests at this level: 12 new tests, 52
unit tests in total, plus the scaffold smoke test.

## Honest limits

- Synthetic documents only. All documents are authored fixtures
  with invented vendors. Real documents add layout noise and
  wording variety that could move errors into higher confidence
  bands, which this eval cannot see.
- No OCR and no LLM. The SPEC headline capabilities are named
  substitutions at v1.0 (plain-text input in OCR layout,
  rule-based extraction). No claim is made about images, scans,
  PDFs, or LLM extraction.
- Only 2 errors. Every capture rate and every low-band accuracy
  rests on tiny counts. A capture rate of 1.0000 is a statement
  about this eval, not a bound on future errors.
- The threshold is fitted and tested on the same eval. The
  recommended flag rule (below 0.60) is chosen from the sweep
  over the same 160 fields it is reported on. There is no
  held-out set, and the selection bias is named in the Deep
  README.
- Correct absence counts as correct. That convention is what
  makes receipt due_date score 1.0000 at confidence 0.00. It is
  stated in every level, not hidden.
- The queue is measured offline only. Burden is counted in
  fields and documents, not minutes. No human review workflow,
  review time, or reviewer accuracy is measured.
- All levels ran on the Muse VM, not the assigned fleet node
  Dell R610. That limit is named in each stage of REPORT.md.

## Why this matters for real document work

The transferable part is the discipline, not the synthetic
scores: state the confidence rule before you measure it, bucket
outcomes by the exact values the rule produces, compute the
calibration error by a stated formula, and measure the review
queue as captures against burden before you pick a threshold.
A confidence number that has never been calibrated is a label.
This project shows, on a small honest eval, how far that label
can be from a probability, and how a queue built on the label
can still catch every error it was shown.

## Links

- Repo: https://github.com/JesunAhmadUshno/document-intelligence
- Release v0.1: https://github.com/JesunAhmadUshno/document-intelligence/releases/tag/v0.1
- Release v0.5: https://github.com/JesunAhmadUshno/document-intelligence/releases/tag/v0.5
- Release v1.0: https://github.com/JesunAhmadUshno/document-intelligence/releases/tag/v1.0
- Tutorial: fanout/tutorial.md in the repo
