from django.urls import path,include
from . import views


app_name = 'pages'  # Add this line to define the namespace

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('privacypolicy', views.privacypolicy, name='privacypolicy'),
    path('termsconditions', views.termsconditions, name='termsconditions'),
    path('articledetails', views.articledetails, name='articledetails'),
    
]