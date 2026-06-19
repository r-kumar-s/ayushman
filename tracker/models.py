from django.db import models


class Visitor(models.Model):

    session_key = models.CharField(
        max_length=100,
        unique=True
    )

    ip_address = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    user_agent = models.TextField(
        blank=True,
        null=True
    )

    first_visit = models.DateTimeField(
        auto_now_add=True
    )

    last_visit = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.session_key


class CampaignVisit(models.Model):

    visitor = models.ForeignKey(
        Visitor,
        on_delete=models.CASCADE,
        related_name='campaigns'
    )

    utm_source = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    utm_medium = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    utm_campaign = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    utm_content = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    utm_term = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    landing_page = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.utm_source} - {self.utm_campaign}"


class PageView(models.Model):

    visitor = models.ForeignKey(
        Visitor,
        on_delete=models.CASCADE,
        related_name='pageviews'
    )

    url = models.TextField()

    referrer = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.url


class Conversion(models.Model):

    CONVERSION_TYPES = [
        ('contact_form', 'Contact Form'),
        ('appointment', 'Appointment'),
        ('phone_call', 'Phone Call'),
        ('whatsapp', 'WhatsApp'),
        ('purchase', 'Purchase'),
    ]

    visitor = models.ForeignKey(
        Visitor,
        on_delete=models.CASCADE
    )

    conversion_type = models.CharField(
        max_length=50,
        choices=CONVERSION_TYPES
    )

    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    notes = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.conversion_type