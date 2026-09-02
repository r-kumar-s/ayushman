from django.urls import path

from . import views


app_name = "blog"


urlpatterns = [

    path(
        "ayurvedic-approach-pcod-pcos/",
        views.ayurvedic_approach_pcod_pcos,
        name="ayurvedic_approach_pcod_pcos",
    ),

    path(
        "pcod-irregular-periods/",
        views.pcod_irregular_periods,
        name="pcod_irregular_periods",
    ),

    path(
        "pcod-weight-management/",
        views.pcod_weight_management,
        name="pcod_weight_management",
    ),

    path(
        "pcod-fertility/",
        views.pcod_fertility,
        name="pcod_fertility",
    ),

    path(
        "panchakarma-for-pcod/",
        views.panchakarma_for_pcod,
        name="panchakarma_for_pcod",
    ),

]