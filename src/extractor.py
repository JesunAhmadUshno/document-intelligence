"""Rule-based field extraction, Level 1 Learn.

Extracts five named fields from synthetic plain-text invoice and
form documents with regular expressions, and scores each extraction
with a stated confidence rule. An eval harness compares extractions
against the hand-labelled ground truth in documents.py, reports
accuracy per field, and builds a review queue of the extractions a
human should check.

There is no OCR, no LLM, and no real document in this level. The
input is already plain text. OCR plus LLM extraction is Build
level scope.

Confidence rule (the same for every field):
- 1.00: a primary labelled pattern matched in the expected format.
- 0.80: an alternate labelled pattern matched.
- 0.60: an unlabelled fallback pattern matched.
- 0.00: nothing matched. The extracted value is None.
An extraction goes to the review queue when its confidence is
below 0.80 or its value is None.

Only the Python standard library is used.
"""
import re

from documents import DOCUMENTS, FIELDS

ISO = r"(\d{4}-\d{2}-\d{2})"
MONEY = r"\$([\d,]+\.\d{2})"


def _search(pattern, text, flags=0):
    return re.search(pattern, text, flags)


def extract_invoice_number(text):
    m = _search(r"^Invoice Number:\s*([A-Z]+-\d+|\d+)\s*$", text, re.M)
    if m:
        return m.group(1), 1.00
    m = _search(r"^Invoice No:\s*([A-Z]+-\d+|\d+)\s*$", text, re.M)
    if m:
        return m.group(1), 0.80
    m = _search(r"^Invoice #\s*([A-Z]+-\d+|\d+)\s*$", text, re.M)
    if m:
        return m.group(1), 0.80
    return None, 0.00


def extract_date(text):
    m = _search(r"^(?:Invoice Date|Date):\s*" + ISO + r"\s*$", text, re.M)
    if m:
        return m.group(1), 1.00
    for line in text.splitlines():
        if line.startswith("Due"):
            continue
        m = _search(ISO, line)
        if m:
            return m.group(1), 0.60
    return None, 0.00


def extract_vendor(text):
    m = _search(r"^Vendor:\s*(.+?)\s*$", text, re.M)
    if m:
        return m.group(1), 1.00
    m = _search(r"^Supplier:\s*(.+?)\s*$", text, re.M)
    if m:
        return m.group(1), 0.80
    for line in text.splitlines():
        line = line.strip()
        if line and ":" not in line and line not in ("INVOICE", "PURCHASE FORM"):
            return line, 0.60
    return None, 0.00


def extract_total(text):
    m = _search(r"^Total:\s*" + MONEY + r"\s*$", text, re.M)
    if m:
        return m.group(1).replace(",", ""), 1.00
    m = _search(r"^Amount Due:\s*" + MONEY + r"\s*$", text, re.M)
    if m:
        return m.group(1).replace(",", ""), 0.80
    return None, 0.00


def extract_due_date(text):
    m = _search(r"^Due Date:\s*" + ISO + r"\s*$", text, re.M)
    if m:
        return m.group(1), 1.00
    m = _search(r"^Due:\s*" + ISO + r"\s*$", text, re.M)
    if m:
        return m.group(1), 0.80
    return None, 0.00


EXTRACTORS = {
    "invoice_number": extract_invoice_number,
    "date": extract_date,
    "vendor": extract_vendor,
    "total": extract_total,
    "due_date": extract_due_date,
}

REVIEW_THRESHOLD = 0.80


def extract_document(doc):
    """Extract all five fields from one document and score them."""
    fields = {}
    for field in FIELDS:
        value, confidence = EXTRACTORS[field](doc["text"])
        truth = doc["ground_truth"][field]
        fields[field] = {
            "extracted": value,
            "ground_truth": truth,
            "correct": value == truth,
            "confidence": confidence,
        }
    return fields


def evaluate(documents=None):
    """Run extraction over the fixtures and build the full result."""
    documents = DOCUMENTS if documents is None else documents
    per_document = []
    review_queue = []
    for doc in documents:
        fields = extract_document(doc)
        per_document.append({
            "doc_id": doc["id"],
            "kind": doc["kind"],
            "fields": fields,
            "correct_count": sum(1 for f in fields.values() if f["correct"]),
            "field_count": len(FIELDS),
        })
        for field in FIELDS:
            rec = fields[field]
            if rec["confidence"] < REVIEW_THRESHOLD or rec["extracted"] is None:
                review_queue.append({
                    "doc_id": doc["id"],
                    "field": field,
                    "confidence": rec["confidence"],
                    "extracted": rec["extracted"],
                    "ground_truth": rec["ground_truth"],
                    "reason": "missing" if rec["extracted"] is None
                              else "low confidence",
                })
    per_field = []
    for field in FIELDS:
        correct = sum(1 for d in per_document if d["fields"][field]["correct"])
        total = len(per_document)
        per_field.append({
            "field": field, "correct": correct, "total": total,
            "accuracy": round(correct / total, 4) if total else 0.0,
        })
    total_fields = sum(d["field_count"] for d in per_document)
    total_correct = sum(d["correct_count"] for d in per_document)
    confidences = [d["fields"][f]["confidence"]
                   for d in per_document for f in FIELDS]
    summary = {
        "documents": len(per_document),
        "fields_per_document": len(FIELDS),
        "total_fields": total_fields,
        "total_correct": total_correct,
        "overall_accuracy": round(total_correct / total_fields, 4)
        if total_fields else 0.0,
        "mean_confidence": round(sum(confidences) / len(confidences), 4)
        if confidences else 0.0,
        "review_queue_count": len(review_queue),
    }
    return {"per_document": per_document, "per_field": per_field,
            "review_queue": review_queue, "summary": summary}
