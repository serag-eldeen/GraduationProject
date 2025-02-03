# mainapp/urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'mainapp'

urlpatterns = [
    path('home/', views.home, name='home'),  # Add the 'home' page URL
    path('logout/', views.logout, name='logout'),  # Define the 'logout' URL explicitly
    path('change_role/<str:role>/', views.change_role, name='change_role'),  # Change role
    path('pay/', views.card_payment_form, name='card_payment_form'),
    path('process-payment/', views.process_card_payment, name='process_card_payment'),
    path('decode/', views.decode_image, name='decode'),
    path('encode/', views.encode_image, name='encode'),
    path('calculate-max-characters/', views.calculate_max_characters, name='calculate_max_characters'),
    path('profile/', views.profile, name='profile'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('update_profile/', views.update_profile, name='update_profile'),
]
# Add this to serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)