from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index.html', views.index, name='index'),
    path('about.html', views.about, name='about'),
    path('contact.html', views.contact, name='contact'),
    path('contact-us', views.contact_us, name='contact_us'),
    path('thyroid.html', views.thyroid, name='thyroid'),
    path('gastrointestinal.html', views.gastrointestinal, name='gastrointestinal'),
    path('lungs.html', views.lungs, name='lungs'),
    path('hematological.html', views.hematological, name='hematological'),
    path('stone.html', views.stone, name='stone'),
    path('tumor.html', views.tumor, name='tumor'),
    path('arthritis.html', views.arthritis, name='arthritis'),
    path('skin.html', views.skin, name='skin'),
    path('female-genital-organ.html', views.female_genital_organ, name='female-genital-organ'),
    path('vamana.html', views.vamana, name='vamana'),
    path('virechana.html', views.virechana, name='virechana'),
    path('basti.html', views.basti, name='basti'),  
    path('nasya.html', views.nasya, name='nasya'),
    path('raktamokshana.html', views.raktamokshana, name='raktamokshana')   
    
]