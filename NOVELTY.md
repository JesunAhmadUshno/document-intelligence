# NOVELTY: document-intelligence (P16)

Status: DRAFT, PROPOSED. Not verified. This text does not move into any public post, paper, or profile until the Jev claim_check gate passes on the exact text.

## Proposed claim

Against document AI services and OCR pipelines: this project aims to differ in the way its SPEC.md section text defines (a from-zero or self-hosted build, measured in public, on a named home fleet, with the failure modes written down). The exact difference is stated at the project's wave, after the prior art is re-read.

## Prior art table

| Prior art | What it does | What this project does differently | Measured difference |
| --- | --- | --- | --- |
| document AI services and OCR pipelines | See DOSSIER.md, Past | PROPOSED, see the claim above | NO MEASUREMENT YET |

## Measured value at v1.0.1 (stated plainly, no novelty claimed)

The measured contribution is a small, fully reproducible calibration audit of route-label confidence in a rule-based extractor: on 160 synthetic fields, the four stated confidence values give ECE 0.1187 and Brier 0.0658 against an in-sample band-accuracy map's Brier 0.0100, every non-zero band is underconfident, and the 0.00 band pools correct absences with real misses. A deterministic stress set shows the rules are format-bound. None of this is novel against document-extraction prior art (for example the FUNSD, CORD, SROIE and DocVQA benchmarks, or layout-aware models such as LayoutLM and Donut); no comparison against them was run, because this project runs no OCR and no learned model. The value is a clean, honest worked example, not a new method.

## Honest size

If the novelty proves small, this file will say so and name the real value instead (a cleaner reproduction, a better benchmark, a first public dataset). No novelty is invented to fill this section.
