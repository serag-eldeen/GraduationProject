from .steganography_utils import encode, decode ,encode_enc , max_characters # Import the utility functions
from django.shortcuts import render, redirect
from PIL import Image, UnidentifiedImageError
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render
from django.conf import settings
from pages.models import Signup
from .models import CardDetails
from PIL import Image
import os
from django.http import JsonResponse
from django.shortcuts import render, redirect
from pages.models import Signup
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist




def delete_account(request):
    if 'user_id' not in request.session:
        return redirect('pages:login')  # Redirect to login if not authenticated

    user = Signup.objects.get(id=request.session['user_id'])

    if request.method == "POST" and 'delete_account' in request.POST:
        # Delete the user account
        user.delete()

        # Log the user out and redirect to the login page
        logout(request)  # Optionally, log the user out after deletion
        messages.success(request, "Your account has been deleted successfully.")
        return redirect('pages:index')  # Redirect to login or homepage after deletion

    return redirect('mainapp:profile') 

def update_profile(request):
    if request.method == "POST":
        # Get the current user from the session or request
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('pages:login')  # Redirect to login if user is not authenticated

        try:
            user = Signup.objects.get(id=user_id)

            # Update the profile picture if provided
            if request.FILES.get('profile_picture'):
                user.profile_picture = request.FILES['profile_picture']

            # Update the username if provided
            if 'user_name' in request.POST:
                user.name = request.POST['user_name']

            # Update the phone number if provided
            if 'phone_number' in request.POST:
                user.phone_number = request.POST['phone_number']

            # Save the changes to the user model
            user.save()

            return redirect('mainapp:profile')  # Redirect to profile page after saving changes
        except ObjectDoesNotExist:
            return redirect('pages:login')  # If user not found, redirect to login page

    return redirect('mainapp:profile')
def profile(request):
    if 'user_id' not in request.session:
        return redirect('pages:login')  # Redirect to login if not authenticated

    user = Signup.objects.get(id=request.session['user_id'])

    if not user.is_verified:
        return render(request, 'pages/verify_email_prompt.html', {'user': user})

    return render(request, 'mainapp/profile.html', {'user': user})


def reset_password(request):
    if 'user_id' not in request.session:
        return redirect('pages:login')

    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        user = Signup.objects.get(id=request.session['user_id'])

        # Check if current password is correct
        if not check_password(current_password, user.password):
            messages.error(request, "Current password is incorrect.")
            return redirect('mainapp:reset_password')

        # Check if new password matches
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect('mainapp:reset_password')

        # Validate password strength
        password_error = validate_password_strength(new_password)
        if password_error:
            messages.error(request, password_error)
            return redirect('mainapp:reset_password')

        # Update password
        user.password = make_password(new_password)
        user.save()
        messages.success(request, "Password updated successfully.")
        return redirect('mainapp:profile')

    return render(request, 'mainapp/reset_password.html')

def validate_password_strength(password):
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not any(char.isdigit() for char in password):
        return "Password must contain at least one digit."
    if not any(char.isalpha() for char in password):
        return "Password must contain at least one letter."
    if not any(char in "@$!%*?&" for char in password):
        return "Password must contain at least one special character (@, $, !, %, *, ?, &)."
    return None

def card_payment_form(request):
    # Get the plan from GET parameters (default to 'pro' if not provided)
    plan = request.GET.get('plan', 'pro')
    
    # Set amount based on the selected plan
    if plan == 'pro':
        amount = 100
    elif plan == 'premium':
        amount = 200
    else:
        amount = 100  # Default to 'pro' price
    
    context = {
        'amount': amount,
        'plan': plan,
    }
    return render(request, 'mainapp/pay.html', context)

def process_card_payment(request):
    """Process the payment with the selected plan and amount."""
    if request.method == 'POST':
        card_number = request.POST.get('card_number')
        expiry_month = request.POST.get('expiry_month')
        expiry_year = request.POST.get('expiry_year')
        cvv = request.POST.get('cvv')
        amount = request.POST.get('amount')
        plan = request.POST.get('plan')  # Get the selected plan

        expiry_date = f"{expiry_month}/{expiry_year}"

        if card_number and expiry_date and cvv:
            CardDetails.objects.create(
                card_number=card_number,
                expiry_date=expiry_date,
                cvv=cvv,
            )
            # Redirect based on plan
            if plan == 'pro':
                return redirect('mainapp:change_role', role='pro')
            elif plan == 'premium':
                return redirect('mainapp:change_role', role='premium')
            else:
                messages.error(request, 'Invalid plan selected.')
                return redirect('mainapp:card_payment_form')
        else:
            messages.error(request, 'Please fill in all required fields.')
        return redirect('mainapp:card_payment_form')
    return redirect('mainapp:card_payment_form')
















