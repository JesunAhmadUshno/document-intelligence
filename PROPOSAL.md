# Proposal: document-intelligence (P16)

Status: NOT LOCKED. Not pre-registered. This file was assembled on
2026-11-08, under the portfolio standard v2, from the plan files the
project already had: SPEC.md (the scope, 2026-11-04), the Build and
Deep plans (BUILD-SPEC.md and DEEP-SPEC.md, 2026-11-05), NOVELTY.md,
DOSSIER.md and ROADMAP.md. Their text is moved here below, unchanged
except for file paths and the removal of self-assigned grades.

Why no lock is claimed: git history shows the scope (commit ad871ca)
came before any code, but it holds no hypothesis and no pass line.
The Build and Deep plans say they were written before their code, but
each was committed in the same commit as that code and its results
(cb76a4d and 0c72b92), so git cannot prove the order. Under the
standard, a lock is never invented after results exist. The repo
carries the label "not pre-registered" and is capped at Functional
until a locked confirmatory cycle (the Next cycle section below)
lifts the cap.

## Question

On a synthetic document corpus, how accurate are hand-written
extraction rules per field, and are their stated confidence values
calibrated probabilities?

## Hypotheses, stated after the fact

These are written down now so the report can score them. None was
registered before its result, so none counts as confirmatory.

- H1 (Deep): the four stated confidence values (1.00, 0.80, 0.60,
  0.00) behave as probabilities of correctness, so the expected
  calibration error over the bands is near zero.
- H2 (Deep): flagging fields below a confidence threshold captures
  every extraction error at a review burden well under the whole
  eval.
- Acceptance criteria for Learn and Build (from SPEC.md, in Scope below):
  the code runs end to end, tests pass, and a result table with its
  method is published.

## Scope (from PROPOSAL.md, 2026-11-04)

Phase skill: spec-driven-development (house engineering pipeline).
Status: Wave 0 scaffold spec, from Roadmap v2 text and the v3 decision pack. Scope and acceptance criteria below are the v2 section text, kept as the source of truth until the project's wave opens its own spec pass.

Fleet node: Dell R610. Wave: Wave 6.
Hiring evidence: 4 of 5 (Mistral preferred, FDE roles at Mistral and OpenAI) [confirmed, fleet and scoring pass 2026-11-04, or the decision pack for P23 to P29].

### Project section text (Roadmap v2, or the v3 candidate text for P23 to P29)

document-intelligence: KEEP

Subject: applied AI pipelines. v1 levels carry over: OCR plus LLM extraction from invoices and forms; table extraction and question answering across many documents; Deep adds per-field confidence scores, an eval harness, and a review queue for low-confidence items.
Shipped scope note (2026-11-07): the section text above is the target scope. What shipped at v1.0 is rule-based extraction over synthetic plain text in OCR layout, with no OCR and no language model; both remain named substitutions in every level and items 3 and 4 of PROPOSAL.md (Next cycle).

Fan-out: Book chapter "Paper Into Data". Paper angle: a confidence-scored extraction eval (accuracy per field against confidence band). Course module: P16-document-intelligence.

### Acceptance criteria (scaffold level)

- Learn closes when the level-1-learn code runs, its README teaches the idea, and a fresh-eyes reader can follow it.
- Build closes when the system runs end to end, tests pass, and one benchmark or result table with method is in the README.
- Deep closes when the Deep scope in the section text is done, the failure modes are written, and the dossier is updated to ship state.
- No level closes on a claim. Evidence only: code, tests, numbers, links.

## Prior work and context (from NOVELTY.md and DOSSIER.md)

### Novelty

Status: DRAFT, PROPOSED. Not verified. This text does not move into any public post, paper, or profile until the Jev claim_check gate passes on the exact text.

#### Proposed claim

Against document AI services and OCR pipelines: this project aims to differ in the way its PROPOSAL.md section text defines (a from-zero or self-hosted build, measured in public, on a named home fleet, with the failure modes written down). The exact difference is stated at the project's wave, after the prior art is re-read.

#### Prior art table

| Prior art | What it does | What this project does differently | Measured difference |
| --- | --- | --- | --- |
| document AI services and OCR pipelines | See Dossier, Past, below | PROPOSED, see the claim above | NO MEASUREMENT YET |

#### Measured value at v1.0.1 (stated plainly, no novelty claimed)

The measured contribution is a small, fully reproducible calibration audit of route-label confidence in a rule-based extractor: on 160 synthetic fields, the four stated confidence values give ECE 0.1187 and Brier 0.0658 against an in-sample band-accuracy map's Brier 0.0100, the 0.60 and 0.80 bands are underconfident while the 1.00 band is exact (99/99), and the 0.00 band pools correct absences with real misses. A deterministic stress set shows the rules are format-bound. None of this is novel against document-extraction prior art (for example the FUNSD, CORD, SROIE and DocVQA benchmarks, or layout-aware models such as LayoutLM and Donut); no comparison against them was run, because this project runs no OCR and no learned model. The value is a clean, honest worked example, not a new method.

