# mainapp/urls.py
from django.urls import path
from . import views

app_name = 'mainapp'

urlpatterns = [
    path('home/', views.home, name='home'),  # Add the 'home' page URL
    path('logout/', views.logout, name='logout'),  # Define the 'logout' URL explicitly
    path('change_role/<str:role>/', views.change_role, name='change_role'),  # Change role
    path('pay/', views.card_payment_form, name='card_payment_form'),
    path('process-payment/', views.process_card_payment, name='process_card_payment'),
]
