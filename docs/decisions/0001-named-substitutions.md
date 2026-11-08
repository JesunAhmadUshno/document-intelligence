# 0001: No OCR and no language model; synthetic plain text in OCR layout

Date: 2026-11-05 (recorded 2026-11-08). Status: accepted.

Context. The target scope is OCR plus language-model extraction. No OCR
engine (`which tesseract` returned nothing) and no language model were
available on the Muse VM, and no free route for either was verified.

Decision. Input is synthetic plain text in the layout an OCR step would
produce, and extraction is rule-based. Both are named substitutions in
every stage of REPORT.md, on the dashboard and in every fan-out piece.

Consequences. No claim is made about images, scans, PDFs or
language-model extraction. Every number describes hand-written rules on
self-authored text. Adding an OCR or model path is items 3 and 4 of the
next cycle in PROPOSAL.md, and its results are reported separately.