#### Honest size

If the novelty proves small, this file will say so and name the real value instead (a cleaner reproduction, a better benchmark, a first public dataset). No novelty is invented to fill this section.

### Dossier: past, present, future

Written under the documentation and publishing standard (past, present, future). Updated at ship time. v1 was 2026-11-04; this update is the v1.0 ship state, 2026-11-05.

#### Past

Prior art for this project is named in the Novelty section above (document AI services and OCR pipelines). The history of the problem, the key papers and systems, and what was tried before are recorded in the Roadmap v2 section text in PROPOSAL.md and will be expanded with dated sources at the project's wave, before Build opens.

#### Present

Current demand evidence: hiring value 4 of 5 (Mistral preferred, FDE roles at Mistral and OpenAI) [confirmed, fleet and scoring pass 2026-11-04; for P23 to P29, the decision pack 2026-11-04]. The Round 3 research (2026-11-04) found the market centre at post-training, evals, environments, and inference depth [confirmed as the research finding; the report is at ~/workspace/research_notes/roadmap-v3-revaluation-research-20261104-0949/report.md]. Tools and versions are pinned at Build time, not in this v1.

Ship state at v1.0 (2026-11-05, measured, Muse VM, Python 3.12, synthetic plain-text documents only, no OCR and no LLM at any level):

- Learn DONE: rule-based extraction over 8 synthetic documents, 38 of 40 fields correct (0.9500), review queue of 5 entries. See REPORT.md (Learn stage).
- Build DONE: pipeline over 32 synthetic documents (16 invoices, 8 forms, 8 receipts), 158 of 160 fields correct (0.9875), 65 of 65 table rows and 260 of 260 cells correct, 15 of 16 cross-document QA questions correct. Jev claim_check on the main Build claim: REVIEW (jev-1.13.0). See REPORT.md (Build stage).
- Deep DONE (compressed Deep, December Compression Protocol): per-field confidence calibration over the unchanged Build eval, with the review queue measured. Band accuracies: 0.8000 at confidence 0.00 (8 of 10), 1.0000 at 0.60 (4 of 4), 1.0000 at 0.80 (47 of 47), 1.0000 at 1.00 (99 of 99). Expected calibration error 0.1187, Brier score 0.0658. A review queue flagging confidence below 0.60 flags 10 of 160 fields (burden 0.0625) across 10 of 32 documents and captures both field errors (capture rate 1.0000). Verdict in REPORT.md (Deep stage): the confidence values are route labels, useful as a ranking for review, not trustworthy as probabilities; the 0.00 band pools 8 correctly detected absences with the 2 errors. Jev claim_check on the main Deep claim: REVIEW (jev-1.13.0, supported noul 0.36, 1,233 input tokens). Tests at ship: 52 unit tests passed plus the scaffold smoke test. See REPORT.md (Deep stage) and PROPOSAL.md (Deep plan).

Named substitutions carried at every level: no OCR engine and no LLM exist on this VM, so input is synthetic plain text in OCR layout and extraction is rule-based; no claim is made about images, scans, PDFs, or LLM extraction. All levels ran on the Muse VM, not the assigned Dell R610, and each stage of the report names that limit.

#### Future

Open problems and the project's next steps sit in the Deep level scope in PROPOSAL.md. Any forecast about this field is [unverified] unless a dated primary source is added here at the wave update.

The v1.1 backlog is the Next cycle section of PROPOSAL.md: a larger and real document eval, OCR and LLM paths when a free route is verified, held-out threshold validation, a human review workflow with timing, per-kind calibration cuts, table and QA confidence, and a Dell R610 fleet run. Nothing in PROPOSAL.md (Next cycle) is built or claimed at v1.0.

## Build plan (from PROPOSAL.md (Build plan), 2026-11-05)

Written first, before the Build code, per the task order.

### Scope from PROPOSAL.md

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

### Named substitutions (honest, stated everywhere)

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
  Python standard library only), and that is named as a
  limit in the report.
- Documents are synthetic, authored for this project, with
  invented vendor names. No real document is used.

### Corpus

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

### Table format (stated)

A table starts with a header row naming the four columns
(item, quantity, unit price, line total), separated by pipe
or by semicolon, matching the document variant. Each following
row with the same delimiter and exactly 4 cells is a line
item: item text, integer quantity, dollar unit price with two
decimals, dollar line total with two decimals. The table ends
at the first line without that delimiter. Line total must
equal quantity times unit price in the authored corpus, and
the document total equals the sum of its line totals.

### Pipeline

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

### Eval harness

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

### Acceptance

- Full test suite passes: Learn tests, Build tests, smoke.
- results_build.json is deterministic across two runs.
- Root README carries the measured Build result table and
  Status: Build DONE; the level README carries method,
  results, failure modes, and one exact main
  results claim paragraph for the Jev gate.
- No em dash in any touched file.

## Deep plan (from PROPOSAL.md (Deep plan), 2026-11-05)

