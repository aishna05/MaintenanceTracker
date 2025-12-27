from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # Changed from '' to 'accounts/'
    path('auth/', include('django.contrib.auth.urls')),
    path('', include('gearguard.urls')),  # GearGuard at root
]
