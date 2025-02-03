from . import image_preparation as img
from . import data_embedding as stego
from django.http import HttpResponse
from django.conf import settings
import numpy as np
import bitstring
import cv2
import os
from django.http import JsonResponse
from django.core.files.storage import default_storage
import os
import cv2
from .data_embedding import get_dct_blocks
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

    return redirect('proapp:profile') 

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

    return render(request, 'proapp/profile.html', {'user': user})


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
        return render(request, 'proapp/home.html', {'user': user})  # Pass user object
    except Signup.DoesNotExist:
        return redirect('pages:login')  # If user not found, redirect to login page


def image(request):
    return render(request, 'proapp/image.html')  # Template for Pro App Home

def video(request):
    return render(request, 'proapp/video.html')  # Template for Pro App Home

def image_lsb_enc(request):
    return render(request, 'proapp/image_lsb_enc.html')  # Template for Pro App Home

def image_lsb_dec(request):
    return render(request, 'proapp/image_lsb_dec.html')  # Template for Pro App Home



import numpy as np

def zigzag(input):
    """
    Perform a zigzag scan of a 2D matrix.
    
    Arguments:
    - input: A 2D numpy array (matrix) of any size.
    
    Returns:
    - A 1D numpy array containing elements of the matrix in zigzag order.
    """
    
    # Initialize variables to keep track of the current position in the matrix
    h, v = 0, 0  # Horizontal and vertical indices
    vmax, hmax = input.shape  # Matrix dimensions
    
    # Initialize the output array with the total number of elements
    output = np.zeros(vmax * hmax)
    i = 0  # Index for the output array
    
    # Perform zigzag scan until the entire matrix is covered
    while (v < vmax) and (h < hmax):
        if (h + v) % 2 == 0:  # Moving up
            if v == 0 or h == hmax - 1:  # Edge cases
                output[i] = input[v, h]
                if h == hmax - 1:  # Last column, move down
                    v += 1
                else:  # Move right if not last column
                    h += 1
                i += 1
            else:  # Move up diagonally
                output[i] = input[v, h]
                v -= 1
                h += 1
                i += 1
        else:  # Moving down
            if h == 0 or v == vmax - 1:  # Edge cases
                output[i] = input[v, h]
                if v == vmax - 1:  # Last row, move right
                    h += 1
                else:  # Move down if not last row
                    v += 1
                i += 1
            else:  # Move down diagonally
                output[i] = input[v, h]
                v += 1
                h -= 1
                i += 1

        # Handle bottom-right element (end of matrix)
        if v == vmax - 1 and h == hmax - 1:
            output[i] = input[v, h]
            break

    return output


def inverse_zigzag(input, vmax, hmax):
    """
    Reconstruct a 2D matrix from a 1D zigzag-scanned array.
    
    Arguments:
    - input: A 1D numpy array containing elements in zigzag order.
    - vmax: The number of rows in the output 2D matrix.
    - hmax: The number of columns in the output 2D matrix.
    
    Returns:
    - A 2D numpy array (matrix) with dimensions (vmax, hmax).
    """
    
    # Initialize the output matrix and set current position
    output = np.zeros((vmax, hmax))
    h, v = 0, 0
    i = 0  # Index for the input array
    
    # Perform inverse zigzag scan to fill the matrix
    while (v < vmax) and (h < hmax):
        if (h + v) % 2 == 0:  # Moving up
            if v == 0 or h == hmax - 1:  # Edge cases
                output[v, h] = input[i]
                if h == hmax - 1:  # Last column, move down
                    v += 1
                else:  # Move right if not last column
                    h += 1
                i += 1
            else:  # Move up diagonally
                output[v, h] = input[i]
                v -= 1
                h += 1
                i += 1
        else:  # Moving down
            if h == 0 or v == vmax - 1:  # Edge cases
                output[v, h] = input[i]
                if v == vmax - 1:  # Last row, move right
                    h += 1
                else:  # Move down if not last row
                    v += 1
                i += 1
            else:  # Move down diagonally
                output[v, h] = input[i]
                v += 1
                h -= 1
                i += 1

        # Handle bottom-right element (end of matrix)
        if v == vmax - 1 and h == hmax - 1:
            output[v, h] = input[i]
            break

    return output






NUM_CHANNELS = 3  # Assuming 3 channels for Y, Cr, Cb




