"""Run the Deep calibration end to end and write results.

Run: python level-3-deep/run_deep.py
Writes level-3-deep/results_deep.json. No timestamps, no
randomness, so two runs produce an identical file.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from calibration import evaluate  # noqa: E402


def main():
    result = evaluate()
    print(f"Fields: {result['total_correct']}/{result['total_fields']} "
          f"correct, accuracy={result['overall_accuracy']:.4f}, "
          f"mean_confidence={result['mean_confidence']:.4f}")
    for b in result["bands"]:
        print(f"Band {b['confidence']:.2f}: {b['correct']}/{b['count']} "
              f"accuracy={b['accuracy']:.4f} gap={b['gap']:.4f}")
    print(f"ECE={result['ece']:.4f} Brier={result['brier']:.4f}")
    for s in result["threshold_sweep"]:
        print(f"Queue {s['rule']}: flagged {s['fields_flagged']} fields "
              f"(burden {s['review_burden']:.4f}), "
              f"{s['documents_flagged']} documents, errors captured "
              f"{s['errors_captured']}/{s['total_errors']} "
              f"(rate {s['error_capture_rate']:.4f})")
    rec = result["recommended_queue"]
    print(f"Recommended: {rec['rule']} flags {rec['fields_flagged']} "
          f"fields and captures {rec['errors_captured']}/"
          f"{rec['total_errors']} errors")
    out = {
        "scenario": "Per-field confidence calibration over the unchanged "
                    "Build eval: 32 synthetic plain-text documents, 160 "
                    "fields; bands are the four stated confidence values "
                    "(0.00, 0.60, 0.80, 1.00); ECE by the stated weighted "
                    "absolute gap formula; review queue measured by a "
                    "threshold sweep; no OCR, no LLM, run on the Muse VM "
                    "not the Dell R610",
        "total_documents": result["total_documents"],
        "total_fields": result["total_fields"],
        "total_correct": result["total_correct"],
        "total_errors": result["total_errors"],
        "overall_accuracy": result["overall_accuracy"],
        "mean_confidence": result["mean_confidence"],
        "bands": result["bands"],
        "ece": result["ece"],
        "brier": result["brier"],
        "per_field": result["per_field"],
        "threshold_sweep": result["threshold_sweep"],
        "recommended_threshold": result["recommended_threshold"],
        "recommended_queue": result["recommended_queue"],
        "items": result["items"],
        "baselines": result["baselines"],
        "breakdowns": result["breakdowns"],
    }
    path = os.path.join(HERE, "results_deep.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    print("Wrote", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
