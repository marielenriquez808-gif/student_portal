from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('enrollment/', include('enrollment.urls')),
    path('grades/', include('grades.urls')),
    path('attendance/', include('attendance.urls')),
    path('schedules/', include('schedules.urls')),
    path('announcements/', include('announcements.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
