from django.db import models


class WhatsAppWebhookEvent(models.Model):

    EVENT_TYPE_CHOICES = (
        ("message", "Incoming Message"),
        ("status", "Message Status"),
        ("other", "Other"),
    )

    DIRECTION_CHOICES = (
        ("incoming", "Incoming"),
        ("status", "Status"),
        ("other", "Other"),
    )

    waba_id = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    phone_number_id = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    event_type = models.CharField(
        max_length=30,
        choices=EVENT_TYPE_CHOICES,
        default="other",
    )

    direction = models.CharField(
        max_length=20,
        choices=DIRECTION_CHOICES,
        default="other",
    )

    message_id = models.CharField(
        max_length=255,
        blank=True,
        default="",
        db_index=True,
    )

    recipient_id = models.CharField(
        max_length=50,
        blank=True,
        default="",
        db_index=True,
    )

    sender_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    message_type = models.CharField(
        max_length=50,
        blank=True,
        default="",
    )

    message_text = models.TextField(
        blank=True,
        default="",
    )

    status = models.CharField(
        max_length=50,
        blank=True,
        default="",
    )

    error_code = models.CharField(
        max_length=50,
        blank=True,
        default="",
    )

    error_message = models.TextField(
        blank=True,
        default="",
    )

    event_timestamp = models.DateTimeField(
        null=True,
        blank=True,
    )

    raw_payload = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "WhatsApp Webhook Event"
        verbose_name_plural = "WhatsApp Webhook Events"

    def __str__(self):
        if self.message_text:
            return f"{self.recipient_id} - {self.message_text[:60]}"

        if self.status:
            return f"{self.recipient_id} - {self.status}"

        return f"WhatsApp Event #{self.pk}"