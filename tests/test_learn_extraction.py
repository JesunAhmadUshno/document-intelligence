"""Unit tests for the Level 1 Learn extraction. Hand-computed expectations."""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "level-1-learn"))
from documents import DOCUMENTS, FIELDS  # noqa: E402
from extractor import (  # noqa: E402
    evaluate,
    extract_date,
    extract_document,
    extract_due_date,
    extract_invoice_number,
    extract_total,
    extract_vendor,
)

BY_ID = {d["id"]: d for d in DOCUMENTS}


class TestExtractors(unittest.TestCase):
    def test_invoice_primary(self):
        self.assertEqual(extract_invoice_number(BY_ID["D01"]["text"]),
                         ("INV-1001", 1.00))

    def test_invoice_alternate_no(self):
        # "Invoice No: 8842" is an alternate label, so 0.80.
        self.assertEqual(extract_invoice_number(BY_ID["D03"]["text"]),
                         ("8842", 0.80))

    def test_invoice_alternate_hash(self):
        self.assertEqual(extract_invoice_number(BY_ID["D07"]["text"]),
                         ("INV-1007", 0.80))

    def test_date_primary(self):
        self.assertEqual(extract_date(BY_ID["D01"]["text"]),
                         ("2026-09-01", 1.00))

    def test_date_fallback_unlabelled(self):
        # D06 carries its date only in the sentence "Issued 2026-08-20
        # for services rendered.", an unlabelled fallback, so 0.60.
        # The Due Date line is excluded from the fallback scan.
        self.assertEqual(extract_date(BY_ID["D06"]["text"]),
                         ("2026-08-20", 0.60))

    def test_date_unsupported_format_misses(self):
        # D08 date is "15 October 2026": no ISO date outside the due
        # line, so the extractor misses it honestly.
        self.assertEqual(extract_date(BY_ID["D08"]["text"]), (None, 0.00))

    def test_vendor_primary(self):
        self.assertEqual(extract_vendor(BY_ID["D01"]["text"]),
                         ("Maple Office Supplies", 1.00))

    def test_vendor_alternate_supplier(self):
        self.assertEqual(extract_vendor(BY_ID["D07"]["text"]),
                         ("Willow Packaging", 0.80))

    def test_vendor_fallback_first_line(self):
        # D05 has no Vendor label: the first line is the vendor, 0.60.
        self.assertEqual(extract_vendor(BY_ID["D05"]["text"]),
                         ("Northwind Traders", 0.60))

    def test_total_primary(self):
        self.assertEqual(extract_total(BY_ID["D01"]["text"]),
                         ("1250.00", 1.00))

    def test_total_alternate_amount_due(self):
        self.assertEqual(extract_total(BY_ID["D05"]["text"]),
                         ("430.50", 0.80))

    def test_total_in_words_misses(self):
        self.assertEqual(extract_total(BY_ID["D08"]["text"]), (None, 0.00))

    def test_due_primary(self):
        self.assertEqual(extract_due_date(BY_ID["D01"]["text"]),
                         ("2026-10-01", 1.00))

    def test_due_alternate(self):
        self.assertEqual(extract_due_date(BY_ID["D03"]["text"]),
                         ("2026-10-15", 0.80))

    def test_due_genuinely_absent(self):
        # D04 has no due date line at all. Extracting None matches
        # the ground truth None, so it counts as correct, and it
        # still goes to the review queue for a human to confirm.
        fields = extract_document(BY_ID["D04"])
        self.assertIsNone(fields["due_date"]["extracted"])
        self.assertTrue(fields["due_date"]["correct"])


class TestEvaluate(unittest.TestCase):
    def setUp(self):
        self.result = evaluate()
        self.by_doc = {d["doc_id"]: d for d in self.result["per_document"]}

    def test_summary_hand_computed(self):
        # Per document correct: D01 5, D02 5, D03 5, D04 5, D05 5,
        # D06 5, D07 5, D08 3 (date and total missed). Total 38 of 40.
        s = self.result["summary"]
        self.assertEqual(s["documents"], 8)
        self.assertEqual(s["total_fields"], 40)
        self.assertEqual(s["total_correct"], 38)
        self.assertEqual(s["overall_accuracy"], 0.95)

    def test_per_field_accuracy(self):
        # invoice 8/8, date 7/8, vendor 8/8, total 7/8, due 8/8.
        pf = {r["field"]: r for r in self.result["per_field"]}
        self.assertEqual(pf["invoice_number"]["accuracy"], 1.0)
        self.assertEqual(pf["date"]["accuracy"], 0.875)
        self.assertEqual(pf["vendor"]["accuracy"], 1.0)
        self.assertEqual(pf["total"]["accuracy"], 0.875)
        self.assertEqual(pf["due_date"]["accuracy"], 1.0)
        self.assertEqual([r["field"] for r in self.result["per_field"]], FIELDS)

    def test_mean_confidence_hand_computed(self):
        # Confidence sums per document: 5.0 + 5.0 + 4.6 + 4.0 + 4.4
        # + 4.6 + 4.6 + 3.0 = 35.2, over 40 fields = 0.88.
        self.assertEqual(self.result["summary"]["mean_confidence"], 0.88)

    def test_review_queue_exact(self):
        # Below 0.80 or missing: D04 due (0.00, missing), D05 vendor
        # (0.60), D06 date (0.60), D08 date (0.00), D08 total (0.00).
        queue = [(q["doc_id"], q["field"]) for q in self.result["review_queue"]]
        self.assertEqual(queue, [("D04", "due_date"), ("D05", "vendor"),
                                 ("D06", "date"), ("D08", "date"),
                                 ("D08", "total")])
        self.assertEqual(self.result["summary"]["review_queue_count"], 5)

    def test_d08_partial(self):
        self.assertEqual(self.by_doc["D08"]["correct_count"], 3)

    def test_determinism(self):
        self.assertEqual(evaluate(), self.result)


if __name__ == "__main__":
    unittest.main()
