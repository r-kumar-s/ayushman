from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.conf import settings
#from django.contrib.auth import get_user_model
from .models import User
from payments.views import create_order

#User = get_user_model()

def users(request):
  template = loader.get_template('home.html')
  return HttpResponse(template.render())

def create_users(request):

    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        quantity = request.POST.get('quantity')

        # if User.objects.filter(username=username).exists():
        #     messages.error(request, 'Username already exists.')
        #     return redirect('register')
        
        user = User.objects.create(fname=fname, lname=lname, email=email, phone=phone,address=address)
        user.save()

        messages.success(request, 'Account created successfully! Please login.')        
        #return request.build_absolute_uri(f"/payments/create_order/?user_id={user.id}")
        return redirect(f'/payments/create?user_id={user.id}&quantity={quantity}')

    return render(request, 'USER/register.html')
    

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password, phone=phone)
        messages.success(request, 'Account created successfully! Please login.')
        return redirect('login')
    return render(request, 'USER/register.html')