Written first, before the Deep code, per the task order.
Compressed Deep under the December Compression Protocol:
the single hardest capability in the SPEC Deep scope,
built, tested, and measured. The rest of the v2 Deep scope
goes into the Next cycle section of PROPOSAL.md as the named v1.1
backlog.

### Scope from PROPOSAL.md

SPEC Deep text: Deep adds per-field confidence scores, an
eval harness, and a review queue for low-confidence items.
Learn shipped a stated confidence rule and a queue list, and
Build shipped the eval harness over 32 documents, but no
level has measured whether the confidence scores mean what
they claim. That measurement is the hardest capability and
is this level:

Per-field confidence calibration against the Build eval,
with the review queue measured.

### What is built

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

### Named substitutions (honest, stated everywhere)

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
  and Build did, and that is named as a limit in
  the report. No live R610 capture is claimed.
- Documents are synthetic, authored for this project, with
  invented vendor names. No real document is used.
- The eval set is NOT extended. Extending corpus.py would
  change every Build number and break direct comparison
  with the Build eval, so Deep measures the same 32
  documents and 160 fields. The small error count that
  follows from this (2 errors) is named as a limit, not
  hidden.

### Acceptance

- Full test suite passes: Learn tests, Build tests, the
  new Deep tests, and the scaffold smoke test. All prior
  tests (40) must still pass.
- results_deep.json is deterministic across two runs.
- Every number in the Deep README is recomputed from
  results_deep.json or by the calibration code, never hand
  typed from memory. The unit tests carry hand-computed
  expectations for the band table, the ECE, and the queue.
- Root README and DOSSIER.md (now this file) are updated to Deep ship
  state, and the Next cycle section of PROPOSAL.md carries the rest of
  the v2 Deep scope as the named v1.1 backlog.
- One exact main results claim paragraph in the Deep
  README goes through the Jev claim_check gate.
- No em dash in any touched file.

## Next cycle

This is the former ROADMAP.md, the v1.1 backlog. A confirmatory
cycle that would lift the "not pre-registered" cap starts by locking
a new version of this file, with hypotheses and pass lines, before
the larger eval (item 1) is built.

Status at v1.0 (2026-11-05): Learn, Build, and compressed
Deep are DONE. Compressed Deep (December Compression
Protocol) built the single hardest capability in the SPEC
Deep scope: per-field confidence calibration against the
Build eval, with the review queue measured. Everything in
the v2 Deep scope that compressed Deep did not build is
listed here as the named v1.1 backlog. Nothing below is
built, and nothing below is claimed.

### v1.1 backlog (named, not built)

1. Larger eval set. More documents per type, more layout
   variants, and more authored hard cases, so band counts
   and the error set are large enough for capture rates
   and band accuracies to carry weight. The Deep threshold
   recommendation rests on 2 errors at v1.0.
2. Real documents. A small set of real invoices, forms,
   and receipts with hand-labelled ground truth, handled
   under a stated privacy rule, to test whether errors
   stay in the lowest confidence band off the authored
   corpus.
3. OCR path. An OCR engine in the pipeline when a free
   route is verified, with the same eval harness scoring
   OCR output, and calibration measured on OCR confidence
   where the engine provides one. At v1.0 there is no OCR:
   it is a named substitution in every level.
4. LLM extraction path. An LLM extractor beside the rules
   when a free route is verified, scored by the same
   harness, with its confidence (stated or derived)
   calibrated the same way. At v1.0 there is no LLM: it
   is a named substitution in every level.
5. Held-out threshold validation. Split a larger eval
   into a selection set and a held-out set, choose the
   review threshold on the first, and report capture and
   burden on the second, removing the same-eval selection
   bias named in the Deep README.
6. Recalibration, only if the data supports it. A fitted
   map from route label to measured accuracy, validated
   on held-out data. At v1.0 no map is fitted: 160 fields
   with 2 errors cannot support one.
7. Human review workflow. The queue as a working review
   surface: a reviewer confirms or corrects flagged
   fields, corrections feed the record, and review time
   per field and reviewer accuracy are measured. At v1.0
   the queue is measured offline in fields and documents,
   not minutes.
8. Per-kind and per-variant calibration cuts. Calibration
   reported separately for invoices, forms, and receipts
   and for variants A and B, once the eval is large
   enough for the cuts to mean something.
9. Table and QA confidence. Confidence and calibration
   for table rows and QA answers, not only the 5 fields.
   At v1.0 tables and QA carry no confidence score.
10. Fleet run. The full pipeline and calibration run on
    the assigned Dell R610 with a live capture, closing
    the run-location limit carried by all three
    levels at v1.0.

### Standing limits that v1.1 does not erase

- No OCR or LLM result may be reported until that path
  actually runs; the substitutions stay named until then.
- Synthetic results and real-document results are always
  reported separately, never pooled.
- The publicity and fan-out set for v1.0 is prepared
  under the documentation and publishing standard; social
  posting follows the standing platform gates and is not
  part of this repo.
