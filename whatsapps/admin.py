from django.contrib import admin
from django.utils.html import format_html

from .models import WhatsAppWebhookEvent


@admin.register(WhatsAppWebhookEvent)
class WhatsAppWebhookEventAdmin(admin.ModelAdmin):

    list_display = (
        "created_at",
        "direction_badge",
        "recipient_id",
        "sender_name",
        "message_type",
        "message_preview",
        "status",
    )

    list_filter = (
        "direction",
        "event_type",
        "message_type",
        "status",
        "created_at",
    )

    search_fields = (
        "recipient_id",
        "sender_name",
        "message_text",
        "message_id",
        "status",
        "error_message",
    )

    readonly_fields = (
        "waba_id",
        "phone_number_id",
        "event_type",
        "direction",
        "message_id",
        "recipient_id",
        "sender_name",
        "message_type",
        "message_text",
        "status",
        "error_code",
        "error_message",
        "event_timestamp",
        "raw_payload",
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 50

    fieldsets = (
        (
            "Message",
            {
                "fields": (
                    "direction",
                    "event_type",
                    "recipient_id",
                    "sender_name",
                    "message_type",
                    "message_text",
                    "status",
                )
            },
        ),
        (
            "WhatsApp",
            {
                "fields": (
                    "waba_id",
                    "phone_number_id",
                    "message_id",
                    "event_timestamp",
                )
            },
        ),
        (
            "Errors",
            {
                "fields": (
                    "error_code",
                    "error_message",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
        (
            "Raw Payload",
            {
                "fields": (
                    "raw_payload",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
        (
            "System",
            {
                "fields": (
                    "created_at",
                )
            },
        ),
    )

    @admin.display(
        description="Direction"
    )
    def direction_badge(self, obj):

        if obj.direction == "incoming":

            return format_html(
                '<strong style="color:#198754;">INCOMING</strong>'
            )

        if obj.direction == "status":

            return format_html(
                '<strong style="color:#6c757d;">STATUS</strong>'
            )

        return obj.direction

    @admin.display(
        description="Message"
    )
    def message_preview(self, obj):

        if not obj.message_text:
            return "-"

        text = obj.message_text.replace(
            "\n",
            " ",
        )

        if len(text) > 80:
            text = text[:80] + "..."

        return text