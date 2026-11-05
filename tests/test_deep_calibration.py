"""Unit tests for Level 3 Deep. Hand-computed expectations.

Hand counts from the Build records (level-2-build/
results_build.json) and the corpus ground truth:

- Confidence values over 160 fields: 1.00 appears 99 times,
  0.80 appears 47 times, 0.60 appears 4 times (the vendor
  fallback on receipt variants B26, B28, B30, B32), and
  0.00 appears 10 times (8 receipt due_date absences, the
  B15 date miss, and the B16 total miss). 99 + 47 + 4 + 10
  = 160.
- The only 2 errors in the Build eval are B15 date and B16
  total, both at confidence 0.00. So band accuracies are:
  0.00 band 8 of 10 = 0.8000, and 1.0000 for the other
  three bands.
- ECE by hand: (10/160) x 0.8000 + (4/160) x 0.4000
  + (47/160) x 0.2000 + (99/160) x 0.0000
  = 0.0500 + 0.0100 + 0.05875 + 0 = 0.11875, which the code
  rounds to 0.1187. Every band is underconfident or exact,
  so the ECE also equals overall accuracy minus mean
  confidence: 0.9875 - 0.8688 = 0.1187.
- Brier by hand: band 0.00 contributes 8 x 1.00 (correct
  absences at confidence 0) = 8.00; band 0.60 contributes
  4 x 0.16 = 0.64; band 0.80 contributes 47 x 0.04 = 1.88;
  band 1.00 contributes 0. Total 10.52, mean 10.52 / 160
  = 0.06575, rounded to 0.0658.
- Queue by hand: flagging confidence below 0.60 flags
  exactly the 10 fields at 0.00, across 10 documents (B15,
  B16, and the 8 receipts), and captures both errors.
  Flagging below 0.80 adds the 4 vendor fields at 0.60, all
  correct, so 14 flagged and no extra error. Flagging below
  1.00 adds the 47 fields at 0.80, all correct, so 61
  flagged, 21 documents, and still the same 2 errors.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "level-3-deep"))
from calibration import (  # noqa: E402
    build_items,
    evaluate,
    queue_at_threshold,
)

RESULT = evaluate()
ITEMS = RESULT["items"]


class TestItems(unittest.TestCase):
    def test_counts(self):
        self.assertEqual(RESULT["total_fields"], 160)
        self.assertEqual(RESULT["total_documents"], 32)
        self.assertEqual(RESULT["total_correct"], 158)
        self.assertEqual(RESULT["total_errors"], 2)
        self.assertEqual(RESULT["overall_accuracy"], 0.9875)
        # Exact mean is 0.86875, on a 4-place rounding boundary:
        # float summation rounds it to 0.8687 or 0.8688 by Python
        # version (3.11 naive sum, 3.12 Neumaier sum), so this
        # assertion uses a tolerance, not exact equality.
        self.assertAlmostEqual(RESULT["mean_confidence"], 0.8688, places=3)

    def test_errors_are_the_two_known_misses(self):
        errors = {(i["doc_id"], i["field"]) for i in ITEMS if not i["correct"]}
        self.assertEqual(errors, {("B15", "date"), ("B16", "total")})
        for i in ITEMS:
            if not i["correct"]:
                self.assertEqual(i["confidence"], 0.0)
                self.assertTrue(i["missing"])


class TestBands(unittest.TestCase):
    def test_band_table_hand_computed(self):
        bands = {b["confidence"]: b for b in RESULT["bands"]}
        self.assertEqual(set(bands), {0.0, 0.6, 0.8, 1.0})
        self.assertEqual((bands[0.0]["count"], bands[0.0]["correct"]), (10, 8))
        self.assertEqual(bands[0.0]["accuracy"], 0.8)
        self.assertEqual((bands[0.6]["count"], bands[0.6]["correct"]), (4, 4))
        self.assertEqual((bands[0.8]["count"], bands[0.8]["correct"]), (47, 47))
        self.assertEqual((bands[1.0]["count"], bands[1.0]["correct"]), (99, 99))
        self.assertEqual(bands[0.6]["accuracy"], 1.0)
        self.assertEqual(bands[0.8]["accuracy"], 1.0)
        self.assertEqual(bands[1.0]["accuracy"], 1.0)
        self.assertEqual(sum(b["count"] for b in bands.values()), 160)

    def test_ece_and_brier_hand_computed(self):
        # Exact ECE is 0.11875, on the same rounding boundary as
        # the mean confidence: 0.1187 or 0.1188 by Python version.
        # Tolerance assertion, for the same reason as test_counts.
        self.assertAlmostEqual(RESULT["ece"], 0.1187, places=3)
        self.assertEqual(RESULT["brier"], 0.0658)
        # No band is overconfident on this eval, so ECE equals
        # the overall accuracy minus the mean confidence.
        # Same rounding boundary: on Python versions where the
        # mean rounds to 0.8687, accuracy minus mean is 0.1188
        # while the band formula gives 0.1187. Tolerance, as above.
        self.assertAlmostEqual(
            RESULT["ece"],
            RESULT["overall_accuracy"] - RESULT["mean_confidence"],
            places=3)

    def test_zero_band_mixes_absences_and_errors(self):
        # The 0.00 band is two opposite things pooled: receipt
        # due_date absences (correct) and real misses (wrong).
        zero = [i for i in ITEMS if i["confidence"] == 0.0]
        due = [i for i in zero if i["field"] == "due_date"]
        rest = [i for i in zero if i["field"] != "due_date"]
        self.assertEqual(len(due), 8)
        self.assertTrue(all(i["correct"] for i in due))
        self.assertEqual(len(rest), 2)
        self.assertTrue(all(not i["correct"] for i in rest))


class TestPerField(unittest.TestCase):
    def test_per_field_accuracy(self):
        pf = {r["field"]: r for r in RESULT["per_field"]}
        self.assertEqual(pf["invoice_number"]["accuracy"], 1.0)
        self.assertEqual(pf["date"]["accuracy"], 0.9688)
        self.assertEqual(pf["vendor"]["accuracy"], 1.0)
        self.assertEqual(pf["total"]["accuracy"], 0.9688)
        self.assertEqual(pf["due_date"]["accuracy"], 1.0)

    def test_per_field_bands(self):
        pf = {r["field"]: r for r in RESULT["per_field"]}
        due = {b["confidence"]: b for b in pf["due_date"]["by_band"]}
        self.assertEqual((due[0.0]["count"], due[0.0]["accuracy"]), (8, 1.0))
        date = {b["confidence"]: b for b in pf["date"]["by_band"]}
        self.assertEqual((date[0.0]["count"], date[0.0]["accuracy"]), (1, 0.0))
        total = {b["confidence"]: b for b in pf["total"]["by_band"]}
        self.assertEqual((total[0.0]["count"], total[0.0]["accuracy"]), (1, 0.0))
        vendor = {b["confidence"]: b for b in pf["vendor"]["by_band"]}
        self.assertEqual((vendor[0.6]["count"], vendor[0.6]["accuracy"]), (4, 1.0))


class TestQueue(unittest.TestCase):
    def test_recommended_threshold(self):
        self.assertEqual(RESULT["recommended_threshold"], 0.60)
        rec = RESULT["recommended_queue"]
        self.assertEqual(rec["fields_flagged"], 10)
        self.assertEqual(rec["review_burden"], 0.0625)
        self.assertEqual(rec["documents_flagged"], 10)
        self.assertEqual(rec["errors_captured"], 2)
        self.assertEqual(rec["error_capture_rate"], 1.0)
        self.assertEqual(rec["flagged_correct"], 8)
        self.assertEqual(set(rec["document_ids"]),
                         {"B15", "B16", "B25", "B26", "B27", "B28",
                          "B29", "B30", "B31", "B32"})

    def test_learn_rule_adds_reviews_and_no_errors(self):
        learn_rule = queue_at_threshold(ITEMS, 0.80)
        self.assertEqual(learn_rule["fields_flagged"], 14)
        self.assertEqual(learn_rule["review_burden"], 0.0875)
        self.assertEqual(learn_rule["errors_captured"], 2)
        self.assertEqual(learn_rule["flagged_correct"], 12)

    def test_strictest_sweep_rule(self):
        strict = queue_at_threshold(ITEMS, 1.00)
        self.assertEqual(strict["fields_flagged"], 61)
        self.assertEqual(strict["review_burden"], 0.3812)
        self.assertEqual(strict["documents_flagged"], 21)
        self.assertEqual(strict["errors_captured"], 2)
        self.assertEqual(strict["flagged_correct"], 59)

    def test_queue_entries_are_the_zero_confidence_fields(self):
        rec = build_items()
        self.assertEqual(len(rec), 160)
        queue = RESULT["recommended_queue"]["queue"]
        self.assertTrue(all(q["confidence"] == 0.0 for q in queue))
        queued = {(q["doc_id"], q["field"]) for q in queue}
        self.assertIn(("B15", "date"), queued)
        self.assertIn(("B16", "total"), queued)

    def test_determinism(self):
        self.assertEqual(evaluate()["bands"], RESULT["bands"])
        self.assertEqual(evaluate()["ece"], RESULT["ece"])
        self.assertEqual(evaluate()["threshold_sweep"],
                         RESULT["threshold_sweep"])


if __name__ == "__main__":
    unittest.main()
