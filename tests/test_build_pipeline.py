"""Unit tests for Level 2 Build. Hand-computed expectations.

Hand sums used below, from the authored document totals:
- Maple Office Supplies: 215.00 + 387.00 + 1660.00 + 150.00
  + 30.50 = 2442.50 (B01, B07, B12, B20, B25).
- Cedar Catering: 385.00 + 702.00 + 120.00 + 105.00 = 1312.00
  (B03, B11, B22, B27).
- Aspen Travel: 1380.00 + 480.00 + 225.00 + 90.00 = 2175.00
  (B09, B15, B24, B31).
- All forms: 146 + 185 + 468 + 150 + 120 + 120 + 110 + 225
  = 1524.00 (B17 to B24).
- All documents, ground truth: 12108.50. The extracted-record
  sum is 11758.50, exactly 350.00 less, because B16 renders
  its total in words and the extractor misses it.
- Table rows per document sum to 65 (counted from the corpus
  specs: four documents with 3 rows, three with 1 row, the
  rest with 2 rows: 4x3 + 3x1 + 25x2 = 65).
"""
import copy
import os
import sys
import unittest
from decimal import Decimal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from corpus import DOCUMENTS  # noqa: E402
from eval_build import _gold_records, evaluate, evaluate_qa, gold_answer  # noqa: E402
from pipeline import build_records, extract_fields, extract_table  # noqa: E402
from qa import QUESTIONS, answer_question  # noqa: E402

BY_ID = {d["id"]: d for d in DOCUMENTS}
RECORDS = build_records()
REC_BY_ID = {r["doc_id"]: r for r in RECORDS}


class TestCorpus(unittest.TestCase):
    def test_counts_and_variants(self):
        self.assertEqual(len(DOCUMENTS), 32)
        kinds = {}
        variants = {}
        for d in DOCUMENTS:
            kinds[d["kind"]] = kinds.get(d["kind"], 0) + 1
            variants.setdefault(d["kind"], set()).add(d["variant"])
        self.assertEqual(kinds, {"invoice": 16, "form": 8, "receipt": 8})
        for kind in kinds:
            self.assertEqual(variants[kind], {"A", "B"})

    def test_authored_arithmetic(self):
        # Every authored row: line total = qty x unit price, and
        # every document total = the sum of its line totals.
        for d in DOCUMENTS:
            rows = d["table_ground_truth"]
            for r in rows:
                self.assertEqual(Decimal(r["unit_price"]) * r["quantity"],
                                 Decimal(r["line_total"]))
            self.assertEqual(
                sum(Decimal(r["line_total"]) for r in rows),
                Decimal(d["ground_truth"]["total"]))

    def test_rows_total_65(self):
        self.assertEqual(sum(len(d["table_ground_truth"]) for d in DOCUMENTS), 65)


class TestFields(unittest.TestCase):
    def test_receipt_patterns(self):
        # B25 is a receipt variant A: Store and Receipt Number.
        f = extract_fields(BY_ID["B25"]["text"])
        self.assertEqual(f["vendor"], {"extracted": "Maple Office Supplies", "confidence": 1.0})
        self.assertEqual(f["invoice_number"]["extracted"], "RCP-4001")
        # B26 is a receipt variant B: vendor is the first line,
        # the total comes from the Paid label at 0.80.
        f = extract_fields(BY_ID["B26"]["text"])
        self.assertEqual(f["vendor"]["extracted"], "Harbour Print Co")
        self.assertEqual(f["invoice_number"]["extracted"], "RCP-4002")
        self.assertEqual(f["total"], {"extracted": "66.00", "confidence": 0.8})

    def test_known_misses(self):
        # B15 date in words and B16 total in words both miss.
        self.assertIsNone(REC_BY_ID["B15"]["fields"]["date"])
        self.assertIsNone(REC_BY_ID["B16"]["fields"]["total"])
        self.assertEqual(BY_ID["B15"]["ground_truth"]["date"], "2026-10-15")
        self.assertEqual(BY_ID["B16"]["ground_truth"]["total"], "350.00")

    def test_field_summary_hand_computed(self):
        # 160 fields; exactly the two known misses are wrong.
        result = evaluate()
        s = result["field_summary"]
        self.assertEqual((s["total_correct"], s["total_fields"]), (158, 160))
        self.assertEqual(s["overall_accuracy"], 0.9875)
        pf = {r["field"]: r["accuracy"] for r in result["per_field"]}
        self.assertEqual(pf, {"invoice_number": 1.0, "date": 0.9688,
                              "vendor": 1.0, "total": 0.9688, "due_date": 1.0})

    def test_receipt_due_date_absence_correct(self):
        # All 8 receipts have ground truth due_date None and the
        # extractor also returns None, so due_date is 32 of 32.
        for doc_id in ("B25", "B26", "B27", "B28", "B29", "B30", "B31", "B32"):
            self.assertIsNone(REC_BY_ID[doc_id]["fields"]["due_date"])


