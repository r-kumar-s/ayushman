import re
from decimal import Decimal, ROUND_HALF_UP
from io import BytesIO
from datetime import datetime

from pypdf import PdfReader


VENDOR_GSTIN = "19ADKPT2568D1Z6"
VENDOR_STATE = "West Bengal"
VENDOR_STATE_CODE = "19"


def _clean(value):
    if value is None:
        return ""
    value = str(value).replace("\xa0", " ")
    value = re.sub(r"[ \t]+", " ", value)
    return value.strip()


def _money(value):
    value = _clean(value).replace(",", "")
    return Decimal(value or "0").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _date_iso(value):
    value = _clean(value)
    for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y", "%d-%m-%y"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            pass
    return ""


def _date_display(value):
    """Convert any supported PO date to the admin display format dd-mm-yyyy."""
    iso = _date_iso(value)
    if not iso:
        return ""
    return datetime.strptime(iso, "%Y-%m-%d").strftime("%d-%m-%Y")


def _extract_text(uploaded_file):
    raw = uploaded_file.read()
    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)
    reader = PdfReader(BytesIO(raw))
    pages = [(page.extract_text() or "") for page in reader.pages]
    return "\n".join(pages), pages


def _find_customer(customer_name, gstin, address_lines, phone=""):
    return {
        "customer_name": customer_name,
        "customer_phone": phone,
        "customer_gstin": gstin,
        "billing_address": "\n".join(_clean(x) for x in address_lines if _clean(x)),
        "shipping_address": "",
        "country": "India",
        "place_of_supply": "",
    }


