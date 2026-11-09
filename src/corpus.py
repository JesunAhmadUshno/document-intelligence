"""Synthetic plain-text corpus for Level 2 Build.

32 documents: 16 invoices, 8 purchase forms, 8 receipts, in 2
layout variants per type (6 variants). Every document is authored
for this project with invented vendor names. The documents are
plain text in the layout an OCR step would produce. There is no
OCR and no LLM in this level: see PROPOSAL.md (Build plan) for the named
substitutions.

Ground truth is built from the authored spec of each document:
the 5 Learn fields plus the line-item table rows. Line total is
quantity times unit price (Decimal arithmetic), and the document
total is the sum of its line totals, except where a document
renders a field in an unsupported format on purpose:

- B15 renders its date in words (ground truth holds the ISO
  value; the extractor is expected to miss it).
- B16 renders its total in words (ground truth holds the sum
  of its line totals; the extractor is expected to miss it).

Receipts have no due date: ground truth due_date is None, and a
correctly detected absence counts as correct, as in Learn.
"""
from decimal import Decimal

# Each spec: id, kind, variant, vendor, number, date, due_date,
# items as (item, quantity, unit price) tuples. Optional flags:
# date_words (render date in words), total_words (render total
# in words).
SPECS = [
    ("B01", "invoice", "A", "Maple Office Supplies", "INV-2001", "2026-09-01", "2026-10-01",
     [("notebooks", 10, "12.50"), ("pens", 20, "2.50"), ("folders", 5, "8.00")], {}),
    ("B02", "invoice", "B", "Harbour Print Co", "INV-2002", "2026-09-03", "2026-10-03",
     [("posters", 50, "4.20"), ("flyers", 200, "0.35")], {}),
    ("B03", "invoice", "A", "Cedar Catering", "INV-2003", "2026-09-05", "2026-10-05",
     [("sandwiches", 30, "9.50"), ("coffee urns", 4, "25.00")], {}),
    ("B04", "invoice", "B", "Elm Bookkeeping", "9101", "2026-09-07", "2026-10-07",
     [("bookkeeping hours", 8, "75.00")], {}),
    ("B05", "invoice", "A", "Northwind Traders", "INV-2005", "2026-09-09", "2026-10-09",
     [("storage boxes", 40, "6.25"), ("tape rolls", 12, "3.50"), ("labels", 10, "4.80")], {}),
    ("B06", "invoice", "B", "Birch Web Studio", "INV-2006", "2026-09-11", "2026-10-11",
     [("landing page", 1, "900.00"), ("logo revision", 2, "75.00")], {}),
    ("B07", "invoice", "A", "Maple Office Supplies", "INV-2007", "2026-09-13", "2026-10-13",
     [("printer paper", 20, "9.75"), ("ink cartridges", 6, "32.00")], {}),
    ("B08", "invoice", "B", "Willow Packaging", "INV-2008", "2026-09-15", "2026-10-15",
     [("cartons", 100, "1.85"), ("bubble wrap", 8, "14.50")], {}),
    ("B09", "invoice", "A", "Aspen Travel", "INV-2009", "2026-09-17", "2026-10-17",
     [("flights", 2, "450.00"), ("hotel nights", 3, "160.00")], {}),
    ("B10", "invoice", "B", "Harbour Print Co", "INV-2010", "2026-09-19", "2026-10-19",
     [("banners", 6, "55.00"), ("stands", 6, "20.00")], {}),
    ("B11", "invoice", "A", "Cedar Catering", "INV-2011", "2026-09-21", "2026-10-21",
     [("lunch platters", 12, "38.00"), ("desserts", 24, "6.50"), ("drinks", 30, "3.00")], {}),
    ("B12", "invoice", "B", "Maple Office Supplies", "INV-2012", "2026-09-23", "2026-10-23",
     [("desks", 4, "275.00"), ("chairs", 4, "140.00")], {}),
    ("B13", "invoice", "A", "Elm Bookkeeping", "INV-2013", "2026-09-25", "2026-10-25",
     [("payroll run", 1, "350.00"), ("tax filing", 1, "250.00")], {}),
    ("B14", "invoice", "B", "Northwind Traders", "INV-2014", "2026-09-27", "2026-10-27",
     [("shelving units", 5, "120.00"), ("casters", 20, "7.50")], {}),
    ("B15", "invoice", "A", "Aspen Travel", "INV-2015", "2026-10-15", "2026-11-15",
     [("train tickets", 4, "85.00"), ("taxis", 5, "28.00")], {"date_words": True}),
    ("B16", "invoice", "B", "Birch Web Studio", "INV-2016", "2026-09-29", "2026-10-29",
     [("hosting setup", 1, "200.00"), ("maintenance", 3, "50.00")], {"total_words": True}),
    ("B17", "form", "A", "Willow Packaging", "FRM-3017", "2026-10-01", "2026-11-01",
     [("shipping cartons", 60, "1.85"), ("tape", 10, "3.50")], {}),
    ("B18", "form", "B", "Willow Packaging", "FRM-3018", "2026-10-03", "2026-11-03",
     [("mailers", 150, "0.90"), ("seals", 10, "5.00")], {}),
    ("B19", "form", "A", "Northwind Traders", "FRM-3019", "2026-10-05", "2026-11-05",
     [("pallets", 8, "45.00"), ("wrap", 6, "18.00")], {}),
    ("B20", "form", "B", "Maple Office Supplies", "FRM-3020", "2026-10-07", "2026-11-07",
     [("binders", 25, "4.40"), ("dividers", 25, "1.60")], {}),
    ("B21", "form", "A", "Harbour Print Co", "FRM-3021", "2026-10-09", "2026-11-09",
     [("business cards", 500, "0.12"), ("envelopes", 250, "0.24")], {}),
    ("B22", "form", "B", "Cedar Catering", "FRM-3022", "2026-10-11", "2026-11-11",
     [("napkins", 200, "0.15"), ("cups", 200, "0.20"), ("plates", 200, "0.25")], {}),
    ("B23", "form", "A", "Birch Web Studio", "FRM-3023", "2026-10-13", "2026-11-13",
     [("domain renewal", 2, "15.00"), ("ssl certificate", 1, "80.00")], {}),
    ("B24", "form", "B", "Aspen Travel", "FRM-3024", "2026-10-15", "2026-11-15",
     [("airport transfers", 2, "65.00"), ("insurance", 1, "95.00")], {}),
    ("B25", "receipt", "A", "Maple Office Supplies", "RCP-4001", "2026-10-17", None,
     [("sticky notes", 6, "3.25"), ("markers", 4, "2.75")], {}),
    ("B26", "receipt", "B", "Harbour Print Co", "RCP-4002", "2026-10-18", None,
     [("photo prints", 20, "1.50"), ("frames", 3, "12.00")], {}),
    ("B27", "receipt", "A", "Cedar Catering", "RCP-4003", "2026-10-19", None,
     [("pastries", 18, "4.50"), ("juice boxes", 12, "2.00")], {}),
    ("B28", "receipt", "B", "Elm Bookkeeping", "RCP-4004", "2026-10-20", None,
     [("ledger books", 3, "22.00")], {}),
    ("B29", "receipt", "A", "Northwind Traders", "RCP-4005", "2026-10-21", None,
     [("padlocks", 4, "16.00"), ("keys", 8, "5.00")], {}),
    ("B30", "receipt", "B", "Willow Packaging", "RCP-4006", "2026-10-22", None,
     [("boxes small", 30, "1.20"), ("boxes large", 20, "2.10")], {}),
    ("B31", "receipt", "A", "Aspen Travel", "RCP-4007", "2026-10-23", None,
     [("transit passes", 5, "18.00")], {}),
    ("B32", "receipt", "B", "Birch Web Studio", "RCP-4008", "2026-10-24", None,
     [("stock photos", 10, "7.00"), ("fonts", 1, "45.00")], {}),
]