class TestTables(unittest.TestCase):
    def test_pipe_table_b01(self):
        self.assertEqual(extract_table(BY_ID["B01"]["text"]), [
            {"item": "notebooks", "quantity": 10, "unit_price": "12.50", "line_total": "125.00"},
            {"item": "pens", "quantity": 20, "unit_price": "2.50", "line_total": "50.00"},
            {"item": "folders", "quantity": 5, "unit_price": "8.00", "line_total": "40.00"},
        ])

    def test_semicolon_table_b22(self):
        # B22 is a form variant B with a semicolon table.
        self.assertEqual(extract_table(BY_ID["B22"]["text"]), [
            {"item": "napkins", "quantity": 200, "unit_price": "0.15", "line_total": "30.00"},
            {"item": "cups", "quantity": 200, "unit_price": "0.20", "line_total": "40.00"},
            {"item": "plates", "quantity": 200, "unit_price": "0.25", "line_total": "50.00"},
        ])

    def test_table_summary(self):
        t = evaluate()["table"]
        self.assertEqual((t["rows_correct"], t["rows_total"]), (65, 65))
        self.assertEqual((t["cells_correct"], t["cells_total"]), (260, 260))
        self.assertEqual(t["extra_rows"], 0)

    def test_table_mutation_changes_extraction(self):
        text = BY_ID["B01"]["text"].replace("pens | 20 |", "pens | 21 |")
        rows = extract_table(text)
        self.assertEqual(rows[1]["quantity"], 21)
        self.assertNotEqual(rows, BY_ID["B01"]["table_ground_truth"])


class TestQA(unittest.TestCase):
    def _answer(self, qid):
        q = [x for x in QUESTIONS if x["id"] == qid][0]
        return answer_question(RECORDS, q)

    def test_spend_per_vendor_hand_sums(self):
        self.assertEqual(self._answer("Q01"),
                         {"value": "2442.50", "doc_ids": ["B01", "B07", "B12", "B20", "B25"]})
        self.assertEqual(self._answer("Q03")["value"], "1312.00")
        self.assertEqual(self._answer("Q05")["value"], "2175.00")
        self.assertEqual(self._answer("Q02")["value"], "916.00")

    def test_largest_and_over_amount(self):
        # Totals over 1000 by hand: B06 1050, B09 1380, B12 1660.
        self.assertEqual(self._answer("Q08"),
                         {"value": {"doc_id": "B12", "total": "1660.00"}, "doc_ids": ["B12"]})
        self.assertEqual(self._answer("Q15")["value"], ["B06", "B09", "B12"])

    def test_counts_and_lookups(self):
        self.assertEqual(self._answer("Q09")["value"], 5)
        self.assertEqual(self._answer("Q10")["value"], 8)
        self.assertEqual(self._answer("Q11")["value"], 16)
        self.assertEqual(self._answer("Q14"),
                         {"value": "Aspen Travel", "doc_ids": ["B09"]})
        self.assertEqual(self._answer("Q16")["value"], "1524.00")

    def test_line_items_question(self):
        ans = self._answer("Q12")
        self.assertEqual(ans["doc_ids"], ["B11"])
        self.assertEqual(ans["value"][0],
                         {"item": "lunch platters", "quantity": 12,
                          "unit_price": "38.00", "line_total": "456.00"})
        self.assertEqual(len(ans["value"]), 3)

    def test_qa_summary_and_known_failure(self):
        per_q, summary = evaluate_qa(DOCUMENTS, RECORDS)
        self.assertEqual((summary["correct"], summary["questions"]), (15, 16))
        self.assertEqual(summary["accuracy"], 0.9375)
        failed = [r["id"] for r in per_q if not r["correct"]]
        self.assertEqual(failed, ["Q07"])
        q07 = [r for r in per_q if r["id"] == "Q07"][0]
        # Gold 12108.50 over 32 docs; the answer misses B16 and
        # its 350.00, exactly the known total-in-words failure.
        self.assertEqual(q07["gold"]["value"], "12108.50")
        self.assertEqual(q07["answer"]["value"], "11758.50")

    def test_records_carry_no_ground_truth(self):
        for r in RECORDS:
            self.assertNotIn("ground_truth", r)
            self.assertNotIn("table_ground_truth", r)

    def test_qa_mutation_changes_answer(self):
        mutated = copy.deepcopy(RECORDS)
        for r in mutated:
            if r["doc_id"] == "B12":
                r["fields"]["total"] = "1.00"
        q = [x for x in QUESTIONS if x["id"] == "Q01"][0]
        self.assertEqual(answer_question(mutated, q)["value"], "783.50")
        q8 = [x for x in QUESTIONS if x["id"] == "Q08"][0]
        self.assertEqual(answer_question(mutated, q8)["value"]["doc_id"], "B09")
        # Gold is computed from ground truth, so it does not move.
        gold = gold_answer(_gold_records(DOCUMENTS), q)
        self.assertEqual(gold["value"], "2442.50")

    def test_determinism(self):
        self.assertEqual(evaluate(), evaluate())


if __name__ == "__main__":
    unittest.main()
