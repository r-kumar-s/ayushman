from decimal import Decimal, ROUND_HALF_UP
import re

from django.db import models
from django.utils import timezone

from users.models import User


# =========================================================
# CUSTOMER MASTER
# =========================================================

class Customer(models.Model):
    """
    Customer Master.

    Customer information is maintained separately from invoices.
    """

    name = models.CharField(
        max_length=255
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )

    gstin = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )

    billing_address = models.TextField(
        blank=True,
        null=True
    )

    shipping_address = models.TextField(
        blank=True,
        null=True
    )

    country = models.CharField(
        max_length=100,
        default="India"
    )

    place_of_supply = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    # Optional link to existing patient/user.
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="customer_profiles"
    )

    active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "invoice_customers"
        ordering = ["name"]

    def __str__(self):
        return self.name


# =========================================================
# INVOICE
# =========================================================

class Invoice(models.Model):
    """
    Tax Invoice Header.

    Customer information is stored as a snapshot inside the
    invoice. Once the invoice is saved, its snapshot fields
    are NOT overwritten when the invoice is edited.
    """

    invoice_no = models.AutoField(
        primary_key=True,
        editable=False
    )

    # Public invoice number shown on the invoice, Admin and PDF.
    # invoice_no remains the internal database ID for backward compatibility.
    invoice_number = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        editable=False
    )

    invoice_date = models.DateField(
        default=timezone.localdate
    )

    # -----------------------------------------------------
    # PURCHASE ORDER
    # -----------------------------------------------------

    po_no = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    po_date = models.DateField(
        blank=True,
        null=True
    )

    delivery_date = models.DateField(
        blank=True,
        null=True
    )

    transporter = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    # -----------------------------------------------------
    # CUSTOMER MASTER
    # -----------------------------------------------------

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="invoices",
        null=True,
        blank=True
    )

    # -----------------------------------------------------
    # CUSTOMER SNAPSHOT
    # -----------------------------------------------------

    customer_name = models.CharField(
        max_length=255
    )

    customer_phone = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )

    customer_gstin = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )

    billing_address = models.TextField(
        blank=True,
        null=True
    )

    shipping_address = models.TextField(
        blank=True,
        null=True
    )

    country = models.CharField(
        max_length=100,
        default="India"
    )

    place_of_supply = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    # -----------------------------------------------------
    # SUPPLIER
    # -----------------------------------------------------

    supplier_state = models.CharField(
        max_length=100,
        default="West Bengal"
    )

    supplier_state_code = models.CharField(
        max_length=10,
        default="19"
    )

    # -----------------------------------------------------
    # TOTALS
    # -----------------------------------------------------

    taxable_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00")
    )

    tax_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00")
    )

    grand_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00")
    )

    amount_in_words = models.CharField(
        max_length=500,
        blank=True,
        null=True
    )

    # -----------------------------------------------------
    # SYSTEM DATES
    # -----------------------------------------------------

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "invoices_invoice"
        ordering = ["-invoice_no"]

    # -----------------------------------------------------
    # SAVE
    # -----------------------------------------------------

    def build_invoice_number(self):
        """Build the permanent public invoice number.

        Format:
            #AB_customername_mm_yyyy_id

        The database AutoField (invoice_no) is used as the final ID.
        Customer name is normalized only for the invoice-number text.
        """
        customer_name = (self.customer_name or "CUSTOMER").strip().upper()
        customer_name = re.sub(r"[^A-Z0-9]+", "_", customer_name)
        customer_name = customer_name.strip("_") or "CUSTOMER"

        date_value = self.invoice_date or timezone.localdate()
        prefix = f"#AB_{customer_name}_{date_value:%m_%Y}_{self.invoice_no}"

        # Keep within the database field limit while preserving the ID.
        if len(prefix) > 255:
            suffix = f"_{date_value:%m_%Y}_{self.invoice_no}"
            customer_part = max(1, 255 - len("#AB_") - len(suffix))
            customer_name = customer_name[:customer_part].rstrip("_")
            prefix = f"#AB_{customer_name}{suffix}"

        return prefix

    def save(self, *args, **kwargs):
        """
        Save the invoice exactly as entered.

        IMPORTANT:
        Customer snapshot fields are NOT overwritten here.

        The public invoice number is generated only when it does not
        already exist, so editing an invoice never changes its number.
        """

        super().save(
            *args,
            **kwargs
        )

        if not self.invoice_number:
            self.invoice_number = self.build_invoice_number()
            type(self).objects.filter(pk=self.pk).update(
                invoice_number=self.invoice_number
            )

    # -----------------------------------------------------
    # CALCULATE INVOICE TOTALS
    # -----------------------------------------------------

    def calculate_totals(self):
        """
        Calculate invoice-level totals from all invoice items.
        """

        taxable_total = Decimal("0.00")

        tax_total = Decimal("0.00")

        for item in self.items.all():

            item.calculate_totals()

            taxable_total += item.taxable_value

            tax_total += item.tax_amount

        self.taxable_total = (
            taxable_total
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

        self.tax_total = (
            tax_total
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

        self.grand_total = (
            self.taxable_total +
            self.tax_total
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

    def __str__(self):
        return (
            f"{self.invoice_number or self.invoice_no} - "
            f"{self.customer_name}"
        )


# =========================================================
# INVOICE ITEM
# =========================================================

class InvoiceItem(models.Model):
    """
    Individual product line inside an invoice.
    """

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="items"
    )

    serial_no = models.PositiveIntegerField(
        default=1
    )

    product_description = models.CharField(
        max_length=255
    )

    hsn_code = models.CharField(
        max_length=20
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=Decimal("0.000")
    )

    rate = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00")
    )

    uom = models.CharField(
        max_length=30,
        default="Kgs"
    )

    taxable_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00")
    )

    tax_type = models.CharField(
        max_length=20,
        choices=[
            ("IGST", "IGST"),
            ("CGST_SGST", "CGST + SGST"),
        ],
        default="IGST"
    )

    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("5.00")
    )

    tax_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00")
    )

    line_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00")
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "invoices_invoiceitem"
        ordering = ["serial_no"]

    def __str__(self):
        return (
            f"{self.invoice} - "
            f"{self.product_description} "
            f"({self.quantity} {self.uom})"
        )

    # -----------------------------------------------------
    # CALCULATE LINE TOTALS
    # -----------------------------------------------------

    def calculate_totals(self):
        """
        Calculate:

        Quantity × Rate = Taxable Value
        Taxable Value × Tax Rate / 100 = Tax Amount
        Taxable Value + Tax Amount = Line Total
        """

        quantity = (
            self.quantity
            or Decimal("0.000")
        )

        rate = (
            self.rate
            or Decimal("0.00")
        )

        tax_rate = (
            self.tax_rate
            or Decimal("0.00")
        )

        # Quantity × Rate
        self.taxable_value = (
            quantity * rate
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

        # Taxable × Tax Rate / 100
        self.tax_amount = (
            self.taxable_value *
            tax_rate /
            Decimal("100")
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

        # Taxable + Tax
        self.line_total = (
            self.taxable_value +
            self.tax_amount
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

        return self

    # -----------------------------------------------------
    # SAVE
    # -----------------------------------------------------

    def save(self, *args, **kwargs):
        """
        Calculate this invoice item's values before saving.
        """

        self.calculate_totals()

        super().save(
            *args,
            **kwargs
        )