def home(request):
    user_id = request.session.get('user_id')  # Retrieve user ID from session
    if not user_id:
        return redirect('pages:login')  # Redirect to login if session data is missing

    # Retrieve user details from the database
    try:
        user = Signup.objects.get(id=user_id)
        user_name = user.name
        user_role = user.role  # Get the user's role (e.g., 'free', 'pro', 'premium')

        # Redirect to the appropriate home page based on the user's role
        if user_role == 'pro':
            return redirect('proapp:home')  # Redirect to Pro app home page
        elif user_role == 'premium':
            return redirect('premiumapp:home')  # Redirect to Premium app home page
        else:
            return render(request, 'mainapp/home.html', {'user': user})  # Pass user object
    except Signup.DoesNotExist:
        return redirect('pages:login')  # If user not found, redirect to login page


def change_role(request, role):
    """
    Change the user's role based on their subscription.
    Redirect to the respective app based on the role.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('pages:login')

    try:
        user = Signup.objects.get(id=user_id)
        if role in ['free', 'pro', 'premium']:
            user.role = role
            user.save()

            if role == 'pro':
                return redirect('proapp:home')  # Redirect to Pro App
            elif role == 'premium':
                return redirect('premiumapp:home')  # Redirect to Premium App
            else:
                return redirect('mainapp:home')  # Free users stay in Main App
        else:
            return redirect('mainapp:home')  # Invalid role fallback
    except Signup.DoesNotExist:
        return redirect('pages:login')
    

def logout(request):
    # Clear the session
    request.session.flush()

    # Redirect to the index page in the 'pages' app
    response = redirect('pages:index')
    response.delete_cookie('user_email')  # Delete the 'user_email' cookie
    return response

def subscribe(request, price):
    try:
        # Convert price from string to float
        price = float(price)
    except ValueError:
        # Handle invalid price if necessary (e.g., redirect to an error page)
        return redirect('mainapp:home')

    # Store the selected price in the session
    request.session['selected_price'] = price
    return redirect('mainapp:pay')  # Redirect to the payment page

def pay(request):
    # Retrieve the price from the session
    price = request.session.get('selected_price', None)
    if not price:
        # If no price is found, redirect to a default page (like an error page or home)
        return redirect('mainapp:home')
    
    return render(request, 'mainapp/pay.html', {'price': price})




def encode_image(request):
    if request.method == "POST":
        # Get user inputs
        message = request.POST.get("message")
        image_file = request.FILES.get("image")

        if not message or not image_file:
            return HttpResponse("Please provide both an image and a message.")

        # Open uploaded image
        img = Image.open(image_file)
        max_chars = max_characters(image_file)

        if len(message) > max_chars:
            return HttpResponse(f"Message is too long. Maximum characters allowed: {max_chars}")

        new_img = img.copy()

        # Embed message into the image
        try:
            encode_enc(new_img, message)
        except Exception as e:
            return HttpResponse(f"An error occurred during encoding: {e}")

        # Save the encoded image temporarily
        output_path = os.path.join(settings.MEDIA_ROOT, "encoded.png")
        new_img.save(output_path)

        # Serve the image as a downloadable file
        with open(output_path, "rb") as f:
            response = HttpResponse(f.read(), content_type="image/png")
            response["Content-Disposition"] = "attachment; filename=encoded.png"
            return response

    return render(request, "mainapp/encode.html")


# Function to decode data from an image
def decode_image(request):
    decoded_message = None  # Initialize the decoded message

    if request.method == "POST":
        image = request.FILES.get('image')

        if not image:
            return render(request, 'mainapp/decode.html', {'error': "Please upload an image."})

        # Save the uploaded image to a temporary location
        temp_image_path = os.path.join(settings.MEDIA_ROOT, 'temp_decode_image.png')
        with open(temp_image_path, 'wb') as f:
            for chunk in image.chunks():
                f.write(chunk)

        # Process the image
        try:
            decoded_message = decode(temp_image_path)  # Call the decode function
        except Exception as e:
            return render(request, 'mainapp/decode.html', {'error': f"An error occurred: {e}"})

    # Render the page with the decoded message or error
    return render(request, 'mainapp/decode.html', {'decoded_message': decoded_message})




# View to calculate max characters based on image
def calculate_max_characters(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']

        # Temporarily save the image to calculate max characters
        temp_image_path = os.path.join(settings.MEDIA_ROOT, 'temp_image.png')
        with open(temp_image_path, 'wb') as f:
            for chunk in image.chunks():
                f.write(chunk)

        try:
            max_chars = max_characters(temp_image_path)
            os.remove(temp_image_path)  # Clean up temporary file
            return JsonResponse({'max_chars': max_chars})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)

