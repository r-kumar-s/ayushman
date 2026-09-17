from django import forms

from .models import Invoice, Customer


# =========================================================
# CUSTOMER SELECT WIDGET
# =========================================================

class CustomerSelect(forms.Select):

    def create_option(
        self,
        name,
        value,
        label,
        selected,
        index,
        subindex=None,
        attrs=None,
    ):
        option = super().create_option(
            name,
            value,
            label,
            selected,
            index,
            subindex,
            attrs,
        )

        if value:
            try:
                customer = Customer.objects.get(pk=str(value))

                option["attrs"]["data-name"] = customer.name or ""
                option["attrs"]["data-phone"] = customer.phone or ""
                option["attrs"]["data-gstin"] = customer.gstin or ""
                option["attrs"]["data-billing-address"] = (
                    customer.billing_address or ""
                )
                option["attrs"]["data-shipping-address"] = (
                    customer.shipping_address or ""
                )
                option["attrs"]["data-country"] = customer.country or ""
                option["attrs"]["data-place-of-supply"] = (
                    customer.place_of_supply or ""
                )

            except (Customer.DoesNotExist, ValueError, TypeError):
                pass

        return option


# =========================================================
# INVOICE ADMIN FORM
# =========================================================

class InvoiceAdminForm(forms.ModelForm):

    # =====================================================
    # TEMPORARY PO PDF UPLOAD
    # =====================================================
    #
    # This field is NOT stored in the Invoice database.
    # It is used only by the "Read PO & Autofill" button.
    # =====================================================

    po_file = forms.FileField(
        label="Purchase Order PDF",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                "accept": ".pdf,application/pdf",
                "id": "id_po_file",
            }
        ),
        help_text=(
            "Upload an Emami or Virgo PO and click "
            "Read PO & Autofill to fill the invoice."
        ),
    )

    class Meta:
        model = Invoice
        fields = "__all__"

        widgets = {

            # =================================================
            # INVOICE DATE
            # Display format: dd-mm-yyyy
            # =================================================

            "invoice_date": forms.TextInput(
                attrs={
                    "placeholder": "dd-mm-yyyy",
                    "autocomplete": "off",
                    "class": "date-ddmmyyyy",
                }
            ),

            "po_no": forms.TextInput(),

            # =================================================
            # PO DATE
            # Display format: dd-mm-yyyy
            # =================================================

            "po_date": forms.TextInput(
                attrs={
                    "placeholder": "dd-mm-yyyy",
                    "autocomplete": "off",
                    "class": "date-ddmmyyyy",
                }
            ),

            # =================================================
            # DELIVERY DATE
            # Display format: dd-mm-yyyy
            # =================================================

            "delivery_date": forms.TextInput(
                attrs={
                    "placeholder": "dd-mm-yyyy",
                    "autocomplete": "off",
                    "class": "date-ddmmyyyy",
                }
            ),

            "transporter": forms.TextInput(),

            # =================================================
            # CUSTOMER
            # =================================================

            "customer": CustomerSelect(),

            "customer_name": forms.TextInput(
                attrs={
                    "class": "customer-auto-field"
                }
            ),

            "customer_phone": forms.TextInput(
                attrs={
                    "class": "customer-auto-field"
                }
            ),

            "customer_gstin": forms.TextInput(
                attrs={
                    "class": "customer-auto-field"
                }
            ),

            "billing_address": forms.Textarea(
                attrs={
                    "class": "customer-auto-field",
                    "rows": 3,
                }
            ),

            "shipping_address": forms.Textarea(
                attrs={
                    "class": "customer-auto-field",
                    "rows": 3,
                }
            ),

            "country": forms.TextInput(
                attrs={
                    "class": "customer-auto-field"
                }
            ),

            "place_of_supply": forms.TextInput(
                attrs={
                    "class": "customer-auto-field"
                }
            ),

            "supplier_state": forms.TextInput(),

            "supplier_state_code": forms.TextInput(),

            "amount_in_words": forms.TextInput(),
        }

    # =========================================================
    # INITIALIZE FORM
    # =========================================================

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # =====================================================
        # CUSTOMER AUTO-FILL DATA
        # =====================================================

        customer_widget = self.fields["customer"].widget

        customer_widget.customer_data = {
            str(customer.pk): {
                "name": customer.name or "",
                "phone": customer.phone or "",
                "gstin": customer.gstin or "",
                "billing_address": (
                    customer.billing_address or ""
                ),
                "shipping_address": (
                    customer.shipping_address or ""
                ),
                "country": customer.country or "",
                "place_of_supply": (
                    customer.place_of_supply or ""
                ),
            }
            for customer in Customer.objects.all()
        }

        # =====================================================
        # CUSTOMER SNAPSHOT FIELDS ARE OPTIONAL
        # =====================================================

        for field_name in [
            "customer_name",
            "customer_phone",
            "customer_gstin",
            "billing_address",
            "shipping_address",
            "country",
            "place_of_supply",
        ]:
            if field_name in self.fields:
                self.fields[field_name].required = False

        # =====================================================
        # FORMAT EXISTING DATES AS dd-mm-yyyy
        # =====================================================
        #
        # When editing an existing invoice, Django's DateField
        # normally converts the database date to YYYY-MM-DD.
        #
        # We explicitly display it as dd-mm-yyyy.
        # =====================================================

        for field_name in [
            "invoice_date",
            "po_date",
            "delivery_date",
        ]:
            field = self.fields.get(field_name)

            if field:
                field.input_formats = [
                    "%d-%m-%Y",
                ]

        # =====================================================
        # FORMAT EXISTING VALUES FOR DISPLAY
        # =====================================================

        if self.instance and self.instance.pk:

            for field_name in [
                "invoice_date",
                "po_date",
                "delivery_date",
            ]:
                value = getattr(
                    self.instance,
                    field_name,
                    None,
                )

                if value:
                    self.initial[field_name] = value.strftime(
                        "%d-%m-%Y"
                    )

        # =====================================================
        # NEW INVOICE
        # =====================================================
        #
        # Invoice model already provides today's date as the
        # default. We only control how it is displayed.
        # =====================================================

        elif not self.initial.get("invoice_date"):

            from django.utils import timezone

            self.initial["invoice_date"] = (
                timezone.localdate().strftime("%d-%m-%Y")
            )

    # =========================================================
    # VALIDATE DATE FORMAT
    # =========================================================

    def clean_invoice_date(self):
        value = self.cleaned_data.get("invoice_date")

        if not value:
            return value

        # Because the model field is a DateField, Django's
        # cleaned value will be converted back to a Python date.
        return value

    def clean_po_date(self):
        value = self.cleaned_data.get("po_date")

        if not value:
            return value

        return value

    def clean_delivery_date(self):
        value = self.cleaned_data.get("delivery_date")

        if not value:
            return value

        return value

    # =========================================================
    # VALIDATE PO PDF
    # =========================================================

    def clean_po_file(self):

        po_file = self.cleaned_data.get("po_file")

        if not po_file:
            return po_file

        name = (
            po_file.name or ""
        ).lower()

        if not name.endswith(".pdf"):
            raise forms.ValidationError(
                "Please upload a PDF purchase order."
            )

        # Maximum 10 MB
        if po_file.size > 10 * 1024 * 1024:
            raise forms.ValidationError(
                "PO PDF must be smaller than 10 MB."
            )

        return po_file