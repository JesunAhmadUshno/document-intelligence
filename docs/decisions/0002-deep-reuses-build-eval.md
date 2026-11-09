# 0002: Deep measures the unchanged Build eval

Date: 2026-11-05 (recorded 2026-11-08). Status: accepted.

Context. Calibration needs errors, and the Build eval has only 2 in 160
fields. Extending the corpus would add errors but change every Build
number.

Decision. Deep calibrates the same 32 documents and 160 fields as Build,
so Deep and Build numbers compare directly. No recalibration map is
fitted: 2 errors cannot support one.

Consequences. Every capture rate and low-band accuracy rests on tiny
counts (capture 2 of 2 has a Wilson 95% interval of 0.3424 to 1.0000),
and the review threshold is chosen on the same items it is scored on.
A larger eval with a held-out split is items 1 and 5 of the next cycle.
