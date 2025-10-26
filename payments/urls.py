from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_order, name='create_order'),
    path('checkout/', views.payment_checkout, name='payment_checkout'),
    path('verify/', views.verify_payment, name='verify_payment'),
    path('webhook/', views.cashfree_webhook, name='cashfree_webhook'),
]

# urlpatterns = [
#     path('users/', views.users, name='users'),
# ]