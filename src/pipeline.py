"""Build pipeline: field extraction plus table extraction.

Field extraction reuses the Level 1 Learn extractor by import,
and adds Build patterns for receipt labels (Receipt Number,
Receipt No, Store, Paid) that Learn does not cover. Build
patterns run first for the fields they name, because the Learn
vendor fallback would otherwise take the RECEIPT header line
as a vendor.

Table extraction follows the stated format in PROPOSAL.md (Build plan):
a header row naming item, quantity, unit price, and line total,
separated by pipe or semicolon; each following row with the
same delimiter and exactly 4 cells is a line item; the table
ends at the first line without that delimiter.

The input is synthetic plain text in the layout an OCR step
would produce. There is no OCR and no LLM here: those are the
named substitutions in PROPOSAL.md (Build plan).

Only the Python standard library is used.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import extractor as learn_extractor  # noqa: E402
from corpus import DOCUMENTS  # noqa: E402

FIELDS = ["invoice_number", "date", "vendor", "total", "due_date"]
MONEY_CELL = re.compile(r"^\$([\d,]+\.\d{2})$")


def _receipt_invoice_number(text):
    m = re.search(r"^Receipt Number:\s*([A-Z]+-\d+|\d+)\s*$", text, re.M)
    if m:
        return m.group(1), 1.00
    m = re.search(r"^Receipt No:\s*([A-Z]+-\d+|\d+)\s*$", text, re.M)
    if m:
        return m.group(1), 0.80
    return None


def _store_vendor(text):
    m = re.search(r"^Store:\s*(.+?)\s*$", text, re.M)
    if m:
        return m.group(1), 1.00
    return None


def _paid_total(text):
    m = re.search(r"^Paid:\s*\$([\d,]+\.\d{2})\s*$", text, re.M)
    if m:
        return m.group(1).replace(",", ""), 0.80
    return None


BUILD_FIRST = {
    "invoice_number": _receipt_invoice_number,
    "vendor": _store_vendor,
    "total": _paid_total,
}


def extract_fields(text):
    """Extract the 5 fields, Build patterns first, then Learn."""
    fields = {}
    for field in FIELDS:
        result = BUILD_FIRST[field](text) if field in BUILD_FIRST else None
        if result is None:
            result = learn_extractor.EXTRACTORS[field](text)
        fields[field] = {"extracted": result[0], "confidence": result[1]}
    return fields


def extract_table(text):
    """Extract line-item rows under the stated table format."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        low = line.lower()
        if "item" not in low or "qty" not in low:
            continue
        delim = "|" if "|" in line else (";" if ";" in line else None)
        if delim is None:
            continue
        rows = []
        for row_line in lines[i + 1:]:
            if delim not in row_line:
                break
            cells = [c.strip() for c in row_line.split(delim)]
            if len(cells) != 4:
                break
            qty_ok = cells[1].isdigit()
            unit = MONEY_CELL.match(cells[2])
            line_total = MONEY_CELL.match(cells[3])
            if not (qty_ok and unit and line_total):
                break
            rows.append({
                "item": cells[0], "quantity": int(cells[1]),
                "unit_price": unit.group(1).replace(",", ""),
                "line_total": line_total.group(1).replace(",", ""),
            })
        return rows
    return []


def build_record(doc):
    """One per-document record: fields, confidences, line items.

    The record carries no ground truth, so the QA layer can
    only answer from extracted values.
    """
    fields = extract_fields(doc["text"])
    return {
        "doc_id": doc["id"], "kind": doc["kind"], "variant": doc["variant"],
        "fields": {f: fields[f]["extracted"] for f in FIELDS},
        "confidence": {f: fields[f]["confidence"] for f in FIELDS},
        "line_items": extract_table(doc["text"]),
    }


def build_records(documents=None):
    documents = DOCUMENTS if documents is None else documents
    return [build_record(d) for d in documents]
