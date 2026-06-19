from django.contrib import admin
from .models import (
    Visitor,
    CampaignVisit,
    PageView,
    Conversion
)


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'session_key',
        'ip_address',
        'first_visit',
        'last_visit'
    )
    search_fields = ('session_key', 'ip_address')


@admin.register(CampaignVisit)
class CampaignVisitAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'visitor',
        'utm_source',
        'utm_medium',
        'utm_campaign',
        'created_at'
    )

    list_filter = (
        'utm_source',
        'utm_medium',
        'utm_campaign'
    )

    search_fields = (
        'utm_source',
        'utm_campaign'
    )


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'visitor',
        'url',
        'created_at'
    )

    search_fields = ('url',)


@admin.register(Conversion)
class ConversionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'visitor',
        'conversion_type',
        'value',
        'created_at'
    )

    list_filter = ('conversion_type',)