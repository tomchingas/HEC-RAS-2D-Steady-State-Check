from django.shortcuts import render
from django.core.files.storage import FileSystemStorage


def home(response):
    return render(response, "app_file_upload/upload.html", {})


def upload(request):
    if request.method == 'POST' and request.FILES['upload']:
        upload = request.FILES['upload']
        fss = FileSystemStorage()
        file = fss.save(upload.name, upload)
        file_url = fss.url(file)
        return render(request, 'app_file_upload/upload.html', {'file_url': file_url})
    return render(request, 'app_file_upload/upload.html')