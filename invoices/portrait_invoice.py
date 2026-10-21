from io import BytesIO
from decimal import Decimal
from pathlib import Path
from datetime import datetime


def number_to_words(number):
    number = Decimal(number or 0)
    rupees = int(number)
    if rupees == 0:
        return "Rupees Zero Only"

    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
            "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
            "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

    def two(n):
        if n < 20:
            return ones[n]
        return tens[n // 10] + (" " + ones[n % 10] if n % 10 else "")

    def three(n):
        if n < 100:
            return two(n)
        return ones[n // 100] + " Hundred" + (" " + two(n % 100) if n % 100 else "")

    parts = []
    crore, rupees = divmod(rupees, 10000000)
    lakh, rupees = divmod(rupees, 100000)
    thousand, rupees = divmod(rupees, 1000)

    if crore:
        parts += [three(crore), "Crore"]
    if lakh:
        parts += [three(lakh), "Lakh"]
    if thousand:
        parts += [three(thousand), "Thousand"]
    if rupees:
        parts.append(three(rupees))
    return "Rupees " + " ".join(parts) + " Only"


def _draw_wrapped(c, text, x, y, max_width, font="DejaVuSans", size=7.5, leading=3.7):
    from reportlab.pdfbase.pdfmetrics import stringWidth
    text = str(text or "")
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if stringWidth(trial, font, size) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    return y


def generate_invoice_pdf_portrait(invoice):
    """Generate the NEW portrait A4 invoice format.

    This is intentionally separate from the existing landscape generator.
    The existing generate_invoice_pdf() is not modified by this function.
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import ImageReader
        from reportlab.platypus import Table, TableStyle, Paragraph
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from django.conf import settings
        from django.http import HttpResponse
    except ImportError as exc:
        from django.http import HttpResponse
        return HttpResponse(
            f"Required PDF dependency is missing: {exc}",
            status=500,
        )

    # DejaVu Sans contains the Indian Rupee (₹) glyph.
    # Use it throughout this portrait invoice so ₹ never renders as a square.
    dejavu_regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    dejavu_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

    if not Path(dejavu_regular).exists() or not Path(dejavu_bold).exists():
        return HttpResponse(
            "DejaVu Sans fonts are not installed. "
            "Install them with: sudo apt install fonts-dejavu",
            status=500,
        )

    try:
        pdfmetrics.registerFont(
            TTFont("DejaVuSans", dejavu_regular)
        )
    except Exception:
        pass

    try:
        pdfmetrics.registerFont(
            TTFont("DejaVuSans-Bold", dejavu_bold)
        )
    except Exception:
        pass

    buffer = BytesIO()
    page_width, page_height = A4
    margin = 7 * mm
    orange = colors.HexColor("#C55A11")
    red = colors.HexColor("#B51212")
    dark = colors.HexColor("#111111")
    gray = colors.HexColor("#F3F3F3")

    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle(f"Invoice #{invoice.pk}")

    def border():
        pdf.setStrokeColor(dark)
        pdf.setLineWidth(0.8)
        pdf.rect(margin, margin, page_width - 2 * margin, page_height - 2 * margin)

    def draw_header():
        border()
        top = page_height - 18 * mm

        # Logo
        logo_path = Path(settings.BASE_DIR) / "staticfiles" / "images" / "logo_transparent_300_100.png"
        if logo_path.exists():
            pdf.drawImage(
                ImageReader(str(logo_path)),
                margin + 4 * mm,
                page_height - 30 * mm,
                width=43 * mm,
                height=15 * mm,
                preserveAspectRatio=True,
                anchor="c",
                mask="auto",
            )

        # Invoice title at top right
        pdf.setFillColor(red)
        pdf.setFont("DejaVuSans-Bold", 18)
        pdf.drawRightString(page_width - margin - 4 * mm, top + 3 * mm, "INVOICE")
        pdf.setFillColor(dark)
        pdf.setFont("DejaVuSans-Bold", 7.5)
        pdf.drawRightString(page_width - margin - 4 * mm, top - 2 * mm,
                            "Original for Recipient / Duplicate For Transporter")

        # Supplier details
        sx = margin + 4 * mm
        sy = page_height - 37 * mm
        pdf.setFont("DejaVuSans-Bold", 9)
        pdf.drawString(sx, sy, "Ayushman Bhavah")
        pdf.setFont("DejaVuSans", 7.3)
        supplier_lines = [
            "Raghunath Pur P.O. Nayasarai, P.S. Mogra",
            "Hooghly - 712513, West Bengal, India",
            "Phone No : 9831353332 / 8469260584",
            "GST Number : 19ADKPT2568D1Z6",
        ]
        for line in supplier_lines:
            sy -= 3.6 * mm
            pdf.drawString(sx, sy, line)

        # Invoice metadata
        rx = page_width - margin - 4 * mm
        y = page_height - 49 * mm
        pdf.setFillColor(red)
        pdf.setFont("DejaVuSans-Bold", 9)
        pdf.drawRightString(rx, y + 13 * mm, f"INVOICE:{invoice.pk}")
        pdf.setFillColor(dark)
        pdf.setFont("DejaVuSans-Bold", 7.5)
        metadata = [
            ("PO NO :", invoice.po_no or ""),
            ("PO DATE :", invoice.po_date.strftime("%d/%m/%Y") if invoice.po_date else ""),
            ("DELIVERY DATE:", invoice.delivery_date.strftime("%d/%m/%Y") if invoice.delivery_date else ""),
        ]
        for label, value in metadata:
            pdf.drawRightString(rx, y, f"{label}    {value}")
            y -= 4.3 * mm

        # BILL TO / SHIP TO
        section_y = page_height - 78 * mm
        left_x = margin + 4 * mm
        right_x = page_width / 2 + 3 * mm
        pdf.setFillColor(red)
        pdf.setFont("DejaVuSans-Bold", 8)
        pdf.drawString(left_x, section_y, "BILL TO:")
        pdf.drawString(right_x, section_y, "SHIP TO:")
        pdf.setFillColor(dark)
        pdf.setFont("DejaVuSans", 7.2)

        customer_nickname = (invoice.customer.nickname or "").strip() if invoice.customer else ""
        displayed_customer_name = customer_nickname or invoice.customer_name or (invoice.customer.name if invoice.customer else "")
        bill_lines = [
            displayed_customer_name,
            f"Phone : {invoice.customer_phone or ''}" if invoice.customer_phone else "",
            f"GSTIN : {invoice.customer_gstin or ''}" if invoice.customer_gstin else "",
        ] + [x for x in (invoice.billing_address or "").splitlines() if x.strip()]
        ship_lines = [
            displayed_customer_name,
            f"GSTIN : {invoice.customer_gstin or ''}" if invoice.customer_gstin else "",
            f"MB NO- {invoice.customer_phone or ''}" if invoice.customer_phone else "",
        ] + [x for x in (invoice.shipping_address or "").splitlines() if x.strip()]

        by = section_y - 5 * mm
        for line in bill_lines[:6]:
            by = _draw_wrapped(pdf, line, left_x, by, 78 * mm, size=7.2, leading=3.5 * mm)
        sy2 = section_y - 5 * mm
        for line in ship_lines[:6]:
            sy2 = _draw_wrapped(pdf, line, right_x, sy2, 78 * mm, size=7.2, leading=3.5 * mm)

        return section_y

    draw_header()

    # Table starts around the same location as the reference portrait invoice.
    table_top = page_height - 123 * mm
    items = list(invoice.items.all().order_by("serial_no"))

    # Dynamic tax label. Never change the stored tax type.
    tax_types = {item.tax_type for item in items if item.tax_type}
    if tax_types == {"CGST_SGST"}:
        tax_header = "CGST &\nSGST @\n5%"
    elif tax_types == {"IGST"}:
        tax_header = "IGST @\n5%"
    else:
        tax_header = "Tax\nAmount"

    data = [[
        "Sr.\nNo", "Product\nCode", "Item\nDescription", "NO &\nDESCRIPTION\nOF\nPACKAGES",
        "HSN\nCODE", "Quantity\n(KG)", "Rate\nPer KG", "Rate", tax_header, "Amount"
    ]]

    for idx, item in enumerate(items, start=1):
        taxable = Decimal(item.taxable_value or 0)
        tax = Decimal(item.tax_amount or 0)
        total = Decimal(item.line_total or 0)
        data.append([
            str(idx),
            "",  # No product-code field exists in current model.
            item.product_description or "",
            "",  # Package description is not stored in current model.
            item.hsn_code or "",
            f"{item.quantity:.2f}",
            f"{item.rate:,.2f}",
            f"{taxable:,.2f}",
            f"{tax:,.2f}",
            f"{total:,.2f}",
        ])

    data.append([
        "", "", "TOTAL", "", "", f"{sum((Decimal(i.quantity or 0) for i in items), Decimal('0')):g}", "",
        f"{invoice.taxable_total:,.2f}", f"{invoice.tax_total:,.2f}", f"{invoice.grand_total:,.2f}"
    ])

    widths = [8*mm, 14*mm, 30*mm, 26*mm, 14*mm, 14*mm, 15*mm, 18*mm, 20*mm, 29*mm]
    usable_width = sum(widths)
    style = ParagraphStyle("invoice_cell", fontName="DejaVuSans", fontSize=5.8, leading=6.5, alignment=TA_CENTER, wordWrap="CJK")
    head_style = ParagraphStyle("invoice_head", fontName="DejaVuSans-Bold", fontSize=5.4, leading=5.8, alignment=TA_CENTER, wordWrap="CJK")

    formatted = []
    for r, row in enumerate(data):
        formatted.append([Paragraph(str(v).replace("\n", "<br/>"), head_style if r == 0 else style) for v in row])

    table = Table(formatted, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.45, dark),
        ("BACKGROUND", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "DejaVuSans-Bold"),
        ("BACKGROUND", (0,-1), (-1,-1), colors.white),
        ("FONTNAME", (0,-1), (-1,-1), "DejaVuSans-Bold"),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 2),
        ("RIGHTPADDING", (0,0), (-1,-1), 2),
        ("TOPPADDING", (0,0), (-1,0), 4),
        ("BOTTOMPADDING", (0,0), (-1,0), 4),
        ("TOPPADDING", (0,1), (-1,-1), 3),
        ("BOTTOMPADDING", (0,1), (-1,-1), 3),
    ]))

    _, table_height = table.wrap(usable_width, 120*mm)
    table.drawOn(pdf, margin + 4*mm, table_top - table_height)
    below = table_top - table_height - 7*mm

    # Totals / amount in words
    pdf.setFont("DejaVuSans-Bold", 7.5)
    pdf.drawString(margin + 4*mm, below, "TOTAL : ₹ " + (invoice.amount_in_words or number_to_words(invoice.grand_total)).replace("Rupees ", "", 1))

    tx = page_width - margin - 67*mm
    ty = below
    pdf.setFont("DejaVuSans-Bold", 7.2)
    total_lines = [
        ("TOTAL BEFORE TAX", f"₹ {invoice.taxable_total:,.2f}"),
        ("TOTAL TAX AMOUNT", f"₹ {invoice.tax_total:,.2f}"),
        ("SHIPPING AND PACKAGING", "₹ 0"),
        ("ROUNDED OFF", "₹ 0"),
        ("TOTAL AMOUNT", f"₹ {invoice.grand_total:,.2f}"),
        ("AMOUNT DUE", f"₹ {invoice.grand_total:,.2f}"),
    ]
    for label, value in total_lines:
        pdf.drawString(tx, ty, label)
        pdf.drawRightString(page_width - margin - 4*mm, ty, value)
        ty -= 4.1*mm

    # Signature / logistics / bank area
    base_y = max(58*mm, ty - 10*mm)
    pdf.setFont("DejaVuSans-Bold", 7.5)
    pdf.line(margin + 4*mm, base_y + 8*mm, margin + 55*mm, base_y + 8*mm)
    pdf.drawString(margin + 4*mm, base_y + 4*mm, "AUTHORISED SIGNATURE")

    pdf.setFont("DejaVuSans-Bold", 7.3)
    pdf.drawString(margin + 4*mm, base_y - 5*mm, "Transporter Name")
    pdf.setFont("DejaVuSans", 7.3)
    pdf.drawString(margin + 48*mm, base_y - 5*mm, invoice.transporter or "")
    pdf.setFont("DejaVuSans-Bold", 7.3)
    pdf.drawString(margin + 4*mm, base_y - 10*mm, "Delivery at")
    pdf.drawString(margin + 4*mm, base_y - 15*mm, "Consignee Number")
    pdf.drawString(margin + 4*mm, base_y - 20*mm, "C.N. No. & Date")
    pdf.drawString(margin + 4*mm, base_y - 25*mm, "Check post")

    bx = page_width / 2 - 5*mm
    pdf.drawString(bx, base_y - 5*mm, "Bank Details")
    pdf.setFont("DejaVuSans", 7.3)
    pdf.drawString(bx + 32*mm, base_y - 5*mm, "Ayushman Bhavah")
    pdf.setFont("DejaVuSans-Bold", 7.3)
    pdf.drawString(bx, base_y - 10*mm, "Bank Name")
    pdf.setFont("DejaVuSans", 7.3)
    pdf.drawString(bx + 32*mm, base_y - 10*mm, "Bank Of Baroda")
    pdf.setFont("DejaVuSans-Bold", 7.3)
    pdf.drawString(bx, base_y - 15*mm, "Account Number")
    pdf.setFont("DejaVuSans", 7.3)
    pdf.drawString(bx + 32*mm, base_y - 15*mm, "57960200000018")
    pdf.setFont("DejaVuSans-Bold", 7.3)
    pdf.drawString(bx, base_y - 20*mm, "IFSC Code")
    pdf.setFont("DejaVuSans", 7.3)
    pdf.drawString(bx + 32*mm, base_y - 20*mm, "BARB0TRIBEN")

    # Terms
    terms_y = margin + 37*mm
    pdf.setFont("DejaVuSans-Bold", 7.5)
    pdf.drawString(margin + 4*mm, terms_y, "TERMS AND CONDITIONS")
    pdf.setFont("DejaVuSans", 6.5)
    terms = [
        "1. Subject to Kolkata Jurisdiction.",
        '2. Please pay by RTGS or Account payee cheque with the name of Ayushman Bhavah.',
        "3. Declaration: We declare that this Invoice shows the actual price of the goods described and that all particulars are true & correct.",
        "4. Payment 30 days after invoice date.",
    ]
    yy = terms_y - 4*mm
    for term in terms:
        pdf.drawString(margin + 4*mm, yy, term)
        yy -= 3.3*mm

    pdf.setFont("DejaVuSans", 6.5)
    pdf.drawRightString(page_width - margin - 4*mm, margin + 4*mm, "Email us at : contact@ayushmaanbhavah.com")

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    preferred_name = (invoice.customer.nickname or "").strip() if invoice.customer else ""
    customer_name = (preferred_name or invoice.customer_name or (invoice.customer.name if invoice.customer else "CUSTOMER")).strip().upper()
    import re
    customer_name = customer_name.replace("&", " AND ")
    customer_name = re.sub(r"[^A-Z0-9]+", "_", customer_name).strip("_") or "CUSTOMER"
    date_part = invoice.invoice_date.strftime("%d%m%Y") if invoice.invoice_date else datetime.today().strftime("%d%m%Y")
    response["Content-Disposition"] = f'inline; filename="AB_{customer_name}_{invoice.pk}_{date_part}.pdf"'
    return response
