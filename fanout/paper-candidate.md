# Paper candidate: P16 document-intelligence

Status: CANDIDATE brief only, prepared 2026-11-05. Nothing
submitted, no venue contacted. Submission is Jesun's tap.
Working title: Route Labels Are Not Probabilities: A Small,
Fully Measured Calibration Study of Rule-Based Document Field
Extraction

## Candidate claim

A per-field confidence score produced by a stated match-route
rule (1.00 primary labelled match, 0.80 alternate labelled match,
0.60 unlabelled fallback, 0.00 no match) is a ranking label, not
a probability. On a fixed eval of 32 synthetic plain-text
documents and 160 fields (accuracy 0.9875), calibration by the
four stated values gave band accuracies of 0.8000 at 0.00 (8 of
10), 1.0000 at 0.60 (4 of 4), 1.0000 at 0.80 (47 of 47), and
1.0000 at 1.00 (99 of 99), an expected calibration error of
0.1187 by the weighted absolute gap formula, and a Brier score
of 0.0658. Of that ECE, 0.0688 is underconfidence in the 0.60 and
0.80 bands (the 1.00 band is exact) and 0.0500 comes from the 0.00
band, a structural confound that pools correctly detected absences
with real extraction errors. A
review queue flagging confidence below 0.60 captured both field
errors at a burden of 10 of 160 fields.

## Evidence in hand (all in the repo)

- Full pipeline and calibration code, Python standard library
  only, deterministic runners, results files checked in
  (level-1-learn, level-2-build, level-3-deep).
- Band table, ECE and Brier computed by stated formulas, with
  hand-computed expectations in the test suite (52 unit tests).
- A three-rule threshold sweep (below 0.60, below 0.80, below
  1.00) reporting fields flagged, burden, documents flagged,
  errors captured, and flagged-but-correct counts for each rule.
- Per-field calibration cuts, including the due_date split that
  exposes the 0.00 band confound (8 of 8 correct at 0.00 for
  due_date, 0 of 2 for date and total combined).
- Failure modes written at every level, including the upstream
  Build failure the queue exists to catch (a total written in
  words is missed, and a cross-document spend answer inherits
  the miss).

## Honest limits (the paper must carry these)

- Synthetic documents only: 32 authored documents with invented
  vendors. No real documents, no OCR, no LLM. The study
  calibrates rule-based route labels, and any generalisation to
  OCR engine scores or LLM confidence is a hypothesis, not a
  result.
- Only 2 errors in the eval. Capture rates and low-band
  accuracies rest on tiny counts and cannot bound future error
  behaviour.
- The recommended threshold is selected on the same eval it is
  reported on. There is no held-out validation at v1.0; that is
  v1.1 backlog item 5 in ROADMAP.md.
- Correct absence counts as correct, a stated convention that
  shapes the 0.00 band. The paper must state it in the method,
  as the repo does.
- Single author, single corpus, no human review timing. The
  queue is measured in fields and documents, not minutes.

## What would strengthen it before submission

1. A larger eval with more authored hard cases, so the error
   set is large enough for capture rates to carry weight
   (PROPOSAL.md Next cycle item 1).
2. Held-out threshold validation: choose the flag rule on a
   selection set, report capture and burden on a held-out set
   (v1.1 item 5).
3. A real-document slice with hand-labelled ground truth,
   reported separately from synthetic results (v1.1 item 2).

## Venue and submission

No venue is named in this brief, and none has been contacted.
Choosing a venue and submitting are Jesun's tap, under the
publications pipeline tracker rules (one venue at a time, fees
post-acceptance only, FREE-ONLY until then).
