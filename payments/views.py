import json
import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
from users.models import User
import os
import shutil
import pdb
from .models import Order


def create_order(request):
    """
    Step 1: Create a new Cashfree order and get a payment session.
    """
    if request.method == "GET":
        user_id = request.GET.get("user_id") 
        order_quantity = int(request.GET.get("quantity"))
        user = User.objects.get(id=f"{user_id}")
        amount = 300 * int(order_quantity); # request.GET.get("amount")
        customer_id = "CUST_" + get_random_string(6)
        order_id = "ORDER_" + get_random_string(8)

        url = f"{settings.CASHFREE['base_url']}/orders"
        headers = {
            "x-client-id": settings.CASHFREE['client_id'],
            "x-client-secret": settings.CASHFREE['client_secret'],
            "x-api-version": "2022-09-01",
            "Content-Type": "application/json"
        }

        payload = {
            "order_id": order_id,
            "order_amount": float(amount),
            "order_currency": "INR",
            "order_quantity": order_quantity,
            "customer_details": {
                "customer_id": customer_id,
                "customer_email": user.email,
                "customer_phone": user.phone,
                #"customer_uid": f"{user_id}",
                "customer_name": user.fname + ' ' + user.lname
                },
            "order_note": "Udarshodhak Payment",
            "order_meta": {
                "return_url": request.build_absolute_uri(f"/payments/verify/?order_id={order_id}")
            }
        }

        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

                
        customer_details = payload["customer_details"]      
        order_id = order_id    
        order_amount = float(amount)
        order_quantity = order_quantity 
        order_currency = "INR"
        order_address = user.address
        order_note = payload["order_note"]  
        order_meta = payload["order_meta"] 
        order_response = data

        order = Order.objects.create(
            user_id=user_id, 
            customer_details=customer_details, 
            order_id=order_id, 
            order_amount=order_amount, 
            order_quantity=order_quantity,
            order_currency=order_currency,
            order_address=order_address,
            order_note=order_note,
            order_meta=order_meta,
            order_response=order_response
        )
        order.save()

        if response.status_code == 200 and "payment_session_id" in data:
            # Render checkout page with session id

            return render(request, "payment_checkout.html", {
                "payment_session_id": data["payment_session_id"],
                "order_id": order_id
            })
        else:
            return JsonResponse({"error": data}, status=400)

    return render(request, "create_order.html")


def payment_checkout(request):
    """
    Optional route if you want to handle direct redirection from JS.
    """
    return render(request, "payment_checkout.html")


def verify_payment(request):
    """
    Step 2: Verify payment after returning from Cashfree.
    """
    order_id = request.GET.get("order_id")

    url = f"{settings.CASHFREE['base_url']}/orders/{order_id}"
    headers = {
        "x-client-id": settings.CASHFREE['client_id'],
        "x-client-secret": settings.CASHFREE['client_secret'],
        "x-api-version": "2022-09-01",
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    status = data.get("order_status", "UNKNOWN")
    order = Order.objects.get(order_id=f"{order_id}")
    order.order_status = status
    order.save()

    if status == "PAID":
        message = "✅ Payment successful! Thank you for your order."
    elif status == "FAILED":
        message = "❌ Payment failed. Please try again."
    else:
        message = f"Payment status: {status}"

    return render(request, "payment_status.html", {"message": message, "data": data, "order":order})


@csrf_exempt
def cashfree_webhook(request):
    """
    Step 3: Handle Cashfree webhook (server-to-server notification).
    """
    try:
        payload = json.loads(request.body.decode('utf-8'))
        order_status = payload.get('orderStatus')

        # TODO: Update your order in DB here
        print("Webhook received:", payload)

        return JsonResponse({"status": "ok"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
