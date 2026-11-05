"""Build eval harness: fields, tables, and cross-document QA.

Gold QA answers are computed here by independent aggregation
code over the corpus ground truth. This module never calls the
QA aggregation helpers to make gold: it re-derives each answer
from the labelled documents, so a QA bug and a gold bug would
have to be the same bug twice to hide. The QA layer itself
only ever sees extracted records, which carry no ground truth.
"""
from decimal import Decimal

from corpus import DOCUMENTS
from pipeline import FIELDS, build_records
from qa import QUESTIONS, answer_question

CELLS = ["item", "quantity", "unit_price", "line_total"]


def evaluate_fields(documents, records):
    per_field = []
    total_correct = 0
    for field in FIELDS:
        correct = sum(1 for doc, rec in zip(documents, records)
                      if rec["fields"][field] == doc["ground_truth"][field])
        per_field.append({"field": field, "correct": correct,
                          "total": len(documents),
                          "accuracy": round(correct / len(documents), 4)})
        total_correct += correct
    total = len(documents) * len(FIELDS)
    return per_field, {"total_fields": total, "total_correct": total_correct,
                       "overall_accuracy": round(total_correct / total, 4)}


def evaluate_tables(documents, records):
    rows_correct = 0
    rows_total = 0
    cells_correct = 0
    cells_total = 0
    extra_rows = 0
    for doc, rec in zip(documents, records):
        gold = doc["table_ground_truth"]
        got = rec["line_items"]
        rows_total += len(gold)
        cells_total += len(gold) * len(CELLS)
        extra_rows += max(0, len(got) - len(gold))
        for i, gold_row in enumerate(gold):
            if i >= len(got):
                continue
            if got[i] == gold_row:
                rows_correct += 1
            cells_correct += sum(1 for c in CELLS if got[i][c] == gold_row[c])
    return {
        "rows_correct": rows_correct, "rows_total": rows_total,
        "row_accuracy": round(rows_correct / rows_total, 4) if rows_total else 0.0,
        "cells_correct": cells_correct, "cells_total": cells_total,
        "cell_accuracy": round(cells_correct / cells_total, 4) if cells_total else 0.0,
        "extra_rows": extra_rows,
    }


def _gold_records(documents):
    return [{
        "doc_id": d["id"], "kind": d["kind"],
        "vendor": d["ground_truth"]["vendor"],
        "number": d["ground_truth"]["invoice_number"],
        "total": d["ground_truth"]["total"],
        "rows": d["table_ground_truth"],
    } for d in documents]


def gold_answer(gold, question):
    """Independent gold computation over ground-truth records."""
    qtype = question["type"]
    params = question["params"]
    if qtype == "total_spend_per_vendor":
        sel = [g for g in gold if g["vendor"] == params["vendor"]]
        return {"value": f"{sum(Decimal(g['total']) for g in sel):.2f}",
                "doc_ids": [g["doc_id"] for g in sel]}
    if qtype == "total_spend_all":
        return {"value": f"{sum(Decimal(g['total']) for g in gold):.2f}",
                "doc_ids": [g["doc_id"] for g in gold]}
    if qtype == "total_spend_for_kind":
        sel = [g for g in gold if g["kind"] == params["kind"]]
        return {"value": f"{sum(Decimal(g['total']) for g in sel):.2f}",
                "doc_ids": [g["doc_id"] for g in sel]}
    if qtype == "largest_document":
        best = gold[0]
        for g in gold[1:]:
            if Decimal(g["total"]) > Decimal(best["total"]):
                best = g
        return {"value": {"doc_id": best["doc_id"], "total": best["total"]},
                "doc_ids": [best["doc_id"]]}
    if qtype == "count_by_vendor":
        sel = [g for g in gold if g["vendor"] == params["vendor"]]
        return {"value": len(sel), "doc_ids": [g["doc_id"] for g in sel]}
    if qtype == "count_by_kind":
        sel = [g for g in gold if g["kind"] == params["kind"]]
        return {"value": len(sel), "doc_ids": [g["doc_id"] for g in sel]}
    if qtype == "line_items_for_invoice":
        sel = [g for g in gold if g["number"] == params["invoice_number"]]
        return {"value": sel[0]["rows"], "doc_ids": [sel[0]["doc_id"]]}
    if qtype == "vendor_of_invoice":
        sel = [g for g in gold if g["number"] == params["invoice_number"]]
        return {"value": sel[0]["vendor"], "doc_ids": [sel[0]["doc_id"]]}
    if qtype == "documents_over_amount":
        threshold = Decimal(params["amount"])
        sel = [g["doc_id"] for g in gold if Decimal(g["total"]) > threshold]
        return {"value": sel, "doc_ids": list(sel)}
    raise ValueError("unknown question type: " + qtype)


def evaluate_qa(documents, records):
    gold = _gold_records(documents)
    per_question = []
    for q in QUESTIONS:
        got = answer_question(records, q)
        want = gold_answer(gold, q)
        per_question.append({
            "id": q["id"], "type": q["type"], "params": q["params"],
            "answer": got, "gold": want,
            "correct": got["value"] == want["value"] and got["doc_ids"] == want["doc_ids"],
        })
    correct = sum(1 for r in per_question if r["correct"])
    return per_question, {"questions": len(per_question), "correct": correct,
                          "accuracy": round(correct / len(per_question), 4)}


def evaluate(documents=None):
    documents = DOCUMENTS if documents is None else documents
    records = build_records(documents)
    per_field, field_summary = evaluate_fields(documents, records)
    table = evaluate_tables(documents, records)
    per_question, qa_summary = evaluate_qa(documents, records)
    confidences = [rec["confidence"][f] for rec in records for f in FIELDS]
    return {
        "records": records, "per_field": per_field,
        "field_summary": field_summary, "table": table,
        "per_question": per_question, "qa_summary": qa_summary,
        "mean_confidence": round(sum(confidences) / len(confidences), 4),
    }
