import hashlib
import hmac
import json
from datetime import datetime, timezone
from django.shortcuts import render, redirect

from django.conf import settings
from django.http import (
    HttpResponse,
    JsonResponse,
)
from django.views.decorators.csrf import csrf_exempt

from .models import WhatsAppWebhookEvent


def _verify_signature(request):
    """
    Verify Meta X-Hub-Signature-256 header.
    """

    app_secret = getattr(
        settings,
        "WHATSAPP_APP_SECRET",
        "",
    )

    if not app_secret:
        return False

    signature = request.headers.get(
        "X-Hub-Signature-256",
        "",
    )

    if not signature.startswith("sha256="):
        return False

    expected_signature = hmac.new(
        app_secret.encode("utf-8"),
        request.body,
        hashlib.sha256,
    ).hexdigest()

    received_signature = signature.split(
        "sha256=",
        1,
    )[1]

    return hmac.compare_digest(
        expected_signature,
        received_signature,
    )


def _timestamp_to_datetime(timestamp):
    """
    Convert WhatsApp Unix timestamp to Django datetime.
    """

    if not timestamp:
        return None

    try:
        return datetime.fromtimestamp(
            int(timestamp),
            tz=timezone.utc,
        )
    except (TypeError, ValueError):
        return None

def book_consultation_whatsapp(request):
    return redirect(
        "https://wa.me/918469260584"
    )


@csrf_exempt
def whatsapp_webhook(request):

    # =========================================================
    # META WEBHOOK VERIFICATION
    # =========================================================

    if request.method == "GET":

        verify_token = request.GET.get(
            "hub.verify_token",
            "",
        )

        challenge = request.GET.get(
            "hub.challenge",
            "",
        )

        configured_token = getattr(
            settings,
            "WHATSAPP_WEBHOOK_VERIFY_TOKEN",
            "",
        )

        if (
            verify_token
            and configured_token
            and hmac.compare_digest(
                verify_token,
                configured_token,
            )
        ):
            return HttpResponse(
                challenge,
                content_type="text/plain",
            )

        return HttpResponse(
            "Verification failed",
            status=403,
        )

    # =========================================================
    # ONLY POST ALLOWED
    # =========================================================

    if request.method != "POST":
        return JsonResponse(
            {
                "error": "Method not allowed"
            },
            status=405,
        )

    # =========================================================
    # VERIFY META SIGNATURE
    # =========================================================

    if not _verify_signature(request):
        return JsonResponse(
            {
                "error": "Invalid signature"
            },
            status=403,
        )

    # =========================================================
    # PARSE JSON
    # =========================================================

    try:
        payload = json.loads(
            request.body.decode("utf-8")
        )
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {
                "error": "Invalid JSON"
            },
            status=400,
        )

    # =========================================================
    # BASIC WEBHOOK STRUCTURE
    # =========================================================

    if payload.get("object") != "whatsapp_business_account":
        return JsonResponse(
            {
                "status": "ignored"
            },
            status=200,
        )

    waba_id = ""

    for entry in payload.get("entry", []):

        waba_id = str(
            entry.get("id", "")
        )

        for change in entry.get("changes", []):

            value = change.get(
                "value",
                {},
            )

            metadata = value.get(
                "metadata",
                {},
            )

            phone_number_id = str(
                metadata.get(
                    "phone_number_id",
                    "",
                )
            )

            # =================================================
            # INCOMING MESSAGES
            # =================================================

            contacts = value.get(
                "contacts",
                [],
            )

            contact_name = ""

            if contacts:
                contact_profile = contacts[0].get(
                    "profile",
                    {},
                )

                contact_name = contact_profile.get(
                    "name",
                    "",
                )

            for message in value.get(
                "messages",
                [],
            ):

                message_id = str(
                    message.get(
                        "id",
                        "",
                    )
                )

                sender_id = str(
                    message.get(
                        "from",
                        "",
                    )
                )

                message_type = message.get(
                    "type",
                    "",
                )

                message_text = ""

                # ---------------------------------------------
                # TEXT MESSAGE
                # ---------------------------------------------

                if message_type == "text":

                    message_text = (
                        message.get(
                            "text",
                            {},
                        ).get(
                            "body",
                            "",
                        )
                    )

                # ---------------------------------------------
                # BUTTON REPLY
                # ---------------------------------------------

                elif message_type == "button":

                    message_text = (
                        message.get(
                            "button",
                            {},
                        ).get(
                            "text",
                            "",
                        )
                    )

                # ---------------------------------------------
                # INTERACTIVE REPLY
                # ---------------------------------------------

                elif message_type == "interactive":

                    interactive = message.get(
                        "interactive",
                        {},
                    )

                    interactive_type = interactive.get(
                        "type",
                        "",
                    )

                    if interactive_type == "button_reply":

                        button_reply = interactive.get(
                            "button_reply",
                            {},
                        )

                        message_text = button_reply.get(
                            "title",
                            "",
                        )

                    elif interactive_type == "list_reply":

                        list_reply = interactive.get(
                            "list_reply",
                            {},
                        )

                        message_text = list_reply.get(
                            "title",
                            "",
                        )

                # ---------------------------------------------
                # STORE MESSAGE
                # ---------------------------------------------

                WhatsAppWebhookEvent.objects.update_or_create(
                    message_id=message_id,
                    defaults={
                        "waba_id": waba_id,
                        "phone_number_id": phone_number_id,
                        "event_type": "message",
                        "direction": "incoming",
                        "recipient_id": sender_id,
                        "sender_name": contact_name,
                        "message_type": message_type,
                        "message_text": message_text,
                        "status": "received",
                        "event_timestamp": _timestamp_to_datetime(
                            message.get(
                                "timestamp"
                            )
                        ),
                        "raw_payload": message,
                    },
                )

            # =================================================
            # MESSAGE STATUS UPDATES
            # =================================================

            for status_event in value.get(
                "statuses",
                [],
            ):

                status_message_id = str(
                    status_event.get(
                        "id",
                        "",
                    )
                )

                recipient_id = str(
                    status_event.get(
                        "recipient_id",
                        "",
                    )
                )

                status_value = status_event.get(
                    "status",
                    "",
                )

                errors = status_event.get(
                    "errors",
                    [],
                )

                error_code = ""
                error_message = ""

                if errors:

                    first_error = errors[0]

                    error_code = str(
                        first_error.get(
                            "code",
                            "",
                        )
                    )

                    error_message = (
                        first_error.get(
                            "title",
                            ""
                        )
                        or first_error.get(
                            "message",
                            ""
                        )
                    )

                WhatsAppWebhookEvent.objects.update_or_create(
                    message_id=status_message_id,
                    defaults={
                        "waba_id": waba_id,
                        "phone_number_id": phone_number_id,
                        "event_type": "status",
                        "direction": "status",
                        "recipient_id": recipient_id,
                        "status": status_value,
                        "error_code": error_code,
                        "error_message": error_message,
                        "event_timestamp": _timestamp_to_datetime(
                            status_event.get(
                                "timestamp"
                            )
                        ),
                        "raw_payload": status_event,
                    },
                )

    # =========================================================
    # ALWAYS RETURN 200 TO META
    # =========================================================

    return JsonResponse(
        {
            "status": "received"
        },
        status=200,
    )

