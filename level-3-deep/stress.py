"""Perturbation stress set: how format-bound are the rules?

Each perturbation is a fixed text edit applied to all 32
Build documents. The ground truth is unchanged, because the
values a reader would take from the page are unchanged; only
the surface format moves. The same pipeline and the same
exact-match scoring as Build are used. There is no
randomness, so two runs give an identical file.

This is a separate experiment from the main eval and is
reported separately: it measures brittleness to four
everyday format shifts, not accuracy on a new corpus.

Run: python level-3-deep/stress.py
Writes level-3-deep/results_stress.json. Python standard
library only. No OCR, no language model.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(os.path.dirname(HERE), "level-2-build")
if BUILD not in sys.path:
    sys.path.insert(0, BUILD)
from corpus import DOCUMENTS  # noqa: E402
from eval_build import evaluate_fields, evaluate_tables  # noqa: E402
from pipeline import build_records  # noqa: E402


def _lowercase_labels(text):
    out = []
    for line in text.split("\n"):
        if ":" in line:
            label, rest = line.split(":", 1)
            line = label.lower() + ":" + rest
        out.append(line)
    return "\n".join(out)


def _indented_lines(text):
    return "\n".join("  " + line if line else line for line in text.split("\n"))


PERTURB = {
    "lowercase_labels": _lowercase_labels,
    "indented_lines": _indented_lines,
    "dmy_dates": lambda t: re.sub(r"(\d{4})-(\d{2})-(\d{2})", r"\3/\2/\1", t),
    "no_currency_symbol": lambda t: t.replace("$", ""),
}

DESCRIPTIONS = {
    "lowercase_labels": "Field labels lower-cased (Total: becomes total:)",
    "indented_lines": "Every line indented by two spaces",
    "dmy_dates": "ISO dates rewritten as DD/MM/YYYY",
    "no_currency_symbol": "Dollar sign removed from every amount",
}


def _score(documents):
    records = build_records(documents)
    per_field, summary = evaluate_fields(documents, records)
    table = evaluate_tables(documents, records)
    return {"per_field": per_field, "total_correct": summary["total_correct"],
            "total_fields": summary["total_fields"],
            "overall_accuracy": summary["overall_accuracy"],
            "rows_correct": table["rows_correct"], "rows_total": table["rows_total"]}


def evaluate(documents=None):
    documents = DOCUMENTS if documents is None else documents
    perturbations = []
    for name, fn in PERTURB.items():
        docs = [{**d, "text": fn(d["text"])} for d in documents]
        perturbations.append({"name": name, "description": DESCRIPTIONS[name], **_score(docs)})
    return {"baseline": _score(documents), "perturbations": perturbations}


def main():
    result = evaluate()
    b = result["baseline"]
    print(f"Unperturbed: {b['total_correct']}/{b['total_fields']} fields, rows {b['rows_correct']}/{b['rows_total']}")
    for p in result["perturbations"]:
        print(f"{p['name']}: {p['total_correct']}/{p['total_fields']} fields "
              f"(accuracy {p['overall_accuracy']:.4f}), rows {p['rows_correct']}/{p['rows_total']}")
    path = os.path.join(HERE, "results_stress.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write("\n")
    print("Wrote", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
