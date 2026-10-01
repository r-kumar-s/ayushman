import requests
from django.conf import settings


def _get_whatsapp_config():
    """
    Get WhatsApp Cloud API configuration from Django settings.
    """

    access_token = getattr(
        settings,
        "WHATSAPP_ACCESS_TOKEN",
        ""
    )

    phone_number_id = getattr(
        settings,
        "WHATSAPP_PHONE_NUMBER_ID",
        ""
    )

    api_version = getattr(
        settings,
        "WHATSAPP_API_VERSION",
        "v26.0"
    )

    if not access_token:
        raise RuntimeError(
            "WHATSAPP_ACCESS_TOKEN is not configured."
        )

    if not phone_number_id:
        raise RuntimeError(
            "WHATSAPP_PHONE_NUMBER_ID is not configured."
        )

    return access_token, phone_number_id, api_version


def _normalize_phone_number(phone_number):
    """
    Normalize Indian mobile numbers.
    """

    phone_number = str(phone_number).strip()

    if phone_number.startswith("+"):
        phone_number = phone_number[1:]

    if phone_number.startswith("0") and len(phone_number) == 11:
        phone_number = "91" + phone_number[1:]

    elif len(phone_number) == 10:
        phone_number = "91" + phone_number

    return phone_number


def _whatsapp_post(payload):
    """
    Send a POST request to WhatsApp Cloud API.
    """

    access_token, phone_number_id, api_version = (
        _get_whatsapp_config()
    )

    url = (
        f"https://graph.facebook.com/"
        f"{api_version}/"
        f"{phone_number_id}/messages"
    )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=30,
    )

    if not response.ok:
        raise RuntimeError(
            f"WhatsApp API error "
            f"{response.status_code}: "
            f"{response.text}"
        )

    return response.json()


def send_whatsapp_text(phone_number, message):
    """
    Send a normal WhatsApp text message.
    """

    phone_number = _normalize_phone_number(phone_number)

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": str(message),
        },
    }

    return _whatsapp_post(payload)

def send_doctor_consultation_closed_message(phone_number):
    message = """Namaste 🙏,

    Please note that Doctor Consultation services will be unavailable from October 8 to October 24, 2026.

    Please schedule your follow-up consultation before October 8 or after October 24.

    Schedule your appointment https://wa.me/8469260584

    Thank you,
    Ayushman Bhavah"""

    return send_whatsapp_text(
        phone_number,
        message,
    )

def send_doctor_consultation_notice(phone_number):
    message = """Namaste 🙏,

    Please note that Doctor Consultation services will be unavailable from October 8 to October 24, 2026.

    Please schedule your follow-up consultation before October 8 or after October 24.

    For consultation booking, please click here:
    https://wa.me/918469260584?text=Hello%2C%20I%20would%20like%20to%20schedule%20my%20Doctor%20Consultation.

    Thank you,
    Ayushman Bhavah"""

    return send_whatsapp_text(
        phone_number,
        message,
    )

def send_doctor_consultation_template(phone_number):
    return send_whatsapp_template(
        phone_number=phone_number,
        template_name="utility_doctor_consultation_closed_oct_2026",
        language_code="en",
    )


def send_whatsapp_template(
    phone_number,
    template_name,
    language_code="en_US",
):
    """
    Send an approved WhatsApp template.

    Example:

        send_whatsapp_template(
            "9599719664",
            "doctor_consultation_closed_oct_2026",
            "en_US",
        )
    """

    phone_number = _normalize_phone_number(phone_number)

    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {
                "code": language_code,
            },
        },
    }

    return _whatsapp_post(payload)