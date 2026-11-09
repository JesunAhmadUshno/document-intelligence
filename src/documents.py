"""Synthetic plain-text document fixtures for Level 1 Learn.

Every document in this file was authored for this project and is
labelled synthetic. They are plain text, not scans or photographs,
so there is no OCR in this level. No real document, no real person,
and no real company appears: vendor names are invented.

Ground truth is the labelled value for each of the five fields,
written by hand from the document text. A field with ground truth
None is genuinely absent from the document (D04 due_date). D08
carries a date in an unsupported format and a total written in
words: its ground truth holds the true values, and the extractor
is expected to miss both.
"""

FIELDS = ["invoice_number", "date", "vendor", "total", "due_date"]

DOCUMENTS = [
    {
        "id": "D01", "kind": "invoice",
        "text": (
            "INVOICE\n"
            "Vendor: Maple Office Supplies\n"
            "Invoice Number: INV-1001\n"
            "Date: 2026-09-01\n"
            "Item: notebooks\n"
            "Total: $1250.00\n"
            "Due Date: 2026-10-01\n"
        ),
        "ground_truth": {
            "invoice_number": "INV-1001", "date": "2026-09-01",
            "vendor": "Maple Office Supplies", "total": "1250.00",
            "due_date": "2026-10-01",
        },
    },
    {
        "id": "D02", "kind": "invoice",
        "text": (
            "INVOICE\n"
            "Vendor: Harbour Print Co\n"
            "Invoice Number: INV-1002\n"
            "Date: 2026-09-03\n"
            "Item: poster printing\n"
            "Total: $240.75\n"
            "Due Date: 2026-10-03\n"
        ),
        "ground_truth": {
            "invoice_number": "INV-1002", "date": "2026-09-03",
            "vendor": "Harbour Print Co", "total": "240.75",
            "due_date": "2026-10-03",
        },
    },
    {
        "id": "D03", "kind": "invoice",
        "text": (
            "INVOICE\n"
            "Vendor: Cedar Catering\n"
            "Invoice No: 8842\n"
            "Date: 2026-09-15\n"
            "Item: event catering\n"
            "Total: $89.99\n"
            "Due: 2026-10-15\n"
        ),
        "ground_truth": {
            "invoice_number": "8842", "date": "2026-09-15",
            "vendor": "Cedar Catering", "total": "89.99",
            "due_date": "2026-10-15",
        },
    },
    {
        "id": "D04", "kind": "invoice",
        "text": (
            "INVOICE\n"
            "Vendor: Elm Bookkeeping\n"
            "Invoice Number: INV-1004\n"
            "Date: 2026-09-20\n"
            "Item: monthly bookkeeping\n"
            "Total: $600.00\n"
            "Payment terms: on receipt\n"
        ),
        "ground_truth": {
            "invoice_number": "INV-1004", "date": "2026-09-20",
            "vendor": "Elm Bookkeeping", "total": "600.00",
            "due_date": None,
        },
    },
    {
        "id": "D05", "kind": "invoice",
        "text": (
            "Northwind Traders\n"
            "Invoice Number: INV-1005\n"
            "Date: 2026-09-22\n"
            "Item: storage boxes\n"
            "Amount Due: $430.50\n"
            "Due Date: 2026-10-22\n"
        ),
        "ground_truth": {
            "invoice_number": "INV-1005", "date": "2026-09-22",
            "vendor": "Northwind Traders", "total": "430.50",
            "due_date": "2026-10-22",
        },
    },
    {
        "id": "D06", "kind": "invoice",
        "text": (
            "INVOICE\n"
            "Vendor: Birch Web Studio\n"
            "Invoice Number: INV-1006\n"
            "Issued 2026-08-20 for services rendered.\n"
            "Item: landing page design\n"
            "Total: $975.25\n"
            "Due Date: 2026-09-20\n"
        ),
        "ground_truth": {
            "invoice_number": "INV-1006", "date": "2026-08-20",
            "vendor": "Birch Web Studio", "total": "975.25",
            "due_date": "2026-09-20",
        },
    },
    {
        "id": "D07", "kind": "form",
        "text": (
            "PURCHASE FORM\n"
            "Supplier: Willow Packaging\n"
            "Invoice # INV-1007\n"
            "Date: 2026-10-02\n"
            "Item: shipping cartons\n"
            "Total: $312.40\n"
            "Due Date: 2026-11-02\n"
        ),
        "ground_truth": {
            "invoice_number": "INV-1007", "date": "2026-10-02",
            "vendor": "Willow Packaging", "total": "312.40",
            "due_date": "2026-11-02",
        },
    },
    {
        "id": "D08", "kind": "invoice",
        "text": (
            "INVOICE\n"
            "Vendor: Aspen Travel\n"
            "Invoice Number: INV-1008\n"
            "Date: 15 October 2026\n"
            "Item: conference travel\n"
            "Total: one hundred dollars\n"
            "Due Date: 2026-11-15\n"
        ),
        "ground_truth": {
            "invoice_number": "INV-1008", "date": "2026-10-15",
            "vendor": "Aspen Travel", "total": "100.00",
            "due_date": "2026-11-15",
        },
    },
]