def image_DCT_enc(request):
    max_chars = None  # Default to None

    if request.method == "POST":
        cover_image = request.FILES.get('cover_image')
        secret_message = request.POST.get('secret_message')

        if cover_image:
            # Save the uploaded cover image temporarily
            cover_image_path = os.path.join(settings.MEDIA_ROOT, 'temp_cover_image.png')
            with open(cover_image_path, 'wb') as f:
                for chunk in cover_image.chunks():
                    f.write(chunk)

            # Get DCT blocks and calculate the number of characters
            dct_blocks, _ = get_dct_blocks(cover_image_path)
            if dct_blocks is not None:
                # Calculate max_chars based on the number of DCT blocks
                max_chars = len(dct_blocks) // 8  # One character requires 8 bits (64 bits per block / 8 = 8 chars per block)

        # Validate message length BEFORE embedding
        if secret_message and max_chars is not None:
            if len(secret_message) > max_chars:
                return render(request, 'proapp/image_DCT_enc.html', {
                    'error': f"Your message is too long! Max allowed: {max_chars} characters.",
                    'max_chars': max_chars
                })

        if cover_image and secret_message:
            output_filename = 'stego_image.png'
            output_path = os.path.join(settings.MEDIA_ROOT, output_filename)

            try:
                # Embed the secret message into the cover image using DCT
                embed_message(cover_image_path, secret_message, output_path)
            except ValueError as e:
                return render(request, 'proapp/image_DCT_enc.html', {
                    'error': str(e),
                    'max_chars': max_chars
                })

            # Prepare the file for download
            with open(output_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type="image/png")
                response['Content-Disposition'] = f'attachment; filename={output_filename}'
                return response

    return render(request, 'proapp/image_DCT_enc.html', {'max_chars': max_chars})

def calculate_capacity_ajax(request):
    """Handles AJAX requests to calculate embedding capacity."""
    if request.method == "POST" and request.FILES.get('cover_image'):
        cover_image = request.FILES['cover_image']

        # Save the uploaded cover image temporarily
        cover_image_path = os.path.join(settings.MEDIA_ROOT, 'temp_cover_image.png')
        with open(cover_image_path, 'wb') as f:
            for chunk in cover_image.chunks():
                f.write(chunk)

        # Get DCT blocks and calculate the number of characters
        dct_blocks, _ = get_dct_blocks(cover_image_path)
        if dct_blocks is not None:
            # Calculate max_chars based on the number of DCT blocks (1 block can store 8 characters)
            max_chars = len(dct_blocks) // 8
            return JsonResponse({'max_chars': max_chars})

    return JsonResponse({'max_chars': 0})  # Default case


def image_DCT_dec(request):
    secret_message = None  # Initialize the variable to hold the decoded message

    if request.method == "POST":
        stego_image = request.FILES.get('stego_image')  # Match the field name in the form
        
        if stego_image:
            stego_image_path = os.path.join(settings.MEDIA_ROOT, 'temp_stego_image.png')

            # Save the uploaded stego image temporarily
            with open(stego_image_path, 'wb') as f:
                for chunk in stego_image.chunks():
                    f.write(chunk)

            # Extract the secret message
            secret_message = extract_message(stego_image_path)

    return render(request, 'proapp/image_DCT_dec.html', {'secret_message': secret_message})

