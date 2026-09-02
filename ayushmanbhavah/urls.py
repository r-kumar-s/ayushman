"""ayushmanbhavah URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from django.contrib.sitemaps.views import sitemap
from home.sitemaps import StaticViewSitemap
from django.conf import settings
from django.conf.urls.static import static

sitemaps = {
    'static': StaticViewSitemap(),
}

urlpatterns = [

    # ============================================================
    # 301 REDIRECTS FROM OLD WEBSITE URLs
    # ============================================================

    path(
        'index.php',
        RedirectView.as_view(url='/', permanent=True)
    ),

    path(
        'index.html',
        RedirectView.as_view(url='/', permanent=True)
    ),

    path(
        'about.html',
        RedirectView.as_view(url='/about/', permanent=True)
    ),

    path(
        'thyroid.html',
        RedirectView.as_view(url='/thyroid/', permanent=True)
    ),

    path(
        'gastrointestinal.html',
        RedirectView.as_view(url='/gastrointestinal/', permanent=True)
    ),

    path(
        'lungs.html',
        RedirectView.as_view(url='/lungs/', permanent=True)
    ),

    path(
        'hematological.html',
        RedirectView.as_view(url='/hematological/', permanent=True)
    ),

    path(
        'stone.html',
        RedirectView.as_view(url='/stone/', permanent=True)
    ),

    path(
        'tumor.html',
        RedirectView.as_view(url='/tumor/', permanent=True)
    ),

    path(
        'arthritis.html',
        RedirectView.as_view(url='/arthritis/', permanent=True)
    ),

    path(
        'skin.html',
        RedirectView.as_view(url='/skin/', permanent=True)
    ),

    path(
        'udarshodhak.html',
        RedirectView.as_view(url='/udarshodhak/', permanent=True)
    ),

    path(
        'contact.html',
        RedirectView.as_view(url='/contact/', permanent=True)
    ),

    path(
        'dr-sushma-tiwary.html',
        RedirectView.as_view(url='/dr-sushma-tiwary/', permanent=True)
    ),

    # ============================================================
    # CURRENT WEBSITE URLS
    # ============================================================

    path('', include('home.urls')),
    path('users/', include('users.urls')),
    path('payments/', include('payments.urls')),
    path('admin/', admin.site.urls),

    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': sitemaps},
        name='sitemap'
    ),

    path("", include("campaigns.urls")),
    path('captcha/', include('captcha.urls')),
    path("blog/",include("blog.urls", namespace="blog"),),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )