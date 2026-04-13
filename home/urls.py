from django.urls import path
from . import views
from home.views import robots_txt

urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('about', views.about, name='about'),
    path('contact', views.contact, name='contact'),
    path('contact-us', views.contact_us, name='contact_us'),
    path('thyroid', views.thyroid, name='thyroid'),
    path('gastrointestinal', views.gastrointestinal, name='gastrointestinal'),
    path('lungs', views.lungs, name='lungs'),
    path('hematological', views.hematological, name='hematological'),
    path('stone', views.stone, name='stone'),
    path('tumor', views.tumor, name='tumor'),
    path('arthritis', views.arthritis, name='arthritis'),
    path('skin', views.skin, name='skin'),
    path('female-genital-organ', views.female_genital_organ, name='female-genital-organ'),
    path('vamana', views.vamana, name='vamana'),
    path('virechana', views.virechana, name='virechana'),
    path('basti', views.basti, name='basti'),  
    path('nasya', views.nasya, name='nasya'),
    path('raktamokshana', views.raktamokshana, name='raktamokshana'),
    path('dr-sushma-tiwary', views.dr_sushma_tiwary, name='dr_sushma_tiwary'),
    path('contact_us_email', views.contact_us_email, name='contact_us_email'),
    path('udarshodhak', views.udarshodhak, name='udarshodhak'),
    path('shirodhara', views.shirodhara, name='shirodhara'),
    path('abhyanga', views.abhyanga, name='abhyanga'),
    path("robots.txt", robots_txt, name="robots_txt"), 
]