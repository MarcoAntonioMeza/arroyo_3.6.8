
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static

from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('arroyo.urls')),
]

#if  not settings.DEBUG:
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#surlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    