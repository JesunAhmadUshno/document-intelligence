"""Cross-document question answering over extracted records.

Questions are structured dicts (type plus params), not natural
language: no LLM is available, and that substitution is named
in PROPOSAL.md (Build plan). Every answer is computed only from the
extracted records built by pipeline.py (which carry no ground
truth), and every answer cites the document ids it used.

Money answers are strings with two decimals, summed with
Decimal. Records whose extracted total is None contribute
nothing to a spend sum and are not cited for it: a missed
total therefore changes the answer, which the eval harness
measures (see the total_spend_all question).
"""
from decimal import Decimal

QUESTIONS = [
    {"id": "Q01", "type": "total_spend_per_vendor", "params": {"vendor": "Maple Office Supplies"}},
    {"id": "Q02", "type": "total_spend_per_vendor", "params": {"vendor": "Harbour Print Co"}},
    {"id": "Q03", "type": "total_spend_per_vendor", "params": {"vendor": "Cedar Catering"}},
    {"id": "Q04", "type": "total_spend_per_vendor", "params": {"vendor": "Willow Packaging"}},
    {"id": "Q05", "type": "total_spend_per_vendor", "params": {"vendor": "Aspen Travel"}},
    {"id": "Q06", "type": "total_spend_per_vendor", "params": {"vendor": "Northwind Traders"}},
    {"id": "Q07", "type": "total_spend_all", "params": {}},
    {"id": "Q08", "type": "largest_document", "params": {}},
    {"id": "Q09", "type": "count_by_vendor", "params": {"vendor": "Maple Office Supplies"}},
    {"id": "Q10", "type": "count_by_kind", "params": {"kind": "receipt"}},
    {"id": "Q11", "type": "count_by_kind", "params": {"kind": "invoice"}},
    {"id": "Q12", "type": "line_items_for_invoice", "params": {"invoice_number": "INV-2011"}},
    {"id": "Q13", "type": "line_items_for_invoice", "params": {"invoice_number": "INV-2001"}},
    {"id": "Q14", "type": "vendor_of_invoice", "params": {"invoice_number": "INV-2009"}},
    {"id": "Q15", "type": "documents_over_amount", "params": {"amount": "1000.00"}},
    {"id": "Q16", "type": "total_spend_for_kind", "params": {"kind": "form"}},
]


def _money(value):
    return f"{value:.2f}"


def _spend(records):
    """(Decimal total, cited ids) over records with a total."""
    total = Decimal("0")
    cited = []
    for r in records:
        value = r["fields"]["total"]
        if value is not None:
            total += Decimal(value)
            cited.append(r["doc_id"])
    return total, cited


def _by_invoice(records, number):
    for r in records:
        if r["fields"]["invoice_number"] == number:
            return r
    return None


def answer_question(records, question):
    """Answer one structured question from extracted records."""
    qtype = question["type"]
    params = question["params"]
    if qtype == "total_spend_per_vendor":
        sel = [r for r in records if r["fields"]["vendor"] == params["vendor"]]
        total, cited = _spend(sel)
        return {"value": _money(total), "doc_ids": cited}
    if qtype == "total_spend_all":
        total, cited = _spend(records)
        return {"value": _money(total), "doc_ids": cited}
    if qtype == "total_spend_for_kind":
        sel = [r for r in records if r["kind"] == params["kind"]]
        total, cited = _spend(sel)
        return {"value": _money(total), "doc_ids": cited}
    if qtype == "largest_document":
        best = None
        for r in records:
            value = r["fields"]["total"]
            if value is not None and (best is None or Decimal(value) > Decimal(best["fields"]["total"])):
                best = r
        return {"value": {"doc_id": best["doc_id"], "total": best["fields"]["total"]},
                "doc_ids": [best["doc_id"]]}
    if qtype == "count_by_vendor":
        sel = [r for r in records if r["fields"]["vendor"] == params["vendor"]]
        return {"value": len(sel), "doc_ids": [r["doc_id"] for r in sel]}
    if qtype == "count_by_kind":
        sel = [r for r in records if r["kind"] == params["kind"]]
        return {"value": len(sel), "doc_ids": [r["doc_id"] for r in sel]}
    if qtype == "line_items_for_invoice":
        rec = _by_invoice(records, params["invoice_number"])
        if rec is None:
            return {"value": [], "doc_ids": []}
        return {"value": rec["line_items"], "doc_ids": [rec["doc_id"]]}
    if qtype == "vendor_of_invoice":
        rec = _by_invoice(records, params["invoice_number"])
        if rec is None:
            return {"value": None, "doc_ids": []}
        return {"value": rec["fields"]["vendor"], "doc_ids": [rec["doc_id"]]}
    if qtype == "documents_over_amount":
        threshold = Decimal(params["amount"])
        sel = [r["doc_id"] for r in records
               if r["fields"]["total"] is not None and Decimal(r["fields"]["total"]) > threshold]
        return {"value": sel, "doc_ids": list(sel)}
    raise ValueError("unknown question type: " + qtype)
