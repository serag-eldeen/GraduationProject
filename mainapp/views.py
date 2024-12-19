from django.shortcuts import render, redirect
from pages.models import Signup
from django.contrib import messages
from .models import CardDetails

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
            return render(request, 'mainapp/home.html', {'user_name': user_name})  # Free role home page
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