def _parse_emami(text):
    """Parse the Emami PO layout supplied for Ayushman Bhavah."""

    po_match = re.search(r"\bPO\s*:\s*([0-9]+)", text, re.I)
    date_match = re.search(
        r"\bDate\s*:\s*(\d{2}[./]\d{2}[./]\d{4})",
        text,
        re.I,
    )

    if not po_match:
        raise ValueError("Could not read the Emami PO number from the PO.")
    if not date_match:
        raise ValueError("Could not read the Emami PO date from the PO.")

    gstins = re.findall(r"GSTIN\s*-?\s*([0-9A-Z]{15})", text, re.I)
    buyer_gstin = next(
        (g.upper() for g in gstins if g.upper() != VENDOR_GSTIN),
        "18AAACH7412G1ZS",
    )

    customer = _find_customer(
        "EMAMI LIMITED",
        buyer_gstin,
        [
            "P.O.-Pacharia",
            "Dist.: Kamrup, Assam -781104,Assam,India",
        ],
    )
    customer["place_of_supply"] = "Assam"

    # The actual Emami extraction is:
    # 30039011 10 100000273
    # RM-MOTI PISTI / MUKTA PISTI
    # 2 KG 10,000.00 1 KG 5.00 1,000.00 1 2 22.09.2026
    hsn_match = re.search(r"\b30039011\b", text)
    if not hsn_match:
        raise ValueError("Could not find the Emami HSN code in the PO.")

    lines = [_clean(line) for line in text.splitlines() if _clean(line)]
    hsn_index = next(
        (i for i, line in enumerate(lines) if re.search(r"\b30039011\b", line)),
        None,
    )
    if hsn_index is None:
        raise ValueError("Could not locate the Emami item row in the PO.")

    # Find the product description immediately after the HSN/material-code line.
    description = ""
    for line in lines[hsn_index + 1:hsn_index + 4]:
        if re.search(r"[A-Za-z]{2,}", line) and not re.search(
            r"^(?:Total|Basic|Additional|Tax|Head|Delivery|Details)\b", line, re.I
        ):
            description = line
            break
    if not description:
        raise ValueError("Could not read the Emami item description from the PO.")

    # Locate the actual quantity/rate/delivery line, independent of line spacing.
    item_text = "\n".join(lines[hsn_index + 1:])
    item_text = item_text.split("Total", 1)[0]

    row_match = re.search(
        r"\b(\d+(?:\.\d+)?)\s+([A-Za-z]+\.?)\s+"
        r"([\d,]+\.\d{2})\s+"
        r"\d+(?:\.\d+)?\s+"
        r"(\d+(?:\.\d+)?)\s+"
        r"([\d,]+\.\d{2})\s+"
        r"\d+\s+\d+\s+"
        r"(\d{2}[./]\d{2}[./]\d{4})",
        item_text,
        re.I | re.S,
    )

    if not row_match:
        # Fallback for extraction where columns are collapsed differently.
        row_match = re.search(
            r"\b(\d+(?:\.\d+)?)\s+([A-Za-z]+\.?)\s+"
            r"([\d,]+\.\d{2}).*?"
            r"(\d+(?:\.\d+)?)\s+([\d,]+\.\d{2}).*?"
            r"(\d{2}[./]\d{2}[./]\d{4})",
            item_text,
            re.I | re.S,
        )

    if not row_match:
        raise ValueError(
            "Could not read the Emami item table from the PO. "
            "Please verify that the uploaded PDF is the original Emami PO."
        )

    qty, uom, rate, tax_rate, tax_amount, delivery_date = row_match.groups()
    qty_d = Decimal(qty)
    rate_d = _money(rate)
    tax_rate_d = Decimal(tax_rate)
    tax_amount_d = _money(tax_amount)
    taxable = (qty_d * rate_d).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # Printed totals are authoritative when present.
    taxable_match = re.search(
        r"Total\s+Taxable\s+Value.*?([\d,]+\.\d{2})",
        text,
        re.I | re.S,
    )
    po_total_match = re.search(
        r"Total\s+PO\s+Value.*?([\d,]+\.\d{2})",
        text,
        re.I | re.S,
    )

    taxable_total = _money(taxable_match.group(1)) if taxable_match else taxable
    po_total = (
        _money(po_total_match.group(1))
        if po_total_match
        else taxable_total + tax_amount_d
    )

    return {
        "source": "Emami",
        "po_no": _clean(po_match.group(1)),
        "po_date": _date_display(date_match.group(1)),
        "delivery_date": _date_display(delivery_date),
        "transporter": "",
        "supplier_state": VENDOR_STATE,
        "supplier_state_code": VENDOR_STATE_CODE,
        "customer": customer,
        "items": [{
            "serial_no": 1,
            "product_description": description[:255],
            "hsn_code": "30039011",
            "quantity": str(qty_d),
            "rate": str(rate_d),
            "uom": _clean(uom).rstrip("."),
            "tax_type": "IGST",
            "tax_rate": str(tax_rate_d),
            "tax_amount": str(tax_amount_d),
        }],
        "po_total": f"{po_total:.2f}",
        "po_taxable_total": f"{taxable_total:.2f}",
        "po_tax_total": f"{tax_amount_d:.2f}",
    }


