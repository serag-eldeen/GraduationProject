from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static



app_name = 'pages'  # Add this line to define the namespace

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('privacypolicy', views.privacypolicy, name='privacypolicy'),
    path('termsconditions', views.termsconditions, name='termsconditions'),
    path('articledetails', views.articledetails, name='articledetails'),
    path('verify/<str:token>/', views.verify_email, name='verify_email'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)