# --------------------- EMBEDDING FUNCTION --------------------- #
def embed_message(cover_image_filepath, secret_message, stego_image_filepath):
    # Load the cover image in BGR format and get its dimensions
    raw_cover_image = cv2.imread(cover_image_filepath, flags=cv2.IMREAD_COLOR)
    height, width = raw_cover_image.shape[:2]

    # Ensure image dimensions are 8x8 compliant by padding if needed
    while height % 8: height += 1
    while width % 8: width += 1
    valid_dim = (width, height)
    padded_image = cv2.resize(raw_cover_image, valid_dim)

    # Convert image to YCrCb colorspace and float32 format for DCT processing
    cover_image_f32 = np.float32(padded_image)
    cover_image_YCC = img.YCC_Image(cv2.cvtColor(cover_image_f32, cv2.COLOR_BGR2YCrCb))

    # Initialize an empty array to hold the processed stego image data
    stego_image = np.empty_like(cover_image_f32)

    # Process each color channel (Y, Cr, Cb) independently
    for chan_index in range(NUM_CHANNELS):
        # ----------- FORWARD DCT STAGE ----------- 
        dct_blocks = [cv2.dct(block) for block in cover_image_YCC.channels[chan_index]]

        # ----------- QUANTIZATION STAGE ----------- 
        dct_quants = [np.around(np.divide(item, img.JPEG_STD_LUM_QUANT_TABLE)) for item in dct_blocks]

        # Sort DCT coefficients in zigzag order
        sorted_coefficients = [zigzag(block) for block in dct_quants]

        # Embed secret data only in the Y (Luminance) channel
        if chan_index == 0:
            # Convert secret message to binary bitstream for embedding
            secret_data = bitstring.BitStream()
            for char in secret_message.encode('ascii'):
                secret_data.append(f'uint:8={char}')

            # Embed the secret data into the DCT coefficients
            embedded_dct_blocks = stego.embed_encoded_data_into_DCT(secret_data, sorted_coefficients)

            # Reorder embedded coefficients back to their original 2D positions
            desorted_coefficients = [inverse_zigzag(block, vmax=8, hmax=8) for block in embedded_dct_blocks]
        else:
            # No embedding; reformat coefficients for inverse DCT
            desorted_coefficients = [inverse_zigzag(block, vmax=8, hmax=8) for block in sorted_coefficients]

        # ----------- DEQUANTIZATION STAGE ----------- 
        dct_dequants = [np.multiply(data, img.JPEG_STD_LUM_QUANT_TABLE) for data in desorted_coefficients]

        # ----------- INVERSE DCT STAGE ----------- 
        idct_blocks = [cv2.idct(block) for block in dct_dequants]

        # Stitch the processed 8x8 blocks back together to form a full channel image
        stego_image[:, :, chan_index] = np.asarray(img.stitch_8x8_blocks_back_together(cover_image_YCC.width, idct_blocks))

    # Convert the stego image back to BGR color space from YCrCb
    stego_image_BGR = cv2.cvtColor(stego_image, cv2.COLOR_YCR_CB2BGR)

    # Clamp pixel values to ensure they are within valid image range [0, 255]
    final_stego_image = np.uint8(np.clip(stego_image_BGR, 0, 255))

    # Save the final stego image to disk
    cv2.imwrite(stego_image_filepath, final_stego_image)
    print(f"Secret message embedded and stego image saved to {stego_image_filepath}")



def extract_message(stego_image_filepath):
    # Read the stego image
    stego_image = cv2.imread(stego_image_filepath, flags=cv2.IMREAD_COLOR)
    height, width = stego_image.shape[:2]
    stego_image_f32 = np.float32(stego_image)
    
    # Convert the image to YCrCb color space
    stego_image_YCC = img.YCC_Image(cv2.cvtColor(stego_image_f32, cv2.COLOR_BGR2YCrCb))

    # Extract DCT coefficients
    dct_blocks = [cv2.dct(block) for block in stego_image_YCC.channels[0]]
    dct_quants = [np.around(np.divide(item, img.JPEG_STD_LUM_QUANT_TABLE)) for item in dct_blocks]
    
    # Sort DCT coefficients in zigzag order
    sorted_coefficients = [zigzag(block) for block in dct_quants]
    
    # Extract encoded data from DCT coefficients
    recovered_data = stego.extract_encoded_data_from_DCT(sorted_coefficients)
    recovered_data.pos = 0  # Reset the bitstream position
    
    # Read the length of the data (assuming it's stored as a 32-bit unsigned integer)
    data_len = int(recovered_data.read('uint:32') / 8)  # Convert from bits to bytes
    
    # Extract the secret data byte by byte
    extracted_data = bytes([recovered_data.read('uint:8') for _ in range(data_len)])
    
    try:
        # Try to decode the extracted data to a string (assuming it's encoded as UTF-8)
        return extracted_data.decode('utf-8')  # Use 'utf-8' to support a broader range of characters
    except UnicodeDecodeError:
        try:
            # If UTF-8 fails, attempt to decode using 'latin-1' or similar encoding
            return extracted_data.decode('latin-1')  # 'latin-1' supports byte-to-byte mapping
        except UnicodeDecodeError:
            # If decoding fails, return the raw binary data
            print(f"Unable to decode as UTF-8 or latin-1, returning binary data: {extracted_data}")
            return extracted_data  # Or return as binary if message isn't string-based


def video_lsb_enc(request):
    return render(request, 'proapp/video_lsb_enc.html')



def video_lsb_dec(request):
    return render(request, 'proapp/video_lsb_dec.html')
  
def video_DCT_enc(request):
    return render(request, 'proapp/video_DCT_enc.html')  # Template for Pro App Home

def video_DCT_dec(request):
    return render(request, 'proapp/video_DCT_dec.html')  # Template for Pro App Home
