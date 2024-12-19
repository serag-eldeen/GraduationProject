from django.shortcuts import render, redirect
from .models import Signup
from django.contrib import messages
import re
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse


# Index page
def index(request):
    return render(request, 'pages/index.html')

# Login page
def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = Signup.objects.get(email=email)
            if check_password(password, user.password):
                # Store user info in session
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                request.session['user_role'] = user.role  # Store the user's role

                # Redirect to the appropriate home page based on the user's role
                if user.role == 'pro':
                    return redirect('proapp:home')  # Redirect to Pro app home page
                elif user.role == 'premium':
                    return redirect('premiumapp:home')  # Redirect to Premium app home page
                else:
                    return redirect('mainapp:home')  # Redirect to Free app home page (default)
            else:
                return render(request, 'pages/login.html', {"error": "Invalid email or password"})
        except Signup.DoesNotExist:
            return render(request, 'pages/login.html', {"error": "Invalid email or password"})

    return render(request, 'pages/login.html')

# Signup page
def signup(request):
    if request.method == "POST":
        email = request.POST.get("email")
        name = request.POST.get("name")
        password = request.POST.get("password")
        agreed_to_terms = request.POST.get("agreed_to_terms") == "on"

        if not agreed_to_terms:
            return render(request, 'pages/signup.html', {"error": "You must agree to the terms and conditions."})

        if Signup.objects.filter(email=email).exists():
            return render(request, 'pages/signup.html', {"error": "Email already exists."})

        password_error = validate_password_strength(password)
        if password_error:
            return render(request, 'pages/signup.html', {"error": password_error})

        # Hash the password before saving
        hashed_password = make_password(password)

        # Create a new user with a default role as 'free'
        Signup.objects.create(email=email, name=name, password=hashed_password, agreed_to_terms=agreed_to_terms, role='free')
        return redirect('pages:login')  # Redirect to login after successful signup

    return render(request, 'pages/signup.html')

# Validate password strength
def validate_password_strength(password):
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r"\d", password):
        return "Password must contain at least one digit."
    if not re.search(r"[A-Za-z]", password):
        return "Password must contain at least one letter."
    if not re.search(r"[@$!%*?&]", password):
        return "Password must contain at least one special character (@, $, !, %, *, ?, &)."
    return None  # None means the password is strong

# Privacy policy page
def privacypolicy(request):
    return render(request, 'pages/privacypolicy.html')

# Terms and conditions page
def termsconditions(request):
    return render(request, 'pages/termsconditions.html')

# Article details page
def articledetails(request):
    return render(request, 'pages/articledetails.html')
