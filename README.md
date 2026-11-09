# document-intelligence

**Question.** On a synthetic document corpus, how accurate are
hand-written extraction rules per field, and are their stated
confidence values calibrated probabilities?

**Headline.** Hand-written rules extracted 158 of 160 fields correctly
from 32 synthetic documents (accuracy 0.9875, Wilson 95% interval
0.9556 to 0.9966), and their four confidence values are route labels,
not probabilities: expected calibration error 0.1187 and Brier score
0.0658. The 0.60 and 0.80 bands are underconfident and the 1.00 band
is exact (99 of 99). The eval holds only 2 errors, so every rate is
indicative, and the rules are format-bound.

**Field.** ML and AI research (evaluation and calibration).
**Job family.** Applied AI engineering: document extraction and evaluation.

**Verdict.** Functional, not pre-registered. Tests pass in CI on Python
3.11 and 3.12, the whole pipeline has run end to end, and CI regenerates
every results file byte for byte from the code. No plan was locked
before the results existed, so the repo is capped at Functional until a
locked confirmatory cycle (PROPOSAL.md, Next cycle) lifts the cap.

Scope, stated plainly. Target scope: OCR plus language-model
extraction, per-field confidence, an eval harness, a review queue.
Shipped: rule-based extraction over synthetic plain text in OCR layout,
with no OCR and no language model; the target scope is the next cycle,
not a claim. All runs were on the Muse VM (CPU), not the assigned Dell
R610.

Live dashboard: https://jesunahmadushno.github.io/document-intelligence/
(an in-browser extractor, QA console, calibration plot and review-queue
explorer; a build-time parity check holds the browser port to the
committed results).

## Reproduce

```text
python3 src/run_learn.py && python3 src/run_build.py && python3 src/run_deep.py && python3 src/stress.py && python3 src/export_texts.py
git diff --exit-code -- results/
python3 -m unittest discover -s tests -p "test_*.py" -v
```

Python 3 standard library only, deterministic, seconds on a CPU. The
first line rewrites every file in results/; the second proves nothing
moved.

## Lifecycle

- Question: DONE 2026-11-04
- Proposal: OPEN (not pre-registered; see PROPOSAL.md)
- Baseline: DONE 2026-11-05
- Build: DONE 2026-11-05
- Evaluate: OPEN
- Report: OPEN
- Review: OPEN
- Release: OPEN

The v0.1, v0.5 and v1.0 tags mark the old Learn, Build and Deep
releases; they are not a v1.0 Released verdict under the standard.

## Layout

| Path | What it holds |
| --- | --- |
| PROPOSAL.md | Question, scope, prior work, the Build and Deep plans, after-the-fact hypotheses, the next cycle (not locked) |
| REPORT.md | Summary of results with their evidence, hypotheses scored, each stage's method, results and limits, the self-review |
| src/ | Corpus fixtures (documents.py, corpus.py), extractor, pipeline, QA, eval, calibration, stress set, and the runners |
| tests/ | Unit tests with hand-computed expectations, and the layout test |
| results/ | results_learn.json, results_build.json, results_deep.json, results_stress.json, documents_export.json, written by the runners in src/ |
| docs/decisions/ | Records of hard-to-reverse choices |
| docs/index.md | Short text summary (the former Pages page) |
| fanout/ | The v1.0 written fan-out drafts and the publicity log (PUBLICITY.md) |
| site/ | The live dashboard, built from results/ and the docs |
| CHANGELOG.md, CITATION.cff, SECURITY.md, LICENSE | Release history, citation, security policy, licence |

No experiments/ folder: the corpus is authored in code (src/documents.py
and src/corpus.py), every result is a deterministic function of that
code, and no raw evidence is captured from outside the repo.

## License

Code: Apache-2.0 (see LICENSE). Tutorials: CC BY 4.0. Ruled in D-V3-11,
2026-11-04.
