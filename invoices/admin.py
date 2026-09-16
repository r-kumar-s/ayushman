from pathlib import Path
from io import BytesIO
from decimal import Decimal
from datetime import datetime

from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, reverse
from django.utils.html import format_html

from .models import Customer, Invoice, InvoiceItem
from .forms import InvoiceAdminForm


# =========================================================
# CUSTOMER MASTER
# =========================================================

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "phone",
        "gstin",
        "place_of_supply",
        "active",
        "created_at",
    )

    list_filter = (
        "active",
        "place_of_supply",
    )

    search_fields = (
        "name",
        "phone",
        "gstin",
    )

    ordering = (
        "name",
    )


# =========================================================
# INVOICE ITEM INLINE
# =========================================================

class InvoiceItemInline(admin.TabularInline):

    model = InvoiceItem

    extra = 1

    fields = (
        "serial_no",
        "product_description",
        "hsn_code",
        "quantity",
        "rate",
        "uom",
        "tax_type",
        "tax_rate",
        "taxable_value",
        "tax_amount",
        "line_total",
    )

    readonly_fields = (
        "taxable_value",
        "tax_amount",
        "line_total",
    )


# =========================================================
# NUMBER TO WORDS
# =========================================================

def number_to_words(number):

    number = Decimal(number or 0)

    rupees = int(number)

    if rupees == 0:
        return "Rupees Zero Only"

    ones = [
        "",
        "One",
        "Two",
        "Three",
        "Four",
        "Five",
        "Six",
        "Seven",
        "Eight",
        "Nine",
        "Ten",
        "Eleven",
        "Twelve",
        "Thirteen",
        "Fourteen",
        "Fifteen",
        "Sixteen",
        "Seventeen",
        "Eighteen",
        "Nineteen",
    ]

    tens = [
        "",
        "",
        "Twenty",
        "Thirty",
        "Forty",
        "Fifty",
        "Sixty",
        "Seventy",
        "Eighty",
        "Ninety",
    ]

    def two_digits(n):

        if n < 20:
            return ones[n]

        return (
            tens[n // 10]
            + (" " + ones[n % 10] if n % 10 else "")
        )

    def three_digits(n):

        if n < 100:
            return two_digits(n)

        return (
            ones[n // 100]
            + " Hundred"
            + (
                " " + two_digits(n % 100)
                if n % 100
                else ""
            )
        )

    words = []

    crore = rupees // 10000000
    rupees %= 10000000

    lakh = rupees // 100000
    rupees %= 100000

    thousand = rupees // 1000
    rupees %= 1000

    hundred = rupees

    if crore:
        words.append(three_digits(crore))
        words.append("Crore")

    if lakh:
        words.append(three_digits(lakh))
        words.append("Lakh")

    if thousand:
        words.append(three_digits(thousand))
        words.append("Thousand")

    if hundred:
        words.append(three_digits(hundred))

    return "Rupees " + " ".join(words) + " Only"


# =========================================================
# PDF GENERATOR
# =========================================================

def generate_invoice_pdf(invoice):

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import ImageReader
        from reportlab.platypus import Table, TableStyle, Paragraph
    except ImportError:

        return HttpResponse(
            "ReportLab is not installed. Run: "
            "python3 -m pip install reportlab",
            status=500,
        )

    buffer = BytesIO()

    page_width, page_height = landscape(A4)

    pdf = canvas.Canvas(
        buffer,
        pagesize=(page_width, page_height),
    )

    # =====================================================
    # COLORS
    # =====================================================

    orange = colors.HexColor("#C55A11")
    dark = colors.HexColor("#111111")
    light_gray = colors.HexColor("#F3F3F3")

    # =====================================================
    # PAGE BORDER
    # =====================================================

    margin = 4.5 * mm

    pdf.setStrokeColor(dark)
    pdf.setLineWidth(1)

    pdf.rect(
        margin,
        margin,
        page_width - (2 * margin),
        page_height - (2 * margin),
    )

    # =====================================================
    # SUPPLIER HEADER
    # =====================================================

    top = page_height - 12 * mm

    pdf.setFont(
        "Helvetica-Bold",
        12,
    )

    pdf.drawString(
        margin + 3 * mm,
        top,
        "AYUSHMAN BHAVAH",
    )

    pdf.setFont(
        "Helvetica",
        7.5,
    )

    supplier_lines = [
        "Raghunath Pur, P.O. Nayasarai, P.S. Mogra",
        "Hooghly - 712513, West Bengal, India",
        "Phone : 9831353332 / 8469260584",
        "GSTIN : 19ADKPT2568D1Z6",
    ]

    y = top - 4 * mm

    for line in supplier_lines:

        pdf.drawString(
            margin + 3 * mm,
            y,
            line,
        )

        y -= 3.5 * mm

    # =====================================================
    # AYUSHMAN BHAVAH LOGO
    # =====================================================
    #
    # The logo is loaded from the same project assets used by
    # the website/invoice implementation. Several common paths
    # are checked so it works in local and production setups.
    # =====================================================

    from django.conf import settings

    # Exact logo path requested for this installation.
    logo_path = (
        Path(settings.BASE_DIR)
        / "staticfiles"
        / "images"
        / "logo_transparent_300_100.png"
    )

    if logo_path:

        logo_width = 55 * mm
        logo_height = 18 * mm

        logo_x = (
            page_width / 2
            - logo_width / 2
        )

        logo_y = (
            page_height
            - 24 * mm
        )

        pdf.drawImage(
            ImageReader(str(logo_path)),
            logo_x,
            logo_y,
            width=logo_width,
            height=logo_height,
            preserveAspectRatio=True,
            anchor="c",
            mask="auto",
        )

    # =====================================================
    # CENTER TITLE
    # =====================================================

    # =====================================================
    # TAX INVOICE TITLE BETWEEN ORANGE LINES
    # =====================================================

    line_y = page_height - 33.5 * mm

    pdf.setFillColor(orange)
    pdf.setStrokeColor(orange)
    pdf.setLineWidth(1.2)

    title = "TAX INVOICE"

    pdf.setFont(
        "Helvetica-Bold",
        14,
    )

    title_width = pdf.stringWidth(
        title,
        "Helvetica-Bold",
        14,
    )

    gap = 5 * mm

    center_x = page_width / 2

    # Left orange line
    pdf.line(
        margin + 2 * mm,
        line_y,
        center_x - (title_width / 2) - gap,
        line_y,
    )

    # Right orange line
    pdf.line(
        center_x + (title_width / 2) + gap,
        line_y,
        page_width - margin - 2 * mm,
        line_y,
    )

    # TAX INVOICE
    pdf.setFillColor(orange)

    pdf.drawCentredString(
        center_x,
        line_y - 2.5 * mm,
        title,
    )

    pdf.setFillColor(dark)
    pdf.setStrokeColor(dark)

    # =====================================================
    # INVOICE DETAILS
    # =====================================================

    right_x = page_width - 78 * mm

    pdf.setFont(
        "Helvetica",
        8,
    )

    invoice_date = (
        invoice.invoice_date.strftime("%d-%b-%y")
        if invoice.invoice_date
        else ""
    )

    po_date = (
        invoice.po_date.strftime("%d-%b-%y")
        if invoice.po_date
        else ""
    )

    delivery_date = (
        invoice.delivery_date.strftime("%d-%b-%y")
        if invoice.delivery_date
        else ""
    )

    details = [
        ("Invoice Date :", invoice_date),
        ("Invoice No. :", str(invoice.invoice_no)),
        ("Purchase Order No.", invoice.po_no or ""),
        ("Purchase Order Date", po_date),
        ("Delivery Date", delivery_date),
    ]

    detail_y = top

    for label, value in details:

        pdf.setFont(
            "Helvetica-Bold",
            7.5,
        )

        pdf.drawString(
            right_x,
            detail_y,
            label,
        )

        pdf.setFont(
            "Helvetica",
            7.5,
        )

        pdf.drawString(
            right_x + 34 * mm,
            detail_y,
            value,
        )

        detail_y -= 4 * mm

    # =====================================================
    # CUSTOMER SECTION
    # =====================================================

    customer_top = line_y - 8 * mm

    col1 = margin + 3 * mm
    col2 = page_width / 2 - 30 * mm
    col3 = page_width - 82 * mm

    pdf.setFont(
        "Helvetica-Bold",
        8,
    )

    pdf.drawString(
        col1,
        customer_top,
        "Customer Name",
    )

    pdf.drawString(
        col2,
        customer_top,
        "Billing Address",
    )

    pdf.drawString(
        col3,
        customer_top,
        "Shipping Address",
    )

    pdf.setFont(
        "Helvetica",
        7.5,
    )

    customer_y = customer_top - 5 * mm

    customer_name = invoice.customer_name or ""

    customer_phone = invoice.customer_phone or ""

    customer_gstin = invoice.customer_gstin or ""

    billing = invoice.billing_address or ""

    shipping = invoice.shipping_address or ""

    pdf.drawString(
        col1,
        customer_y,
        customer_name,
    )

    pdf.drawString(
        col1,
        customer_y - 4 * mm,
        "Phone : " + customer_phone,
    )

    pdf.drawString(
        col1,
        customer_y - 8 * mm,
        "GSTIN : " + customer_gstin,
    )

    # Billing address

    billing_lines = billing.splitlines()

    by = customer_y

    for line in billing_lines[:4]:

        pdf.drawString(
            col2,
            by,
            line,
        )

        by -= 4 * mm

    # Shipping address

    shipping_lines = shipping.splitlines()

    sy = customer_y

    for line in shipping_lines[:4]:

        pdf.drawString(
            col3,
            sy,
            line,
        )

        sy -= 4 * mm

    # =====================================================
    # COUNTRY / PLACE OF SUPPLY
    # =====================================================

    country_y = line_y - 36.5 * mm

    pdf.setFillColor(light_gray)

    pdf.rect(
        margin + 2 * mm,
        country_y,
        page_width - 2 * margin - 4 * mm,
        7 * mm,
        fill=1,
        stroke=0,
    )

    pdf.setFillColor(dark)

    pdf.setFont(
        "Helvetica-Bold",
        7.5,
    )

    pdf.drawString(
        margin + 4 * mm,
        country_y + 2.5 * mm,
        "Country of supply :",
    )

    pdf.setFont(
        "Helvetica",
        7.5,
    )

    pdf.drawString(
        margin + 34 * mm,
        country_y + 2.5 * mm,
        invoice.country or "India",
    )

    pdf.setFont(
        "Helvetica-Bold",
        7.5,
    )

    pdf.drawString(
        page_width / 2,
        country_y + 2.5 * mm,
        "Place of Supply :",
    )

    pdf.setFont(
        "Helvetica",
        7.5,
    )

    pdf.drawString(
        page_width / 2 + 32 * mm,
        country_y + 2.5 * mm,
        invoice.place_of_supply or "",
    )

    # =====================================================
    # PRODUCT TABLE
    # =====================================================

    items = invoice.items.all().order_by(
        "serial_no"
    )

    table_data = [
        [
            "Sl.",
            "Product Description",
            "HSN\nCode",
            "Qty\n(in UoM)",
            "Rate\n/ UoM",
            "UoM",
            "Taxable value",
            "Tax Type",
            "Tax Rate",
            "Total Tax Amount",
            "Total",
        ]
    ]

    for index, item in enumerate(items, start=1):

        taxable = Decimal(
            item.taxable_value or 0
        )

        tax = Decimal(
            item.tax_amount or 0
        )

        total = Decimal(
            item.line_total or 0
        )

        table_data.append(
            [
                str(index),
                item.product_description or "",
                item.hsn_code or "",
                f"{item.quantity:.2f}",
                f"{item.rate:.2f}",
                item.uom or "",
                f"{taxable:,.2f}",
                item.tax_type or "",
                f"{item.tax_rate:.0f}%",
                f"{tax:,.2f}",
                f"{total:,.2f}",
            ]
        )

    # TOTAL ROW

    table_data.append(
        [
            "",
            "TOTAL -",
            "",
            "",
            "",
            "",
            f"{invoice.taxable_total:,.2f}",
            "",
            "",
            f"{invoice.tax_total:,.2f}",
            f"{invoice.grand_total:,.2f}",
        ]
    )

    table_x = margin + 1 * mm

    # The table Y position is calculated after ReportLab measures
    # the actual table height. This is essential because the
    # number of invoice items can change.

    table_width = (
        page_width - 0 * margin - 4 * mm
    )

    col_widths = [
        8 * mm,
        52 * mm,
        20 * mm,
        22 * mm,
        22 * mm,
        15 * mm,
        27 * mm,
        22 * mm,
        25 * mm,
        35 * mm,
        35 * mm,
    ]

    table = Table(
        table_data,
        colWidths=col_widths,
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    dark,
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    6.5,
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER",
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    dark,
                ),
                (
                    "BACKGROUND",
                    (0, -1),
                    (-1, -1),
                    orange,
                ),
                (
                    "TEXTCOLOR",
                    (0, -1),
                    (-1, -1),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, -1),
                    (-1, -1),
                    "Helvetica-Bold",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
            ]
        )
    )

    # =====================================================
    # CALCULATE PRODUCT TABLE HEIGHT AND POSITION
    # =====================================================
    #
    # The TOP of the product table is fixed just below the
    # Country / Place of Supply row.
    #
    # ReportLab then gives us the REAL table height. We calculate
    # the bottom from that height.
    #
    # This fixes BOTH cases:
    #   - few items: no huge blank space before the table
    #   - many items: everything below follows the table downward
    # =====================================================

    table_width_actual, table_height = table.wrap(
        table_width,
        100 * mm,
    )

    table_top = country_y - 4 * mm

    table_y = table_top - table_height

    table.drawOn(
        pdf,
        table_x,
        table_y,
    )

    # =====================================================
    # AMOUNT IN WORDS
    # =====================================================

    words_y = table_y - 8 * mm

    pdf.setFont(
        "Helvetica-Bold",
        7.5,
    )

    pdf.setFillColor(orange)

    pdf.drawString(
        table_x,
        words_y,
        "Amount (in words) :",
    )

    pdf.setFillColor(dark)

    pdf.setFont(
        "Helvetica",
        7.5,
    )

    amount_words = (
        invoice.amount_in_words
        or number_to_words(
            invoice.grand_total
        )
    )

    pdf.drawString(
        table_x + 40 * mm,
        words_y,
        amount_words,
    )

    # =====================================================
    # HSN TAX DETAILS
    # =====================================================
    #
    # IMPORTANT FIX:
    # hsn_table height is calculated dynamically. The table is
    # positioned directly below Amount in Words. This means that
    # adding more HSN codes increases the table downward without
    # overwriting the Transporter / Bank section.
    # =====================================================

    hsn_data = [
        [
            "HSN tax details",
            "IGST",
            "CGST",
            "SGST",
        ]
    ]

    hsn_summary = {}

    for item in items:

        hsn = item.hsn_code or ""

        if hsn not in hsn_summary:

            hsn_summary[hsn] = {
                "igst": Decimal("0.00"),
                "cgst": Decimal("0.00"),
                "sgst": Decimal("0.00"),
            }

        tax = Decimal(
            item.tax_amount or 0
        )

        if item.tax_type == "IGST":

            hsn_summary[hsn]["igst"] += tax

        else:

            half = tax / Decimal("2")

            hsn_summary[hsn]["cgst"] += half
            hsn_summary[hsn]["sgst"] += half

    for hsn, values in hsn_summary.items():

        hsn_data.append(
            [
                hsn,
                (
                    f"{values['igst']:,.2f}"
                    if values["igst"]
                    else "-"
                ),
                (
                    f"{values['cgst']:,.2f}"
                    if values["cgst"]
                    else "-"
                ),
                (
                    f"{values['sgst']:,.2f}"
                    if values["sgst"]
                    else "-"
                ),
            ]
        )

    hsn_table = Table(
        hsn_data,
        colWidths=[
            55 * mm,
            25 * mm,
            25 * mm,
            25 * mm,
        ],
    )

    hsn_table.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    dark,
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (-1, -1),
                    "CENTER",
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
            ]
        )
    )

    hsn_width, hsn_height = hsn_table.wrap(
        130 * mm,
        100 * mm,
    )

    # HSN table top starts a small distance below Amount in Words.
    hsn_top = words_y - 7 * mm

    # ReportLab drawOn() receives the bottom-left Y coordinate.
    hsn_bottom = hsn_top - hsn_height

    hsn_table.drawOn(
        pdf,
        table_x,
        hsn_bottom,
    )

    # =====================================================
    # TRANSPORTER
    # =====================================================
    #
    # Position transporter below the REAL bottom of the HSN
    # table, not at a fixed page position.
    # =====================================================

    transporter_y = hsn_bottom - 5 * mm

    pdf.setFont(
        "Helvetica-Bold",
        7.5,
    )

    pdf.drawString(
        table_x,
        transporter_y,
        "Transporter Name :",
    )

    pdf.setFont(
        "Helvetica",
        7.5,
    )

    pdf.drawString(
        table_x + 28 * mm,
        transporter_y,
        invoice.transporter or "",
    )

    # =====================================================
    # BANK DETAILS
    # =====================================================

    bank_y = transporter_y - 5 * mm

    pdf.setFont(
        "Helvetica-Bold",
        7.5,
    )

    pdf.drawString(
        table_x,
        bank_y,
        "Bank Name :",
    )

    pdf.setFont(
        "Helvetica",
        7.5,
    )

    pdf.drawString(
        table_x + 28 * mm,
        bank_y,
        "Bank of Baroda",
    )

    account_y = bank_y - 5 * mm

    pdf.setFont(
        "Helvetica-Bold",
        7.5,
    )

    pdf.drawString(
        table_x,
        account_y,
        "Account No.:",
    )

    pdf.setFont(
        "Helvetica",
        7.5,
    )

    pdf.drawString(
        table_x + 28 * mm,
        account_y,
        "57960200000018",
    )

    # IFSC on a separate line
    ifsc_y = account_y - 5 * mm

    pdf.setFont(
        "Helvetica-Bold",
        7.5,
    )

    pdf.drawString(
        table_x,
        ifsc_y,
        "IFSC Code :",
    )

    pdf.setFont(
        "Helvetica",
        7.5,
    )

    pdf.drawString(
        table_x + 28 * mm,
        ifsc_y,
        "BARB0TRIBEN",
    )

    # =====================================================
    # AUTHORIZED SIGNATORY
    # =====================================================
    #
    # Signature remains anchored on the right side of the page.
    # It is independent of the left-side flowing invoice details.
    # =====================================================

    sign_y = 36 * mm
    sign_x = page_width - 78 * mm

    pdf.line(
        sign_x,
        sign_y + 8 * mm,
        page_width - 20 * mm,
        sign_y + 8 * mm,
    )

    pdf.setFont(
        "Helvetica",
        7,
    )

    pdf.drawCentredString(
        sign_x + 29 * mm,
        sign_y + 4 * mm,
        "Authorized Signatory",
    )

    # =====================================================
    # TERMS
    # =====================================================
    #
    # Terms now follow Account No. dynamically.
    # =====================================================

    terms_y = ifsc_y - 8 * mm

    pdf.setFont(
        "Helvetica-Bold",
        7.5,
    )

    pdf.drawString(
        table_x,
        terms_y,
        "TERMS AND CONDITIONS",
    )

    pdf.setFont(
        "Helvetica",
        6.5,
    )

    terms = [
        '1. Subject to Kolkata Jurisdiction.',
        '2. Please pay by RTGS or Account payee cheque in the name of "Ayushman Bhavah".',
        '3. Declaration: We declare that this Invoice shows the actual price of the goods described and that all particulars are true & correct.',
        '4. Invoice is payable within 30 days.',
    ]

    ty = terms_y - 4 * mm

    for term in terms:

        pdf.drawString(
            table_x,
            ty,
            term,
        )

        ty -= 3.2 * mm

    # =====================================================
    # EMAIL
    # =====================================================

    pdf.setFont(
        "Helvetica-Bold",
        7,
    )

    pdf.drawCentredString(
        page_width / 2,
        margin + 2 * mm,
        "Email us at : contact@ayushmaanbhavah.com",
    )

    # =====================================================
    # FINISH
    # =====================================================

    pdf.showPage()
    pdf.save()

    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/pdf",
    )

    response[
        "Content-Disposition"
    ] = (
        f'inline; filename="Invoice_{invoice.invoice_no}.pdf"'
    )

    return response


