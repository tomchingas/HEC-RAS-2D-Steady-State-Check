from django.urls import path
from . import views


app_name = 'app_file_upload'


urlpatterns = [
    path("", views.home, name="home"),
    path("upload", views.upload, name="upload")
]