TOTAL_WORDS = {"350.00": "three hundred fifty dollars"}
DATE_WORDS = {"2026-10-15": "15 October 2026"}


def _money(value):
    return f"{Decimal(value):.2f}"


def _rows(items):
    rows = []
    for name, qty, unit in items:
        line = Decimal(unit) * qty
        rows.append({"item": name, "quantity": qty,
                     "unit_price": _money(unit), "line_total": _money(line)})
    return rows


def _table_lines(rows, variant):
    if variant == "A":
        lines = ["Item | Qty | Unit Price | Line Total"]
        lines += [f"{r['item']} | {r['quantity']} | ${r['unit_price']} | ${r['line_total']}"
                  for r in rows]
    else:
        lines = ["Item; Qty; Unit Price; Amount"]
        lines += [f"{r['item']}; {r['quantity']}; ${r['unit_price']}; ${r['line_total']}"
                  for r in rows]
    return lines


def _render(spec):
    doc_id, kind, variant, vendor, number, date, due, items, flags = spec
    rows = _rows(items)
    total = _money(sum(Decimal(r["line_total"]) for r in rows))
    date_text = DATE_WORDS[date] if flags.get("date_words") else date
    table = _table_lines(rows, variant)
    if kind == "invoice" and variant == "A":
        lines = ["INVOICE", f"Vendor: {vendor}", f"Invoice Number: {number}",
                 f"Date: {date_text}"] + table + [f"Total: ${total}", f"Due Date: {due}"]
    elif kind == "invoice":
        total_line = (f"Amount Due: {TOTAL_WORDS[total]}" if flags.get("total_words")
                      else f"Amount Due: ${total}")
        lines = ["INVOICE", f"Supplier: {vendor}", f"Invoice No: {number}",
                 f"Date: {date_text}"] + table + [total_line, f"Due: {due}"]
    elif kind == "form" and variant == "A":
        lines = ["PURCHASE FORM", f"Vendor: {vendor}", f"Invoice Number: {number}",
                 f"Date: {date_text}"] + table + [f"Total: ${total}", f"Due Date: {due}"]
    elif kind == "form":
        lines = ["PURCHASE FORM", f"Supplier: {vendor}", f"Invoice # {number}",
                 f"Date: {date_text}"] + table + [f"Total: ${total}", f"Due Date: {due}"]
    elif kind == "receipt" and variant == "A":
        lines = ["RECEIPT", f"Store: {vendor}", f"Receipt Number: {number}",
                 f"Date: {date_text}"] + table + [f"Total: ${total}"]
    else:
        lines = [vendor, f"Receipt No: {number}",
                 f"Date: {date_text}"] + table + [f"Paid: ${total}"]
    return "\n".join(lines) + "\n", rows, total


def _build_documents():
    docs = []
    for spec in SPECS:
        doc_id, kind, variant, vendor, number, date, due, items, flags = spec
        text, rows, total = _render(spec)
        docs.append({
            "id": doc_id, "kind": kind, "variant": variant, "text": text,
            "ground_truth": {
                "invoice_number": number, "date": date, "vendor": vendor,
                "total": total, "due_date": due,
            },
            "table_ground_truth": rows,
        })
    return docs


DOCUMENTS = _build_documents()
