"""Run the Learn eval and write deterministic results.

Run: python level-1-learn/run_learn.py
Writes level-1-learn/results_learn.json. No timestamps, no randomness,
so two runs produce an identical file.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from documents import FIELDS  # noqa: E402
from extractor import evaluate  # noqa: E402


def main():
    result = evaluate()
    for d in result["per_document"]:
        cells = " ".join(
            f"{f}={d['fields'][f]['extracted']}({d['fields'][f]['confidence']:.2f},"
            f"{'ok' if d['fields'][f]['correct'] else 'WRONG'})" for f in FIELDS)
        print(f"{d['doc_id']} {d['kind']}: {cells} "
              f"correct={d['correct_count']}/{d['field_count']}")
    for pf in result["per_field"]:
        print(f"Field {pf['field']}: {pf['correct']}/{pf['total']} "
              f"accuracy={pf['accuracy']:.4f}")
    s = result["summary"]
    print(f"Summary: {s['total_correct']}/{s['total_fields']} fields correct "
          f"across {s['documents']} documents; accuracy={s['overall_accuracy']:.4f} "
          f"mean_confidence={s['mean_confidence']:.4f} "
          f"review_queue={s['review_queue_count']}")
    out = {"scenario": "8 synthetic plain-text documents, 5 fields each, "
                       "rule-based extraction, no OCR, no LLM",
           "per_document": result["per_document"],
           "per_field": result["per_field"],
           "review_queue": result["review_queue"],
           "summary": s}
    path = os.path.join(HERE, "results_learn.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    print("Wrote", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
