"""Run the Build pipeline end to end and write results.

Run: python level-2-build/run_build.py
Writes level-2-build/results_build.json. No timestamps, no
randomness, so two runs produce an identical file.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from eval_build import evaluate  # noqa: E402


def main():
    result = evaluate()
    fs = result["field_summary"]
    t = result["table"]
    q = result["qa_summary"]
    print(f"Fields: {fs['total_correct']}/{fs['total_fields']} correct, "
          f"accuracy={fs['overall_accuracy']:.4f}, "
          f"mean_confidence={result['mean_confidence']:.4f}")
    for pf in result["per_field"]:
        print(f"Field {pf['field']}: {pf['correct']}/{pf['total']} "
              f"accuracy={pf['accuracy']:.4f}")
    print(f"Tables: rows {t['rows_correct']}/{t['rows_total']} "
          f"accuracy={t['row_accuracy']:.4f}; cells {t['cells_correct']}/"
          f"{t['cells_total']} accuracy={t['cell_accuracy']:.4f}; "
          f"extra_rows={t['extra_rows']}")
    print(f"QA: {q['correct']}/{q['questions']} correct, "
          f"accuracy={q['accuracy']:.4f}")
    for pq in result["per_question"]:
        print(f"{pq['id']} {pq['type']}: {'ok' if pq['correct'] else 'WRONG'}")
    out = {
        "scenario": "32 synthetic plain-text documents (16 invoices, 8 forms, "
                    "8 receipts, 2 layout variants per type) in the layout an "
                    "OCR step would produce; rule-based extraction reusing the "
                    "Learn extractor plus receipt patterns; table extraction; "
                    "cross-document QA from extracted records only; no OCR, "
                    "no LLM, run on the Muse VM not the Dell R610",
        "records": result["records"],
        "per_field": result["per_field"],
        "field_summary": result["field_summary"],
        "mean_confidence": result["mean_confidence"],
        "table": result["table"],
        "per_question": result["per_question"],
        "qa_summary": result["qa_summary"],
    }
    path = os.path.join(HERE, "results_build.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    print("Wrote", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
