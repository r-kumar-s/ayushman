from django.urls import path
from . import views


urlpatterns = [

    path(
        "<slug:topic>/<slug:slug>/",
        views.blog_article,
        name="blog_article",
    ),

]