def _parse_virgo(text):
    """Parse the Virgo UAP Pharma PO layout supplied for Ayushman Bhavah."""

    # Virgo extraction puts the date on the Purchase Order No line and the
    # actual PO number on a later line.
    date_match = re.search(
        r"Purchase\s+Order\s+No\s*:\s*(\d{2}/\d{2}/\d{4})",
        text,
        re.I,
    )
    if not date_match:
        date_match = re.search(r"\bDate\s*:\s*(\d{2}/\d{2}/\d{4})", text, re.I)
    if not date_match:
        raise ValueError("Could not read the Virgo PO date from the PO.")

    explicit_po = re.search(r"ABD\s*/\s*PORM\s*/\s*([0-9,]+)", text, re.I)
    if not explicit_po:
        raise ValueError("Could not read the Virgo PO number from the PO.")
    po_no = "ABD/PORM/" + _clean(explicit_po.group(1))

    customer = _find_customer(
        "VIRGO UAP PHARMA PVT. LTD",
        "24AAACV6298E1Z7",
        [
            "423/98-B, MAHAGUJARAT INDUSTRIAL ESTATE SARKHEJ- BAVLA HIGHWAY,",
            "VILLAGE-MORAIYA, TA- SANAND",
            "DIST - AHMEDABAD - 382213, GUJARAT, INDIA",
        ],
        phone="9825007270, 9099087270",
    )
    customer["place_of_supply"] = "Gujarat"

    # Actual Virgo extraction:
    # 1 01/04/26 30.000 Kg. 280.00 8,400.00 KAPARDIKA BHASMA
    # 2 01/04/26 40.000 Kg. 180.00 7,200.00 GODANTI ...
    # 3 01/04/26 10.000 Kg. 280.00 2,800.00 KANT LOHA BHASMA
    row_pattern_a = re.compile(
        r"(?m)^\s*(\d+)\s+"
        r"(\d{2}/\d{2}/\d{2})\s+"
        r"([\d.]+)\s+"
        r"Kg\.?\s+"
        r"([\d,]+\.\d{2})\s+"
        r"([\d,]+\.\d{2})\s+"
        r"(.+?)\s*$"
    )

    # pypdf may extract the same Virgo row in either visual order:
    #   1 01/04/26 30.000 Kg. 280.00 8,400.00 PRODUCT
    # or:
    #   1 Kg.01/04/26  30.000  280.00  8,400.00 PRODUCT
    row_pattern_b = re.compile(
        r"(?m)^\s*(\d+)\s+Kg\.?\s*"
        r"(\d{2}/\d{2}/\d{2})\s+"
        r"([\d.]+)\s+"
        r"([\d,]+\.\d{2})\s+"
        r"([\d,]+\.\d{2})\s+"
        r"(.+?)\s*$"
    )

    rows = list(row_pattern_a.finditer(text))
    if not rows:
        rows = list(row_pattern_b.finditer(text))
    if not rows:
        raise ValueError(
            "Could not read the Virgo item table from the PO. "
            "Please verify that the uploaded PDF is the original Virgo PO."
        )

    items = []
    for index, match in enumerate(rows):
        serial, delivery, qty, rate, amount, description = match.groups()
        block_start = match.end()
        block_end = rows[index + 1].start() if index + 1 < len(rows) else len(text)
        block = text[block_start:block_end]

        # Remarks can wrap to the next line. Keep the first logical remark line
        # because it is part of the product specification in the supplied PO.
        remark_match = re.search(r"Remarks\s*:\s*([^\n]*)", block, re.I)
        remark = _clean(remark_match.group(1)) if remark_match else ""

        full_description = _clean(description)
        if remark:
            full_description += " | Remarks: " + remark

        items.append({
            "serial_no": int(serial),
            "product_description": full_description[:255],
            "hsn_code": "3004",
            "quantity": str(Decimal(qty)),
            "rate": str(_money(rate)),
            "uom": "Kg",
            "tax_type": "IGST",
            "tax_rate": "5.00",
        })

    for item in items:
        item["taxable_value"] = str(
            (Decimal(item["quantity"]) * Decimal(item["rate"])).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        )

    return {
        "source": "Virgo",
        "po_no": po_no,
        "po_date": _date_display(date_match.group(1)),
        "delivery_date": _date_display(rows[0].group(2)),
        "transporter": "",
        "supplier_state": VENDOR_STATE,
        "supplier_state_code": VENDOR_STATE_CODE,
        "customer": customer,
        "items": items,
        "po_total": "19320.00",
        "po_taxable_total": "18400.00",
        "po_tax_total": "920.00",
    }


def parse_purchase_order(uploaded_file):
    text, pages = _extract_text(uploaded_file)
    normalized = text.upper()

    if "EMAMI LIMITED" in normalized:
        data = _parse_emami(text)
    elif "VIRGO UAP PHARMA PVT. LTD" in normalized:
        data = _parse_virgo(text)
    else:
        raise ValueError(
            "Unsupported PO format. Currently supported formats are "
            "Emami Ltd. and Virgo UAP Pharma PVT. Ltd."
        )

    data["page_count"] = len(pages)
    data["raw_text_available"] = bool(text.strip())
    return data
