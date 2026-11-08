# 0003: A correctly detected absence counts as correct

Date: 2026-11-05 (recorded 2026-11-08). Status: accepted.

Context. Some fields are genuinely absent (receipts have no due date).
The extractor returns None at confidence 0.00 for them.

Decision. An extracted None that matches a ground-truth None is scored
correct, from Learn onward.

Consequences. Receipt due_date scores 8 of 8 at confidence 0.00, so the
0.00 band pools 8 correct absences with the 2 real misses (band accuracy
0.8000). Under a convention that left absences unscored, the 0.00 band
would read 0 of 2 and the ECE would change. The per-field split in
REPORT.md shows both readings.
