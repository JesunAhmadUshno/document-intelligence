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

Rigor additions (v1.0.1): a Wilson 95% interval on every
accuracy and on the error capture rate, two in-sample
baselines (a constant confidence equal to the overall
accuracy, and the band-accuracy map), and per-kind,
per-variant and per-layout cuts. With 2 errors in 160
fields these are indicative only: the intervals are wide
on purpose, and that is the point of reporting them.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(os.path.dirname(HERE), "level-2-build")
if BUILD not in sys.path:
    sys.path.insert(0, BUILD)
from corpus import DOCUMENTS  # noqa: E402
from pipeline import FIELDS, build_records  # noqa: E402

THRESHOLDS = [0.60, 0.80, 1.00]
Z95 = 1.959964


def wilson_interval(k, n, z=Z95):
    """Wilson score 95% interval for k successes in n trials."""
    if n == 0:
        return [0.0, 1.0]
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return [round(max(0.0, centre - half), 4), round(min(1.0, centre + half), 4)]


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
            "wilson95": wilson_interval(correct, len(sel)),
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
            "wilson95": wilson_interval(correct, len(sel)),
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
        "capture_wilson95": wilson_interval(captured, total_errors),
        "flagged_correct": len(flagged) - captured,
        "queue": [{"doc_id": i["doc_id"], "field": i["field"],
                   "confidence": i["confidence"],
                   "extracted": i["extracted"], "correct": i["correct"]}
                  for i in flagged],
    }


def baselines(items, bands):
    """ECE and Brier for the stated labels against two in-sample
    baselines: one constant confidence equal to the overall
    accuracy, and each item scored by its own band accuracy.
    Both baselines are fitted on the items they are scored on."""
    n = len(items)
    acc = sum(1 for i in items if i["correct"]) / n
    outcome = [1 if i["correct"] else 0 for i in items]
    band_acc = {b["confidence"]: b["correct"] / b["count"] for b in bands}
    mapped = [band_acc[i["confidence"]] for i in items]
    return {
        "stated_route_labels": {"ece": expected_calibration_error(items, bands),
                                "brier": brier_score(items)},
        "constant_overall_accuracy": {
            "confidence": round(acc, 4), "ece": 0.0,
            "brier": round(sum((acc - y) ** 2 for y in outcome) / n, 4)},
        "band_accuracy_map_in_sample": {
            "ece": 0.0,
            "brier": round(sum((c - y) ** 2 for c, y in zip(mapped, outcome)) / n, 4)},
    }


def _group_row(group, sel):
    correct = sum(1 for i in sel if i["correct"])
    return {
        "group": group, "count": len(sel), "correct": correct,
        "errors": len(sel) - correct,
        "accuracy": round(correct / len(sel), 4),
        "wilson95": wilson_interval(correct, len(sel)),
        "mean_confidence": round(sum(i["confidence"] for i in sel) / len(sel), 4),
        "ece": expected_calibration_error(sel, band_table(sel)),
    }


def breakdowns(items, documents=None):
    """Accuracy and ECE per kind, per variant (A/B), and per
    layout (kind plus variant). Too small to conclude from."""
    documents = DOCUMENTS if documents is None else documents
    meta = {d["id"]: (d["kind"], d["variant"]) for d in documents}
    keys = {
        "by_kind": lambda i: meta[i["doc_id"]][0],
        "by_variant": lambda i: meta[i["doc_id"]][1],
        "by_layout": lambda i: "/".join(meta[i["doc_id"]]),
    }
    out = {}
    for name, key in keys.items():
        groups = {}
        for i in items:
            groups.setdefault(key(i), []).append(i)
        out[name] = [_group_row(g, sel) for g, sel in groups.items()]
    return out


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
        "baselines": baselines(items, bands),
        "breakdowns": breakdowns(items, documents),
    }
