"""Deep calibration: per-field confidence calibration and a
measured review queue over the Build eval.

The Build pipeline runs over its own 32-document eval,
unchanged. Each of the 160 extracted fields becomes one
item with its stated confidence and a correct flag (exact
match against ground truth; a correctly detected absence
counts as correct, as in Learn and Build).

Bands are the four stated confidence values themselves
(0.00, 0.60, 0.80, 1.00): the confidence rule uses no other
values, so no binning choice is hidden.

Expected calibration error (ECE), stated formula:

    ECE = sum over bands b of (n_b / N) * |acc_b - conf_b|

The Brier score is reported as a secondary measure: the
mean of (confidence - outcome)^2 over all items, outcome 1
when correct and 0 when wrong.

The review queue is measured by a threshold sweep: for each
candidate rule "flag confidence below T", the fields
flagged, the review burden, the documents flagged, the
errors captured, and the error capture rate.

There is no OCR and no LLM here: the named substitutions
from Build stand (synthetic plain text in OCR layout,
rule-based extraction). Only the Python standard library
is used.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(os.path.dirname(HERE), "level-2-build")
if BUILD not in sys.path:
    sys.path.insert(0, BUILD)
from corpus import DOCUMENTS  # noqa: E402
from pipeline import FIELDS, build_records  # noqa: E402

THRESHOLDS = [0.60, 0.80, 1.00]


def build_items(documents=None, records=None):
    """One item per extracted field, with its correct flag."""
    documents = DOCUMENTS if documents is None else documents
    records = build_records(documents) if records is None else records
    items = []
    for doc, rec in zip(documents, records):
        for field in FIELDS:
            items.append({
                "doc_id": doc["id"], "field": field,
                "confidence": rec["confidence"][field],
                "extracted": rec["fields"][field],
                "ground_truth": doc["ground_truth"][field],
                "correct": rec["fields"][field] == doc["ground_truth"][field],
                "missing": rec["fields"][field] is None,
            })
    return items


def band_table(items):
    """Accuracy per confidence band (bands are the values)."""
    bands = []
    for conf in sorted({i["confidence"] for i in items}):
        sel = [i for i in items if i["confidence"] == conf]
        correct = sum(1 for i in sel if i["correct"])
        acc = correct / len(sel)
        bands.append({
            "confidence": conf, "count": len(sel), "correct": correct,
            "accuracy": round(acc, 4), "gap": round(abs(acc - conf), 4),
        })
    return bands


def expected_calibration_error(items, bands):
    n = len(items)
    return round(sum((b["count"] / n) * abs(b["accuracy"] - b["confidence"])
                     for b in bands), 4)


def brier_score(items):
    return round(sum((i["confidence"] - (1 if i["correct"] else 0)) ** 2
                     for i in items) / len(items), 4)


def per_field_table(items):
    """Per-field accuracy overall and inside each band used."""
    table = []
    for field in FIELDS:
        sel = [i for i in items if i["field"] == field]
        correct = sum(1 for i in sel if i["correct"])
        by_band = []
        for conf in sorted({i["confidence"] for i in sel}):
            bsel = [i for i in sel if i["confidence"] == conf]
            bcorrect = sum(1 for i in bsel if i["correct"])
            by_band.append({
                "confidence": conf, "count": len(bsel),
                "correct": bcorrect,
                "accuracy": round(bcorrect / len(bsel), 4),
            })
        table.append({
            "field": field, "count": len(sel), "correct": correct,
            "accuracy": round(correct / len(sel), 4), "by_band": by_band,
        })
    return table


def queue_at_threshold(items, threshold):
    """Review queue for the rule: flag confidence below T."""
    flagged = [i for i in items if i["confidence"] < threshold]
    total_errors = sum(1 for i in items if not i["correct"])
    captured = sum(1 for i in flagged if not i["correct"])
    return {
        "threshold": threshold,
        "rule": f"confidence < {threshold:.2f}",
        "fields_flagged": len(flagged),
        "review_burden": round(len(flagged) / len(items), 4),
        "documents_flagged": len({i["doc_id"] for i in flagged}),
        "document_ids": sorted({i["doc_id"] for i in flagged}),
        "errors_captured": captured,
        "total_errors": total_errors,
        "error_capture_rate": round(captured / total_errors, 4) if total_errors else 0.0,
        "flagged_correct": len(flagged) - captured,
        "queue": [{"doc_id": i["doc_id"], "field": i["field"],
                   "confidence": i["confidence"],
                   "extracted": i["extracted"], "correct": i["correct"]}
                  for i in flagged],
    }


def evaluate(documents=None):
    items = build_items(documents)
    bands = band_table(items)
    sweep = [queue_at_threshold(items, t) for t in THRESHOLDS]
    recommended = next(
        (s for s in sweep if s["error_capture_rate"] == 1.0), None)
    total_correct = sum(1 for i in items if i["correct"])
    return {
        "items": items, "bands": bands,
        "ece": expected_calibration_error(items, bands),
        "brier": brier_score(items),
        "per_field": per_field_table(items),
        "threshold_sweep": sweep,
        "recommended_threshold": recommended["threshold"] if recommended else None,
        "recommended_queue": recommended,
        "total_fields": len(items), "total_correct": total_correct,
        "overall_accuracy": round(total_correct / len(items), 4),
        "mean_confidence": round(
            sum(i["confidence"] for i in items) / len(items), 4),
        "total_errors": len(items) - total_correct,
        "total_documents": len({i["doc_id"] for i in items}),
    }
