from django.shortcuts import render

def home(request):
    return render(request, 'premiumapp/home.html')  # Template for Premium App Home
