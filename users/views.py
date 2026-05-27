from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import User, PatientFollowup

from .forms import (
    UserForm,
    PatientFollowupForm,
    PatientFollowupFormSet
)


def users(request):
    users = User.objects.all()

    return render(request, 'list.html', {
        'users': users
    })


def create_users(request):

    if request.method == 'POST':

        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        dob = request.POST.get('dob')
        referred_by = request.POST.get('referred_by')
        quantity = request.POST.get('quantity')

        # Check existing email
        if email and User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('create_users')

        user = User.objects.create(
            fname=fname,
            lname=lname,
            email=email,
            phone=phone,
            address=address,
            dob=dob if dob else None,
            referred_by=referred_by
        )

        messages.success(request, 'User created successfully!')

        return redirect(f'/payments/create?user_id={user.id}&quantity={quantity}')

    return render(request, 'create.html')


def detail(request, id):

    user = get_object_or_404(User, id=id)

    return render(request, 'detail.html', {
        'user': user
    })


def edit(request, id):

    user = get_object_or_404(User, id=id)

    if request.method == 'POST':

        form = UserForm(
            request.POST,
            instance=user
        )

        formset = PatientFollowupFormSet(
            request.POST,
            request.FILES,
            instance=user
        )

        # Validate BOTH independently so we get errors from each
        form_valid    = form.is_valid()
        formset_valid = formset.is_valid()

        if form_valid and formset_valid:

            form.save()

            formset.save()

            messages.success(
                request,
                'Updated successfully!'
            )

            return redirect('users')

    else:

        form = UserForm(instance=user)

        formset = PatientFollowupFormSet(instance=user)

    return render(request, 'edit.html', {
        'form': form,
        'formset': formset,
        'user': user
    })


def update(request, id):

    user = get_object_or_404(User, id=id)

    if request.method == 'POST':

        user.fname = request.POST.get('fname')
        user.lname = request.POST.get('lname')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        user.address = request.POST.get('address')

        dob = request.POST.get('dob')

        user.dob = dob if dob else None

        user.referred_by = request.POST.get('referred_by')

        user.save()

        messages.success(request, 'User updated successfully!')

        return redirect('users')

    return render(request, 'edit.html', {
        'user': user
    })


def delete(request, id):

    user = get_object_or_404(User, id=id)

    if request.method == 'POST':
        user.delete()

        messages.success(request, 'User deleted successfully!')

        return redirect('users')

    return render(request, 'delete.html', {
        'user': user
    })


def create_with_followup(request):

    if request.method == 'POST':

        user_form = UserForm(request.POST)

        followup_form = PatientFollowupForm(
            request.POST,
            request.FILES
        )

        if user_form.is_valid() and followup_form.is_valid():

            user = user_form.save()

            followup = followup_form.save(commit=False)

            followup.user = user

            followup.save()

            messages.success(
                request,
                'User and followup created successfully!'
            )

            return redirect('users')

    else:

        user_form = UserForm()

        followup_form = PatientFollowupForm()

    return render(request, 'create_with_followup.html', {
        'user_form': user_form,
        'followup_form': followup_form
    })