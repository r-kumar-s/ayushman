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
        attrs=None
    ):

        option = super().create_option(
            name,
            value,
            label,
            selected,
            index,
            subindex,
            attrs
        )

        # -----------------------------------------------------
        # Get actual Customer from database
        # -----------------------------------------------------

        if value:

            try:
                customer = Customer.objects.get(
                    pk=str(value)
                )

                option["attrs"]["data-name"] = (
                    customer.name or ""
                )

                option["attrs"]["data-phone"] = (
                    customer.phone or ""
                )

                option["attrs"]["data-gstin"] = (
                    customer.gstin or ""
                )

                option["attrs"]["data-billing-address"] = (
                    customer.billing_address or ""
                )

                option["attrs"]["data-shipping-address"] = (
                    customer.shipping_address or ""
                )

                option["attrs"]["data-country"] = (
                    customer.country or ""
                )

                option["attrs"]["data-place-of-supply"] = (
                    customer.place_of_supply or ""
                )

            except (
                Customer.DoesNotExist,
                ValueError,
                TypeError
            ):
                pass

        return option


# =========================================================
# INVOICE ADMIN FORM
# =========================================================

class InvoiceAdminForm(forms.ModelForm):

    class Meta:

        model = Invoice

        fields = "__all__"

        widgets = {

            # -------------------------------------------------
            # INVOICE
            # -------------------------------------------------

            "invoice_date": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),

            "po_no": forms.TextInput(),

            "po_date": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),

            "delivery_date": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),

            "transporter": forms.TextInput(),

            # -------------------------------------------------
            # CUSTOMER
            # -------------------------------------------------

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
                    "rows": 3
                }
            ),

            "shipping_address": forms.Textarea(
                attrs={
                    "class": "customer-auto-field",
                    "rows": 3
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

            # -------------------------------------------------
            # SUPPLIER
            # -------------------------------------------------

            "supplier_state": forms.TextInput(),

            "supplier_state_code": forms.TextInput(),

            # -------------------------------------------------
            # AMOUNT
            # -------------------------------------------------

            "amount_in_words": forms.TextInput(),

        }


    def clean_customer_gstin(self):
        value = self.cleaned_data.get("customer_gstin")
        return value.upper().strip() if value else ""


    def __init__(
        self,
        *args,
        **kwargs
    ):

        super().__init__(
            *args,
            **kwargs
        )


        # =====================================================
        # CUSTOMER DATA FOR JAVASCRIPT
        # =====================================================

        customer_widget = (
            self.fields["customer"].widget
        )


        customers = Customer.objects.all()


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

            for customer in customers

        }


        # =====================================================
        # CUSTOMER SNAPSHOT FIELDS
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

                self.fields[
                    field_name
                ].required = False