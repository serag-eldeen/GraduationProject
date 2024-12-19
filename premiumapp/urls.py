from django.urls import path
from . import views

app_name = 'premiumapp'

urlpatterns = [
    path('home/', views.home, name='home'),
]
