# Changelog

All notable changes to this project. Format: Keep a Changelog 1.1.
Versions follow Semantic Versioning. Tags v0.1, v0.5 and v1.0 exist
from the old Learn, Build and Deep ladder; v1.0.1 was never tagged.

## [Unreleased]

### Changed
- 2026-11-08: Restructured to the portfolio standard v2. The README is
  the abstract (question, headline with its interval, field, job
  family, verdict, reproduce, lifecycle, layout). PROPOSAL.md (not
  locked) holds SPEC.md, the Build and Deep plans, NOVELTY.md,
  DOSSIER.md and ROADMAP.md. REPORT.md holds the three level READMEs,
  the old README result tables and docs/research-review.md. Code moved
  to src/ and every results file to results/; no number changed.
  PUBLICITY.md moved to fanout/.
- 2026-11-08: Verdict under the standard: Functional, not
  pre-registered. Git history shows no plan with hypotheses and pass
  lines committed before results, so no proposal-v1 tag is set.
- 2026-11-08: Self-assigned grades removed from every public file
  (README, docs, level write-ups, fan-out drafts, publicity log,
  dashboard).

### Added
- 2026-11-08: Wilson 95% interval on overall field accuracy
  (overall_wilson95 in results/results_deep.json, 0.9556 to 0.9966),
  with a hand-checked test and a dashboard parity check; it is the
  README headline interval.
- 2026-11-08: tests/test_layout.py (required files exist, no public
  grade), CI on Python 3.11 and 3.12 with read-only permissions that
  regenerates every results file and fails on any change, CodeQL for
  Python and JavaScript, Dependabot for npm, CITATION.cff, SECURITY.md,
  docs/decisions/.

## [1.0.1] - 2026-11-07 (not tagged)

### Added
- Wilson 95% intervals on every band, per-field accuracy and the error
  capture rate; in-sample constant-confidence and band-accuracy
  baselines; per-kind, per-variant and per-layout cuts.
- Perturbation stress set (src/stress.py, results/results_stress.json).
- Document text export for the dashboard (src/export_texts.py).
- Live dashboard in site/ with a JavaScript port held to the Python
  results by a build-time parity check, published by the Pages
  workflow.
- Research review (now REPORT.md, Self-review).

### Changed
- README and SPEC state the target scope beside the shipped scope.
- Vite upgraded to 6.4.5 so npm audit reports no high or critical
  advisories.

## [1.0] - 2026-11-05

### Added
- Deep (compressed): per-field confidence calibration over the
  unchanged Build eval (ECE 0.1187, Brier 0.0658) and a measured
  review-queue threshold sweep.
- Actions polish pack: CI matrix on Python 3.11 and 3.12 with ruff,
  CodeQL, Dependabot, release workflow, labeler, greetings, stale.
  The 3.11 leg exposed a float rounding boundary in two Deep test
  assertions (exact ECE 0.11875 and mean confidence 0.86875); those
  two assertions use a 3-place tolerance, and no result changed.
- Written fan-out set in fanout/.

## [0.5] - 2026-11-05

### Added
- Build: 32-document synthetic corpus, table extraction and
  cross-document QA (158 of 160 fields, 65 of 65 rows, 15 of 16
  questions).

## [0.1] - 2026-11-05

### Added
- Learn: rule-based extraction over 8 synthetic documents with a
  stated confidence rule, an eval harness and a review queue (38 of 40
  fields).
- 2026-11-04: Wave 0 scaffold: SPEC.md, DOSSIER.md, NOVELTY.md.
