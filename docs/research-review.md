# Research review: document-intelligence (P16)

Date: 2026-11-07. Reviewed at v1.0 (commit cb20df5) and updated for the
v1.0.1 rigor additions on branch site/live-dashboard.

This review grades the repo as a research artifact against a PhD-level
rubric. Every gap that could be fixed on a CPU, with no paid service and
no long run, is fixed in this change; every gap that remains names the
exact data or compute it needs.

## Summary

| Dimension | Grade (of 10) | State after this change |
| --- | --- | --- |
| Research question | 6 | Clear and answerable; now stated as an audit, not as OCR extraction |
| Hypotheses | 5 | Implicit; the Deep verdict tests one (are scores probabilities?) |
| Method | 8 | Stated formulas, specs written before code, deterministic runners |
| Baselines | 6 (was 3) | Constant-confidence and band-accuracy baselines added, in-sample |
| Statistics and uncertainty | 6 (was 2) | Wilson 95% intervals on every accuracy and on capture rate |
| Reproducibility | 9 | Stdlib only, deterministic, CI on 3.11 and 3.12, JS parity gate |
| Threats to validity | 7 (was 6) | Named in each level; stress set measures format brittleness |
| Related work | 3 (was 2) | Benchmarks and models named; no comparison possible without OCR |
| Limitations | 8 | Written plainly in every level, on the dashboard, and below |

Overall: about 6.5 of 10 as a research artifact (was about 6) and about
8.5 of 10 as an engineering artifact (was about 8). The self-graded
level scores on record (Learn 8,700, Build 7,650, Deep 7,450 of 10,000)
are unchanged.

## 1. Research question

Question as built: on a synthetic document corpus, how accurate are
hand-written extraction rules per field, and are their stated confidence
values calibrated probabilities?

Gap found: the README tagline and SPEC described the project as "OCR
plus LLM extraction", which the shipped code does not do. Fixed: README
and SPEC now state the target scope and the shipped scope side by side
("rule-based over synthetic text, no OCR, no language model").

## 2. Hypotheses

The Deep level tests one hypothesis with a written verdict: the stated
confidence values behave as probabilities of correctness. Rejected:
every non-zero band is underconfident and the 0.00 band mixes two
meanings. The Learn and Build levels have acceptance criteria rather
than falsifiable hypotheses. Remaining gap: no pre-registered hypothesis
with a falsification threshold. Needs no compute, only a written
pre-registration before the next eval set is built (ROADMAP item 1).

## 3. Method

Strong. BUILD-SPEC.md and DEEP-SPEC.md were written before the code;
ECE and Brier formulas are stated; bands are the four stated values, so
no binning choice is hidden; gold QA answers are derived independently
of the QA code. Added: a JavaScript port of the extractor, QA and
calibration code whose parity with the Python results is asserted on
every site build (site/src/parity.check.mjs). That doubles as a
cross-implementation test of the extractor.

## 4. Baselines

Gap found: no baseline for calibration. Fixed (level-3-deep/calibration.py,
key `baselines` in results_deep.json):

- Constant confidence equal to the overall accuracy: ECE 0.0000, Brier
  0.0123.
- In-sample band-accuracy map: ECE 0.0000, Brier 0.0100.
- Stated route labels: ECE 0.1187, Brier 0.0658.

Both baselines are fitted on the items they are scored on and are
labelled in-sample. They show that most of the Brier score is the
labels' values, not ranking failure. Remaining gap: an out-of-sample
recalibration baseline. Needs a held-out eval of a few hundred labelled
fields with enough errors to fit on (ROADMAP items 1, 5 and 6); CPU
only, minutes to run, but the data does not exist yet.

There is no extraction baseline beyond the rules (for example an OCR
engine or a learned extractor). Needs an OCR engine and a free or local
model on the same corpus (ROADMAP items 3 and 4).

## 5. Statistics and uncertainty

Gap found: no interval estimate anywhere, while capture rate and band
accuracies rest on 2 errors. Fixed: Wilson 95% intervals (stdlib math,
`wilson_interval` in calibration.py, unit-tested by hand) on every band
accuracy, every per-field accuracy, every group in the new cuts, and the
error capture rate. Capture of 2 of 2 has an interval of 0.3424 to 1.0.
The dashboard draws these as whiskers, computed in the browser and
checked against the Python values at build time.

Added per-kind, per-variant and per-layout cuts (key `breakdowns`),
labelled indicative only because each group holds 0 to 2 errors.

Remaining gap: power. With 2 errors, no capture rate or band accuracy
can be estimated tightly. Needs a larger labelled eval (ROADMAP item 1):
roughly 30 or more errors would bring a Wilson interval on capture rate
to about plus or minus 0.15.

## 6. Reproducibility

Strong. Standard library only; all three runners and the new stress
runner are deterministic, and the committed results files are checked
by `git diff --exit-code` after a rerun. CI runs on Python 3.11 and
3.12. New: unit tests assert that results_stress.json and
level-2-build/documents_export.json match a fresh run, and the site
build fails if the browser port drifts from any committed result.

## 7. Threats to validity

Named in every level README. Added one measurement: a deterministic
perturbation stress set (level-3-deep/stress.py, results_stress.json),
reported separately from the main eval. Four fixed format shifts on all
32 documents with labels unchanged:

| Shift | Fields correct | Table rows |
| --- | --- | --- |
| Labels lower-cased | 47 / 160 | 65 / 65 |
| Lines indented two spaces | 43 / 160 | 65 / 65 |
| Dates as DD/MM/YYYY | 103 / 160 | 65 / 65 |
| Dollar sign removed | 127 / 160 | 0 / 65 |

The rules are format-bound: the 0.9875 headline holds only for the
exact formats the rules were written for. Remaining threats:

- Same author wrote corpus, rules and shifts. Needs an independently
  authored or real document set (ROADMAP items 1 and 2).
- Threshold chosen on the same eval it is scored on. Needs a held-out
  split of a larger eval (ROADMAP item 5).
- Run location: the Muse VM, not the assigned Dell R610. Needs one run
  on the R610 (ROADMAP item 10); seconds of CPU.

## 8. Related work

Gap found: DOSSIER.md Past has no dated citations and NOVELTY.md is a
placeholder. Partly fixed: NOVELTY.md now states the measured value
plainly (a reproducible calibration audit of route-label confidence)
and names the standard benchmarks (FUNSD, CORD, SROIE, DocVQA) and
layout-aware models (LayoutLM, Donut) as the prior art it does not
compare against, with the reason. Remaining gap: a dated literature
review and a measured comparison. The comparison needs an OCR engine,
one of those public datasets, and a CPU or GPU run of a pretrained
layout model; that is outside this change's no-GPU, no-download scope.

## 9. Limitations

Written plainly in each level README, in ROADMAP.md (the v1.1 backlog,
not built and not claimed), and on the dashboard (limits.md window):
synthetic self-authored corpus, no OCR and no language model, 2 errors,
in-sample threshold, four discrete route values rather than a
probability model, offline-only review queue, and the run location.

## What changed in this review

- calibration.py: Wilson intervals, two in-sample baselines, cuts by
  kind, variant and layout; results_deep.json regenerated (additive
  keys only, every v1.0 number unchanged).
- stress.py and results_stress.json: perturbation stress set.
- export_texts.py and documents_export.json: document texts for the
  dashboard, so the site never retypes a document.
- tests/test_deep_upgrades.py: 16 new tests (68 in total).
- README, SPEC, NOVELTY and the Deep README: scope wording and the new
  results.
- site/: live dashboard with a build-time parity gate;
  .github/workflows/pages.yml publishes it.
