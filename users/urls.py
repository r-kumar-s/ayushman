from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.users, name='users'),
    path('create_users', views.create_users, name='create_users'),
    ]