# =========================================================
# INVOICE ADMIN
# =========================================================

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):

    form = InvoiceAdminForm

    # =====================================================
    # JAVASCRIPT
    # =====================================================

    class Media:

        js = (
            "invoices/js/invoice_admin.js",
        )

    # =====================================================
    # LIST PAGE
    # =====================================================

    list_display = (
        "invoice_no",
        "invoice_date",
        "customer",
        "grand_total",
        "created_at",
        "invoice_actions",
    )

    list_filter = (
        "invoice_date",
        "transporter",
    )

    search_fields = (
        "customer__name",
        "customer_name",
        "customer_gstin",
        "po_no",
    )

    ordering = (
        "-invoice_no",
    )

    # =====================================================
    # LIST ACTION BUTTONS
    # =====================================================

    @admin.display(
        description="Actions"
    )
    def invoice_actions(self, obj):

        edit_url = reverse(
            "admin:invoices_invoice_change",
            args=[obj.pk],
        )

        delete_url = reverse(
            "admin:invoices_invoice_delete",
            args=[obj.pk],
        )

        pdf_url = reverse(
            "admin:invoices_invoice_pdf",
            args=[obj.pk],
        )

        return format_html(
            '<a class="button" '
            'href="{}" '
            'style="margin-right:4px;">Edit</a> '
            '<a class="button" '
            'href="{}" '
            'style="margin-right:4px; color:#ba2121;">Delete</a> '
            '<a class="button" '
            'href="{}" '
            'target="_blank">PDF</a>',
            edit_url,
            delete_url,
            pdf_url,
        )

    # =====================================================
    # CUSTOM ADMIN URLS
    # =====================================================

    def get_urls(self):

        urls = super().get_urls()

        custom_urls = [
            path(
                "<path:object_id>/pdf/",
                self.admin_site.admin_view(
                    self.invoice_pdf_view
                ),
                name="invoices_invoice_pdf",
            ),
        ]

        return custom_urls + urls

    # =====================================================
    # PDF VIEW
    # =====================================================

    def invoice_pdf_view(
        self,
        request,
        object_id,
    ):

        invoice = self.get_object(
            request,
            object_id,
        )

        if invoice is None:

            from django.http import Http404

            raise Http404(
                "Invoice does not exist."
            )

        return generate_invoice_pdf(
            invoice
        )

    # =====================================================
    # READONLY FIELDS
    # =====================================================

    readonly_fields = (
        "invoice_no",
        "taxable_total",
        "tax_total",
        "grand_total",
    )

    # =====================================================
    # FORM FIELD ORDER
    # =====================================================

    fields = (
        "invoice_no",
        "invoice_date",

        "po_no",
        "po_date",
        "delivery_date",
        "transporter",

        "customer",

        "customer_name",
        "customer_phone",
        "customer_gstin",
        "billing_address",
        "shipping_address",
        "country",
        "place_of_supply",

        "supplier_state",
        "supplier_state_code",

        "taxable_total",
        "tax_total",
        "grand_total",
        "amount_in_words",
    )

    # =====================================================
    # PRODUCT ITEMS
    # =====================================================

    inlines = (
        InvoiceItemInline,
    )

    # =====================================================
    # SAVE FORMSET
    # =====================================================

    # =========================================================
    # SAVE INVOICE HEADER
    # =========================================================

    def save_model(
        self,
        request,
        obj,
        form,
        change,
    ):
        # Save ONLY the Invoice record.
        # Editing an invoice must NEVER modify Customer master data.
        super().save_model(
            request,
            obj,
            form,
            change,
        )


    # =========================================================
    # SAVE RELATED ITEMS + RECALCULATE INVOICE TOTALS
    # =========================================================

    def save_related(
        self,
        request,
        form,
        formsets,
        change,
    ):

        # Let Django save/update/delete all InvoiceItem rows.
        super().save_related(
            request,
            form,
            formsets,
            change,
        )

        invoice = form.instance

        # Recalculate every saved item and the invoice totals.
        invoice.calculate_totals()

        # Update ONLY calculated totals in the database.
        # We intentionally do not call invoice.save() here because
        # Invoice.save() also refreshes the customer snapshot fields.
        Invoice.objects.filter(
            pk=invoice.pk
        ).update(
            taxable_total=invoice.taxable_total,
            tax_total=invoice.tax_total,
            grand_total=invoice.grand_total,
        )
