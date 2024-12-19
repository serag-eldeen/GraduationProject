from django.urls import path
from . import views

app_name = 'proapp'

urlpatterns = [
    path('home/', views.home, name='home'),
]
