from django.shortcuts import render

# Create your views here.

def why_ayushmaan_bhavah(request):
    return render(request, "why-ayushmaan-bhavah/index.html")