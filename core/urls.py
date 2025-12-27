from django.contrib import admin
from django.urls import path, include
<<<<<<< HEAD
from django.conf import settings
from django.conf.urls.static import static
=======
>>>>>>> f2c9782093ae85f39d71042520c11cfd2ac3b462

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # Changed from '' to 'accounts/'
    path('auth/', include('django.contrib.auth.urls')),
    path('', include('gearguard.urls')),  # GearGuard at root
]
<<<<<<< HEAD

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT)
=======
>>>>>>> f2c9782093ae85f39d71042520c11cfd2ac3b462
