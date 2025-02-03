from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.http import FileResponse, JsonResponse
import numpy as np
from .utils import encrypt_audio, decrypt_audio
from django.http import JsonResponse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from .utils import encrypt_audio, decrypt_audio  # Assuming your functions are in audio_utils.py
from .utils2 import Embedding, Extracting
from django.conf import settings
import bitstring
import cv2
import os
import logging
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from pages.models import Signup
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.contrib.auth import logout


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

    return redirect('premiumapp:profile') 
def profile(request):
    if 'user_id' not in request.session:
        return redirect('pages:login')  # Redirect to login if not authenticated

    user = Signup.objects.get(id=request.session['user_id'])

    # If the user is not verified, show the email verification prompt
    if not user.is_verified:
        return render(request, 'pages/verify_email_prompt.html', {'user': user})

    # Handle the unsubscribe button action (role change to 'free')
    if request.method == "POST" and 'unsubscribe' in request.POST:
        # Change the user's role to 'free' and save
        user.role = 'free'
        user.save()

        # Redirect to the profile page after updating the role
        return redirect('mainapp:home')  # Or to another page of your choice after unsubscribe

    return render(request, 'premiumapp/profile.html', {'user': user})

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

def home(request):
    user_id = request.session.get('user_id')  # Retrieve user ID from session
    if not user_id:
        return redirect('pages:login')  # Redirect to login if session data is missing

    try:
        user = Signup.objects.get(id=user_id)  # Fetch user from DB
        return render(request, 'premiumapp/home.html', {'user': user})  # Pass user object
    except Signup.DoesNotExist:
        return redirect('pages:login')  # If user not found, redirect to login page


def image(request):
    return render(request, 'premiumapp/image.html')  # Template for premium App Home

def video(request):
    return render(request, 'premiumapp/video.html')  # Template for premium App Home

def audio(request):
    return render(request, 'premiumapp/audio.html')  # Template for premium App Home

def image_lsb_enc(request):
    return render(request, 'premiumapp/image_lsb_enc.html')  # Template for Pro App Home

def image_lsb_dec(request):
    return render(request, 'premiumapp/image_lsb_dec.html')  # Template for Pro App Home

def image_DCT_enc(request):
    return render(request, 'premiumapp/image_DCT_enc.html')  # Template for Pro App

def image_DCT_dec(request):
    return render(request, 'premiumapp/image_DCT_dec.html')  # Template for Pro App

def video_lsb_enc(request):
    return render(request, 'premiumapp/video_lsb_enc.html')  # Template for Pro App Home

def video_lsb_dec(request):
    return render(request, 'premiumapp/video_lsb_dec.html')  # Template for Pro App Home

def video_DCT_enc(request):
    return render(request, 'premiumapp/video_DCT_enc.html')  # Template for Pro App

def video_DCT_dec(request):
    return render(request, 'premiumapp/video_DCT_dec.html')  # Template for Pro App

# Embed message into audio
@csrf_exempt
def audio_lsb_enc(request):
    if request.method == "POST":
        try:
            audio_file = request.FILES.get("audio")
            message = request.POST.get("message")

            if not audio_file or not message:
                return render(request, 'premiumapp/audio_lsb_enc.html', {"error": "Audio file and message are required."})

            # Save the audio file
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            audio_path = fs.save(audio_file.name, audio_file)
            audio_full_path = os.path.join(settings.MEDIA_ROOT, audio_path)

            # Generate the output file path
            output_file_name = f"encrypted_{audio_file.name}"
            output_path = os.path.join(settings.MEDIA_ROOT, output_file_name)

            # Embed the message
            encrypt_audio(audio_full_path, message, output_path)

            # Prepare the file for download
            with open(output_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='audio/wav')
                response['Content-Disposition'] = f'attachment; filename={output_file_name}'
                return response

        except Exception as e:
            return render(request, 'premiumapp/audio_lsb_enc.html', {"error": str(e)})

    return render(request, 'premiumapp/audio_lsb_enc.html')


# Extract message from audio
@csrf_exempt
def audio_lsb_dec(request):
    if request.method == "POST":
        try:
            audio_file = request.FILES.get("audio")

            if not audio_file:
                return render(request, 'premiumapp/audio_lsb_dec.html', {"error": "Audio file is required."})

            # Save the uploaded audio file
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            audio_path = fs.save(audio_file.name, audio_file)
            audio_full_path = os.path.join(settings.MEDIA_ROOT, audio_path)

            # Extract the hidden message
            extracted_message = decrypt_audio(audio_full_path)

            return render(request, 'premiumapp/audio_lsb_dec.html', {"message": extracted_message})

        except Exception as e:
            return render(request, 'premiumapp/audio_lsb_dec.html', {"error": str(e)})

    return render(request, 'premiumapp/audio_lsb_dec.html')


def audio_phasecoding_enc(request):
    if request.method == 'POST' and request.FILES.get('audio'):
        audio_file = request.FILES['audio']
        message = request.POST.get('message')
        
        # Save the uploaded audio file
        fs = FileSystemStorage()
        filename = fs.save(audio_file.name, audio_file)
        uploaded_file_url = fs.url(filename)
        
        # Perform phase coding embedding
        input_filename = fs.path(filename)  # Full path to the file
        output_filename = fs.path('encoded_' + filename)
        
        # Call the embedding function (audio phase coding)
        Embedding(input_filename, output_filename, message)
        
        # Read the encoded file to return as a response for download
        with open(output_filename, 'rb') as encoded_file:
            response = HttpResponse(encoded_file.read(), content_type='audio/wav')
            response['Content-Disposition'] = f'attachment; filename="encoded_{audio_file.name}"'
            return response
    
    return render(request, 'premiumapp/audio_phaseecoding_enc.html')

def audio_phasecoding_dec(request):
    if request.method == 'POST' and request.FILES.get('audio'):
        audio_file = request.FILES['audio']
        
        # Save the uploaded audio file
        fs = FileSystemStorage()
        filename = fs.save(audio_file.name, audio_file)
        uploaded_file_url = fs.url(filename)
        
        # Perform phase coding extraction
        input_filename = fs.path(filename)  # Full path to the file
        msg_len = 1000  # Default message length to extract
        message = Extracting(input_filename, msg_len)
        
        # Return the message extracted on the same page
        return render(request, 'premiumapp/audio_phaseecoding_dec.html', {
            'message': message
        })
    
    return render(request, 'premiumapp/audio_phaseecoding_dec.html')

