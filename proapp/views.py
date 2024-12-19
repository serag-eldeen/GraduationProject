from django.shortcuts import render

def home(request):
    return render(request, 'proapp/home.html')  # Template for Pro App Home
