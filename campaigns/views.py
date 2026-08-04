from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from .models import Consultation
from django.core.mail import EmailMultiAlternatives


# Create your views here.

def why_ayushmaan_bhavah(request):
    return render(request, "why-ayushmaan-bhavah/index.html")

def consultation_submit(request):
    if request.method == "POST":

        Consultation.objects.create(
            name=request.POST.get("name"),
            phone=request.POST.get("phone"),
            age=request.POST.get("age") or None,
            condition=request.POST.get("condition"),
            message=request.POST.get("message")
        )

        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        age = request.POST.get("age", "").strip()
        condition = request.POST.get("condition", "").strip()
        message = request.POST.get("message", "").strip()

        if not name or not phone or not condition:
            return JsonResponse({
                "success": False,
                "message": "Please fill all required fields."
            })

        subject = f"🩺 New Consultation Request - {name}"

        html_message = f"""
        <html>
        <body style="font-family:Arial,sans-serif;">
            <h2 style="color:#1d7c5b;">New Consultation Request</h2>

            <table cellpadding="8" cellspacing="0" border="1" style="border-collapse:collapse;">
                <tr>
                    <th align="left">Name</th>
                    <td>{name}</td>
                </tr>
                <tr>
                    <th align="left">Phone</th>
                    <td>{phone}</td>
                </tr>
                <tr>
                    <th align="left">Age</th>
                    <td>{age or 'Not Provided'}</td>
                </tr>
                <tr>
                    <th align="left">Health Concern</th>
                    <td>{condition}</td>
                </tr>
                <tr>
                    <th align="left">Description</th>
                    <td>{message or 'No description provided.'}</td>
                </tr>
            </table>

            <br>

            <p>
                <strong>Submitted From:</strong><br>
                Ayushman Bhavah Website
            </p>

        </body>
        </html>
        """

        email = EmailMultiAlternatives(
            subject=subject,
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[
                "contact@ayushmaanbhavah.com",
            ]
        )

        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)



        return JsonResponse({"success": True})

    return JsonResponse({"success": False})