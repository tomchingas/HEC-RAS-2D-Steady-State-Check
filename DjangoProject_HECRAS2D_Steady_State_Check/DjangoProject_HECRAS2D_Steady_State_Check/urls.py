"""DjangoProject_HECRAS2D_Steady_State_Check URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# UPLOAD NOTE: Keep in mind it only works when DEBUG is set to True and the URL specified in the settings is local (i.e. /media/ not https://media.site.com/). Will want to upload to a host server for production

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include ('app_file_upload.urls')),
    path('upload/', include('app_file_upload.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
