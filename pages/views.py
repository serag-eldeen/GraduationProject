from django.shortcuts import render, redirect
from .models import Signup
from django.contrib import messages
import re
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse
from datetime import datetime
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.utils.datastructures import MultiValueDictKeyError


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
            if not user.is_verified:  # Check if the account is verified
                return render(request, 'pages/login.html', {"error": "Your account is not verified. Please check your email to verify your account."})

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


def generate_verification_token():
    return get_random_string(length=32)

# Send verification email
def send_verification_email(user):
    token = generate_verification_token()
    verification_url = f"{settings.SITE_URL}/verify/{token}/"
    subject = "Please verify your email address"
    message = f"Click the link below to verify your email:\n{verification_url}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
    
    # Save the token and expiration time in the database
    user.verification_token = token
    user.token_expiry = timezone.now() + timedelta(hours=1)  # Token expires in 1 hour
    user.save()

# Signup view
def signup(request):
    if request.method == "POST":
        email = request.POST.get("email")
        name = request.POST.get("name")
        password = request.POST.get("password")
        phone_number = request.POST.get("phone_number")
        date_of_birth = request.POST.get("date_of_birth")
        country = request.POST.get("country")
        gender = request.POST.get("gender")
        agreed_to_terms = request.POST.get("agreed_to_terms") == "on"
        role = request.POST.get("role", "free")  # Default role is 'free'
        profile_picture = request.FILES.get('profile_picture')  # Get the uploaded image
        
        print(f"Profile Picture: {profile_picture}")  # Check if file is received


        # Form validation checks
        if not agreed_to_terms:
            return render(request, 'pages/signup.html', {"error": "You must agree to the terms and conditions."})

        if Signup.objects.filter(email=email).exists():
            return render(request, 'pages/signup.html', {"error": "Email already exists."})

        if not phone_number:
            return render(request, 'pages/signup.html', {"error": "Phone number is required."})

        password_error = validate_password_strength(password)
        if password_error:
            return render(request, 'pages/signup.html', {"error": password_error})

        # Validate date of birth
        try:
            dob = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
        except ValueError:
            return render(request, 'pages/signup.html', {"error": "Invalid date format. Use YYYY-MM-DD."})

        # Hash the password before saving
        hashed_password = make_password(password)

        # Create the new user
        user = Signup.objects.create(
            email=email, name=name, password=hashed_password,
            phone_number=phone_number, date_of_birth=dob,
            country=country, gender=gender, agreed_to_terms=agreed_to_terms, role=role,
            profile_picture=profile_picture  # Save the profile picture
        )

        # Send verification email
        send_verification_email(user)

        # Success message and redirect
        return render(request, 'pages/signup.html', {"success": "Account created successfully. Please check your email to verify your account."})

    return render(request, 'pages/signup.html')

def verify_email(request, token):
    try:
        user = Signup.objects.get(verification_token=token)

        # Check if the token has expired
        if user.token_expiry < timezone.now():
            return HttpResponse("Verification link expired. Please request a new one.")

        # Mark the user as verified
        user.is_verified = True
        user.verification_token = None  # Clear the token after successful verification
        user.token_expiry = None  # Clear the expiration time
        user.save()

        return redirect('pages:login')  # Redirect to login after successful verification
    except Signup.DoesNotExist:
        return HttpResponse("Invalid verification link.")

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
