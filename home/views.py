from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMessage
import pdb;
import datetime;
# pdb.set_trace()   



from .forms import ContactUsForm

#from .models import Home

def index(request):
    context ={}
    context['form']= ContactUsForm()
    today = datetime.date.today()
    year = today.strftime("%Y")
    return render(request, "index.html", context)

  # template = loader.get_template('index.html')
  # return HttpResponse(template.render())

def about(request):
  template = loader.get_template('about.html')
  return HttpResponse(template.render())

def contact(request):
  template = loader.get_template('contact.html')
  return HttpResponse(template.render())

def contact_us(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = ContactUsForm(request.POST)
        # check whether it's valid:     
        if form.is_valid(): 
            
            subject = "Ayushman Bhavah Website Inquiry" 
            body = {
              'first_name': form.cleaned_data['fname'], 
              'last_name': form.cleaned_data['lname'], 
              'email': form.cleaned_data['sender'], 
              'message':form.cleaned_data['message'], 
            }
            message = "\n".join(body.values())

        try:
          send_mail(subject, message, form.cleaned_data['sender'], ['stsush29@gmail.com','contact@ayushmaanbhavah.com',]) 
          #email = EmailMessage(subject, message, to=['rshaw@aecordigital.com'])
          #email.send()
        except BadHeaderError:
          #return HttpResponseRedirect("/thanks/")
          return HttpResponse('Invalid header found.')
          return redirect ("home:index")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ContactUsForm()

    return render(request, "index.html", {"form": form})

def thyroid(request):
  template = loader.get_template('treatments/thyroid.html')
  return HttpResponse(template.render())

def gastrointestinal(request):
  template = loader.get_template('treatments/gastrointestinal.html')
  return HttpResponse(template.render())

def lungs(request):
  template = loader.get_template('treatments/lungs.html')
  return HttpResponse(template.render())

def hematological(request):
  template = loader.get_template('treatments/hematological.html')
  return HttpResponse(template.render())

def stone(request):
  template = loader.get_template('treatments/stone.html')
  return HttpResponse(template.render())

def tumor(request):
  template = loader.get_template('treatments/tumor.html')
  return HttpResponse(template.render())
  
def arthritis(request):
  template = loader.get_template('treatments/arthritis.html')
  return HttpResponse(template.render())

def skin(request):
  template = loader.get_template('treatments/skin.html')
  return HttpResponse(template.render())

def male_genital_organ(request):
  template = loader.get_template('treatments/male-genital-organ.html')
  return HttpResponse(template.render())

def female_genital_organ(request):
  template = loader.get_template('treatments/female-genital-organ.html')
  return HttpResponse(template.render())

def vamana(request):
  template = loader.get_template('panchkarma/vamana.html')
  return HttpResponse(template.render())

def virechana(request):
  template = loader.get_template('panchkarma/virechana.html')
  return HttpResponse(template.render())

def basti(request):
  template = loader.get_template('panchkarma/basti.html')
  return HttpResponse(template.render())

def nasya(request):
  template = loader.get_template('panchkarma/nasya.html')
  return HttpResponse(template.render())

def raktamokshana(request):
  template = loader.get_template('panchkarma/raktamokshana.html')
  return HttpResponse(template.render())

  

            