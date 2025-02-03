from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from . import views

app_name = 'proapp'

urlpatterns = [
    path('home/', views.home, name='home'),
    path('image/', views.image, name='image'),
    path('video/', views.video, name='video'),
    path('image_lsb_enc/', views.image_lsb_enc, name='image_lsb_enc'),
    path('image_lsb_dec/', views.image_lsb_dec, name='image_lsb_dec'),
    path('image_DCT_enc/', views.image_DCT_enc, name='image_DCT_enc'),
    path('calculate_capacity_ajax/', views.calculate_capacity_ajax, name='calculate_capacity_ajax'),
    path('image_DCT_dec/', views.image_DCT_dec, name='image_DCT_dec'),
    path('video_lsb_enc/', views.video_lsb_enc, name='video_lsb_enc'),
    path('video_lsb_dec/', views.video_lsb_dec, name='video_lsb_dec'),
    path('video_DCT_enc/', views.video_DCT_enc, name='video_DCT_enc'),
    path('video_DCT_dec/', views.video_DCT_dec, name='video_DCT_dec'),
    path('profile/', views.profile, name='profile'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('delete-account/', views.delete_account, name='delete_account'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
