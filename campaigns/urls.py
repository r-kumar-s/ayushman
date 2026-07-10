print("***** campaigns.urls loaded *****")


from django.urls import path
from . import views

urlpatterns = [
    path(
        "why-ayushmaan-bhavah/",
        views.why_ayushmaan_bhavah,
        name="why_ayushmaan_bhavah",
    ),
]