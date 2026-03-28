from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),   # til almashtirish — CHANGED
    path('', include('apps.users.urls')),
    path('', include('apps.patients.urls')),
    path('', include('apps.drugs.urls')),
    path('', include('apps.prescriptions.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
