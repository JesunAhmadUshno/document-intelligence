"""Export the document texts and labels to one JSON file.

The live dashboard in site/ reads this file at build time,
so the browser extractor runs on exactly the texts the
Python pipeline runs on and never retypes a document.

Run: python src/export_texts.py
Writes results/documents_export.json. No timestamps,
so two runs produce an identical file.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
from corpus import DOCUMENTS as BUILD_DOCUMENTS  # noqa: E402
from documents import DOCUMENTS as LEARN_DOCUMENTS  # noqa: E402

OUT = os.path.join(os.path.dirname(HERE), "results", "documents_export.json")


def export():
    return {
        "build": [{k: d[k] for k in ("id", "kind", "variant", "text", "ground_truth", "table_ground_truth")}
                  for d in BUILD_DOCUMENTS],
        "learn": [{k: d[k] for k in ("id", "kind", "text", "ground_truth")} for d in LEARN_DOCUMENTS],
    }


def main():
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(export(), f, indent=2, sort_keys=True)
        f.write("\n")
    print("Wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
