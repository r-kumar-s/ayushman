(function () {
    "use strict";

    console.log("Ayushman Bhavah Invoice Admin JS loaded");


    // =========================================================
    // NUMBER
    // =========================================================

    function getNumber(value) {

        if (value === null || value === undefined) {
            return 0;
        }

        var n = parseFloat(
            String(value).replace(/,/g, "").trim()
        );

        return isNaN(n) ? 0 : n;
    }


    // =========================================================
    // ROUND
    // =========================================================

    function money(value) {

        return Math.round(
            (value + Number.EPSILON) * 100
        ) / 100;

    }


    // =========================================================
    // CUSTOMER AUTO POPULATE
    // =========================================================

    function populateCustomerFields() {

        var customerSelect =
            document.getElementById("id_customer");

        if (!customerSelect) {

            console.warn(
                "Customer dropdown not found."
            );

            return;
        }


        var selectedOption =
            customerSelect.options[
                customerSelect.selectedIndex
            ];


        if (!selectedOption || !selectedOption.value) {

            console.log(
                "No customer selected."
            );

            return;
        }


        console.log(
            "Selected customer:",
            selectedOption.text
        );


        // -----------------------------------------------------
        // Read customer data from OPTION data-* attributes
        // -----------------------------------------------------

        var name =
            selectedOption.getAttribute("data-name") || "";

        var phone =
            selectedOption.getAttribute("data-phone") || "";

        var gstin =
            selectedOption.getAttribute("data-gstin") || "";

        var billingAddress =
            selectedOption.getAttribute(
                "data-billing-address"
            ) || "";

        var shippingAddress =
            selectedOption.getAttribute(
                "data-shipping-address"
            ) || "";

        var country =
            selectedOption.getAttribute(
                "data-country"
            ) || "";

        var placeOfSupply =
            selectedOption.getAttribute(
                "data-place-of-supply"
            ) || "";


        console.log(
            "Customer data:",
            {
                name: name,
                phone: phone,
                gstin: gstin,
                billingAddress: billingAddress,
                shippingAddress: shippingAddress,
                country: country,
                placeOfSupply: placeOfSupply
            }
        );


        // -----------------------------------------------------
        // Populate fields
        // -----------------------------------------------------

        setCustomerField(
            "id_customer_name",
            name
        );


        setCustomerField(
            "id_customer_phone",
            phone
        );


        setCustomerField(
            "id_customer_gstin",
            gstin
        );


        setCustomerField(
            "id_billing_address",
            billingAddress
        );


        setCustomerField(
            "id_shipping_address",
            shippingAddress
        );


        setCustomerField(
            "id_country",
            country
        );


        setCustomerField(
            "id_place_of_supply",
            placeOfSupply
        );


        // -----------------------------------------------------
        // GSTIN uppercase
        // -----------------------------------------------------

        var gstinField =
            document.getElementById(
                "id_customer_gstin"
            );

        if (gstinField) {

            gstinField.value =
                gstinField.value.toUpperCase();

        }


        console.log(
            "Customer fields populated successfully."
        );

    }


    // =========================================================
    // SET CUSTOMER FIELD
    // =========================================================

    function setCustomerField(
        fieldId,
        value
    ) {

        var field =
            document.getElementById(fieldId);


        if (!field) {

            console.warn(
                "Customer field not found:",
                fieldId
            );

            return;
        }


        field.value = value || "";


        // Trigger Django/Admin listeners if any

        field.dispatchEvent(
            new Event(
                "change",
                {
                    bubbles: true
                }
            )
        );

    }


    // =========================================================
    // CUSTOMER DROPDOWN EVENT
    // =========================================================

    function initializeCustomerAutoFill() {

        var customerSelect =
            document.getElementById(
                "id_customer"
            );


        if (!customerSelect) {

            console.warn(
                "id_customer dropdown not found."
            );

            return;
        }


        console.log(
            "Customer auto-fill initialized."
        );


        // -----------------------------------------------------
        // When customer changes
        // -----------------------------------------------------

        customerSelect.addEventListener(
            "change",
            function () {

                populateCustomerFields();

            }
        );



    }


    // =========================================================
    // AMOUNT IN WORDS
    // =========================================================

    function numberToWords(number) {

        number = Math.round(
            getNumber(number)
        );


        if (number === 0) {

            return "Rupees Zero Only";

        }


        var ones = [
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
            "Nineteen"
        ];


        var tens = [
            "",
            "",
            "Twenty",
            "Thirty",
            "Forty",
            "Fifty",
            "Sixty",
            "Seventy",
            "Eighty",
            "Ninety"
        ];


        function twoDigits(n) {

            if (n < 20) {

                return ones[n];

            }


            return (
                tens[Math.floor(n / 10)] +
                (
                    n % 10
                        ? " " + ones[n % 10]
                        : ""
                )
            );

        }


        function threeDigits(n) {

            if (n < 100) {

                return twoDigits(n);

            }


            return (
                ones[Math.floor(n / 100)] +
                " Hundred" +
                (
                    n % 100
                        ? " " + twoDigits(n % 100)
                        : ""
                )
            );

        }


        var words = [];


        var crore =
            Math.floor(
                number / 10000000
            );

        number =
            number % 10000000;


        var lakh =
            Math.floor(
                number / 100000
            );

        number =
            number % 100000;


        var thousand =
            Math.floor(
                number / 1000
            );

        number =
            number % 1000;


        var remaining =
            number;


        if (crore) {

            words.push(
                threeDigits(crore) +
                " Crore"
            );

        }


        if (lakh) {

            words.push(
                threeDigits(lakh) +
                " Lakh"
            );

        }


        if (thousand) {

            words.push(
                threeDigits(thousand) +
                " Thousand"
            );

        }


        if (remaining) {

            words.push(
                threeDigits(remaining)
            );

        }


        return (
            "Rupees " +
            words.join(" ") +
            " Only"
        );

    }


    // =========================================================
    // FIND ALL INVOICE ITEM ROWS
    // =========================================================

    function getInvoiceRows() {

        var rows =
            document.querySelectorAll(
                ".inline-group tr.form-row"
            );


        console.log(
            "Invoice item rows:",
            rows.length
        );


        return rows;

    }


    // =========================================================
    // AUTO NUMBER INVOICE ITEM SERIAL NUMBERS
    // =========================================================

    function updateSerialNumbers() {

        var rows = getInvoiceRows();
        var serial = 1;

        rows.forEach(function (row) {

            // Skip Django empty/template rows
            if (
                row.classList.contains("empty-form") ||
                row.querySelector('[name*="__prefix__"]')
            ) {
                return;
            }

            // Skip rows marked for deletion
            var deleteCheckbox = row.querySelector(
                'input[name$="-DELETE"]'
            );

            if (deleteCheckbox && deleteCheckbox.checked) {
                return;
            }

            var serialInput = row.querySelector(
                'input[name$="-serial_no"]'
            );

            if (serialInput) {
                serialInput.value = serial;
                serial += 1;
            }
        });
    }


    // =========================================================
    // UPDATE INLINE ROW CALCULATED CELL
    // =========================================================

    function setRowValue(
        row,
        fieldName,
        value
    ) {

        var cell =
            row.querySelector(
                ".field-" + fieldName
            );


        if (!cell) {

            console.warn(
                "Cannot find row field:",
                fieldName
            );

            return;

        }


        cell.textContent =
            Number(value).toFixed(2);

    }


    // =========================================================
    // UPDATE INVOICE TOTAL
    // =========================================================

    function setInvoiceTotal(
        fieldName,
        value
    ) {

        var wrapper =
            document.querySelector(
                ".field-" + fieldName
            );


        if (!wrapper) {

            console.warn(
                "Cannot find invoice total:",
                fieldName
            );

            return;

        }


        var formatted =
            Number(value).toFixed(2);


        // Django Admin readonly value

        var readonly =
            wrapper.querySelector(
                ".readonly"
            );


        if (readonly) {

            readonly.textContent =
                formatted;

            return;

        }


        // Fallback input

        var input =
            wrapper.querySelector(
                "input"
            );


        if (input) {

            input.value =
                formatted;

            return;

        }

    }


    // =========================================================
    // CALCULATE ONE ROW
    // =========================================================

    function calculateRow(row) {

        if (!row) {

            return {
                taxable: 0,
                tax: 0,
                total: 0
            };

        }


        // -----------------------------------------------------
        // Deleted row
        // -----------------------------------------------------

        var deleteCheckbox =
            row.querySelector(
                'input[name$="-DELETE"]'
            );


        if (
            deleteCheckbox &&
            deleteCheckbox.checked
        ) {

            return {
                taxable: 0,
                tax: 0,
                total: 0
            };

        }


        // -----------------------------------------------------
        // Quantity
        // -----------------------------------------------------

        var quantityInput =
            row.querySelector(
                'input[name$="-quantity"]'
            );


        // -----------------------------------------------------
        // Rate
        // -----------------------------------------------------

        var rateInput =
            row.querySelector(
                'input[name$="-rate"]'
            );


        // -----------------------------------------------------
        // Tax rate
        // -----------------------------------------------------

        var taxRateInput =
            row.querySelector(
                'input[name$="-tax_rate"]'
            );


        if (
            !quantityInput ||
            !rateInput
        ) {

            return {
                taxable: 0,
                tax: 0,
                total: 0
            };

        }


        var quantity =
            getNumber(
                quantityInput.value
            );


        var rate =
            getNumber(
                rateInput.value
            );


        var taxRate = 0;


        if (taxRateInput) {

            taxRate =
                getNumber(
                    taxRateInput.value
                );

        }


        // =====================================================
        // TAXABLE VALUE
        // =====================================================

        var taxable =
            money(
                quantity * rate
            );


        // =====================================================
        // TAX
        // =====================================================

        var tax =
            money(
                taxable * taxRate / 100
            );


        // =====================================================
        // LINE TOTAL
        // =====================================================

        var total =
            money(
                taxable + tax
            );


        console.log(
            "Row calculation:",
            {
                quantity: quantity,
                rate: rate,
                taxRate: taxRate,
                taxable: taxable,
                tax: tax,
                total: total
            }
        );


        // =====================================================
        // DISPLAY ROW VALUES
        // =====================================================

        setRowValue(
            row,
            "taxable_value",
            taxable
        );


        setRowValue(
            row,
            "tax_amount",
            tax
        );


        setRowValue(
            row,
            "line_total",
            total
        );


        return {
            taxable: taxable,
            tax: tax,
            total: total
        };

    }


    // =========================================================
    // CALCULATE COMPLETE INVOICE
    // =========================================================

    function calculateInvoice() {

        // Keep invoice item serial numbers sequential: 1, 2, 3, ...
        updateSerialNumbers();

        var taxableTotal = 0;

        var taxTotal = 0;

        var grandTotal = 0;


        var rows =
            getInvoiceRows();


        rows.forEach(
            function (row) {

                // Skip empty form

                if (
                    row.classList.contains(
                        "empty-form"
                    )
                ) {

                    return;

                }


                // Skip template row

                if (
                    row.querySelector(
                        '[name*="__prefix__"]'
                    )
                ) {

                    return;

                }


                var result =
                    calculateRow(row);


                taxableTotal +=
                    result.taxable;


                taxTotal +=
                    result.tax;


                grandTotal +=
                    result.total;

            }
        );


        // =====================================================
        // ROUND
        // =====================================================

        taxableTotal =
            money(
                taxableTotal
            );


        taxTotal =
            money(
                taxTotal
            );


        grandTotal =
            money(
                grandTotal
            );


        console.log(
            "Invoice totals:",
            {
                taxableTotal:
                    taxableTotal,

                taxTotal:
                    taxTotal,

                grandTotal:
                    grandTotal
            }
        );


        // =====================================================
        // DISPLAY TOTALS
        // =====================================================

        setInvoiceTotal(
            "taxable_total",
            taxableTotal
        );


        setInvoiceTotal(
            "tax_total",
            taxTotal
        );


        setInvoiceTotal(
            "grand_total",
            grandTotal
        );


        // =====================================================
        // AMOUNT IN WORDS
        // =====================================================

        var amountWords =
            document.getElementById(
                "id_amount_in_words"
            );


        if (amountWords) {

            amountWords.value =
                numberToWords(
                    grandTotal
                );

        }

    }


    // =========================================================
    // LIVE INPUT CALCULATION
    // =========================================================

    document.addEventListener(
        "input",
        function (event) {

            if (
                event.target.matches(
                    'input[name$="-quantity"]'
                ) ||

                event.target.matches(
                    'input[name$="-rate"]'
                ) ||

                event.target.matches(
                    'input[name$="-tax_rate"]'
                )
            ) {

                calculateInvoice();

            }

        }
    );


    // =========================================================
    // TAX TYPE / DELETE
    // =========================================================

    document.addEventListener(
        "change",
        function (event) {

            if (
                event.target.matches(
                    'select[name$="-tax_type"]'
                ) ||

                event.target.matches(
                    'input[name$="-DELETE"]'
                )
            ) {

                calculateInvoice();

            }

        }
    );


    // =========================================================
    // NEW INLINE ROW
    // =========================================================

    document.addEventListener(
        "formset:added",
        function () {

            setTimeout(
                calculateInvoice,
                100
            );

        }
    );


    // =========================================================
    // PAGE LOAD
    // =========================================================

    function initialize() {

        console.log(
            "Initializing Invoice Admin..."
        );


        // Customer auto-fill

        initializeCustomerAutoFill();


        // Invoice calculations

        calculateInvoice();

    }


    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            initialize
        );

    } else {

        initialize();

    }

})();