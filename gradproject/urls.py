from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('pro/', include('proapp.urls')),
    path('premium/', include('premiumapp.urls')),
    path('mainapp/', include('mainapp.urls')),  # Main app URLs
    path('pages/', include('pages.urls')),  # Pages app URLs
    path('pages/', LogoutView.as_view(), name='logout'),
    path('', include('pages.urls')),  # Redirect root to pages app (e.g., login page)
]
