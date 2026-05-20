from django.urls import path
from . import views

urlpatterns = [

    path('', views.users, name='users'),

    path('create_users/', views.create_users, name='create_users'),

    path('detail/<int:id>/', views.detail, name='detail'),

    path('edit/<int:id>/', views.edit, name='edit'),

    path('update/<int:id>/', views.update, name='update'),

    path('delete/<int:id>/', views.delete, name='delete'),

    path('create_with_followup/', views.create_with_followup, name='create_with_followup'),

]