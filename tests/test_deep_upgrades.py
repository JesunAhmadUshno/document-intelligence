"""Unit tests for the Deep rigor upgrades: Wilson intervals,
calibration baselines, per-kind and per-variant cuts, the
perturbation stress set, and the document text export.

Hand-computed expectations:

- Wilson 95% interval on 2 of 2 (z = 1.959964): centre
  (1 + z^2/4) / (1 + z^2/2) = 1.9604 / 2.9207 = 0.6712, half
  width z * sqrt(z^2/16) / 2.9207 = 0.3288, so [0.3424, 1.0].
- Constant-confidence baseline at the overall accuracy
  0.9875: a single band, so ECE 0; Brier = p(1 - p)
  = 0.9875 x 0.0125 = 0.01234, rounded to 0.0123.
- In-sample band-accuracy map: each item scored by its band
  accuracy, so ECE 0; Brier = 10 x 0.8 x 0.2 / 160 = 0.01.
- Variant A holds B15 (date error), variant B holds B16
  (total error): 1 error in 80 fields each, accuracy 0.9875.
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
import export_texts  # noqa: E402
import stress  # noqa: E402
from calibration import evaluate, wilson_interval  # noqa: E402

RESULT = evaluate()


class TestWilson(unittest.TestCase):
    def test_two_of_two(self):
        self.assertEqual(wilson_interval(2, 2), [0.3424, 1.0])

    def test_overall_accuracy_interval(self):
        # Hand check, 158 of 160, z = 1.96: centre (0.9875 + 0.0120) / 1.0240
        # = 0.9761, half width 1.96 * sqrt(0.0000772 + 0.0000375) / 1.0240
        # = 0.0205, so [0.9556, 0.9966]. This is the README headline interval.
        self.assertEqual(RESULT["overall_wilson95"], [0.9556, 0.9966])

    def test_zero_of_zero_is_uninformative(self):
        self.assertEqual(wilson_interval(0, 0), [0.0, 1.0])

    def test_interval_contains_estimate(self):
        lo, hi = wilson_interval(8, 10)
        self.assertTrue(lo < 0.8 < hi)

    def test_bands_and_capture_carry_intervals(self):
        bands = {b["confidence"]: b for b in RESULT["bands"]}
        self.assertEqual(bands[0.6]["wilson95"], wilson_interval(4, 4))
        rec = RESULT["recommended_queue"]
        self.assertEqual(rec["capture_wilson95"], [0.3424, 1.0])
        for f in RESULT["per_field"]:
            self.assertEqual(f["wilson95"], wilson_interval(f["correct"], f["count"]))


class TestBaselines(unittest.TestCase):
    def test_constant_confidence(self):
        b = RESULT["baselines"]["constant_overall_accuracy"]
        self.assertEqual(b["confidence"], 0.9875)
        self.assertEqual(b["ece"], 0.0)
        self.assertEqual(b["brier"], 0.0123)

    def test_band_accuracy_map_in_sample(self):
        b = RESULT["baselines"]["band_accuracy_map_in_sample"]
        self.assertEqual(b["ece"], 0.0)
        self.assertEqual(b["brier"], 0.01)

    def test_stated_labels_match_headline(self):
        b = RESULT["baselines"]["stated_route_labels"]
        self.assertEqual((b["ece"], b["brier"]), (RESULT["ece"], RESULT["brier"]))


class TestBreakdowns(unittest.TestCase):
    def test_by_kind_counts(self):
        kinds = {g["group"]: g for g in RESULT["breakdowns"]["by_kind"]}
        self.assertEqual({k: g["count"] for k, g in kinds.items()},
                         {"invoice": 80, "form": 40, "receipt": 40})
        self.assertEqual(kinds["invoice"]["errors"], 2)
        self.assertEqual(kinds["form"]["accuracy"], 1.0)

    def test_by_variant(self):
        var = {g["group"]: g for g in RESULT["breakdowns"]["by_variant"]}
        self.assertEqual((var["A"]["errors"], var["B"]["errors"]), (1, 1))
        self.assertEqual(var["A"]["accuracy"], 0.9875)

    def test_by_layout_has_six_groups(self):
        self.assertEqual(len(RESULT["breakdowns"]["by_layout"]), 6)


class TestStress(unittest.TestCase):
    def test_unperturbed_matches_build(self):
        res = stress.evaluate()
        self.assertEqual(res["baseline"]["total_correct"], 158)

    def test_dmy_dates_break_every_date(self):
        res = {p["name"]: p for p in stress.evaluate()["perturbations"]}
        dates = {f["field"]: f for f in res["dmy_dates"]["per_field"]}["date"]
        self.assertEqual(dates["correct"], 0)

    def test_perturbations_are_deterministic_text_edits(self):
        text = "Date: 2026-09-01\nTotal: $12.50\n"
        self.assertEqual(stress.PERTURB["dmy_dates"](text), "Date: 01/09/2026\nTotal: $12.50\n")
        self.assertEqual(stress.PERTURB["no_currency_symbol"](text), "Date: 2026-09-01\nTotal: 12.50\n")
        self.assertEqual(stress.PERTURB["lowercase_labels"](text), "date: 2026-09-01\ntotal: $12.50\n")
        self.assertEqual(stress.PERTURB["indented_lines"](text), "  Date: 2026-09-01\n  Total: $12.50\n")

    def test_committed_results_are_current(self):
        with open(os.path.join(ROOT, "results", "results_stress.json"), encoding="utf-8") as f:
            self.assertEqual(json.load(f), json.loads(json.dumps(stress.evaluate())))


class TestExport(unittest.TestCase):
    def test_committed_export_is_current(self):
        with open(export_texts.OUT, encoding="utf-8") as f:
            self.assertEqual(json.load(f), json.loads(json.dumps(export_texts.export())))

    def test_export_counts(self):
        data = export_texts.export()
        self.assertEqual((len(data["build"]), len(data["learn"])), (32, 8))


if __name__ == "__main__":
    unittest.main()
