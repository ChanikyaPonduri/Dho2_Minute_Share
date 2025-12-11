import os
import uuid
import random
from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from django.urls import reverse
from django.utils import timezone
from .forms import UploadForm, CodeForm
from .models import FileShare
from .encryption import encrypt_bytes, decrypt_bytes
from .cleaners import clean_expired

def home_view(request):
    return render(request, "fileapp/home.html")

def _generate_unique_code():
    for _ in range(1000):
        code = f"{random.randint(0, 999999):06d}"
        exists = FileShare.objects.filter(code=code, created_at__gt=timezone.now() - timezone.timedelta(minutes=2)).exists()
        if not exists:
            return code
    while True:
        code = f"{random.randint(0, 999999):06d}"
        if not FileShare.objects.filter(code=code, created_at__gt=timezone.now() - timezone.timedelta(minutes=2)).exists():
            return code

def upload_view(request):
    clean_expired()
    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES["file"]
            original = f.name
            data = f.read()

            payload, wrapped = encrypt_bytes(data)

            enc_dir = "/tmp/encrypted"
            os.makedirs(enc_dir, exist_ok=True)

            filename = f"{uuid.uuid4().hex}.enc"
            fullpath = f"/tmp/encrypted/{filename}"

            with open(fullpath, "wb") as fh:
                fh.write(payload)

            code = _generate_unique_code()

            FileShare.objects.create(
                code=code,
                file_path=fullpath,
                encrypted_key=wrapped,
                original_filename=original
            )

            return render(request, "fileapp/success.html", {"code": code})
    else:
        form = UploadForm()

    return render(request, "fileapp/upload.html", {"form": form})

def download_view(request):
    clean_expired()
    error = None
    if request.method == "POST":
        form = CodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]

            try:
                rec = FileShare.objects.get(code=code)
            except FileShare.DoesNotExist:
                return render(request, "fileapp/not_found.html")

            if rec.is_expired():
                return render(request, "fileapp/not_found.html")

            full = rec.file_path
            if not os.path.exists(full):
                return render(request, "fileapp/not_found.html")

            with open(full, "rb") as fh:
                payload = fh.read()

            try:
                plain = decrypt_bytes(payload, rec.encrypted_key)
            except:
                return render(request, "fileapp/not_found.html")

            response = HttpResponse(plain, content_type="application/octet-stream")
            response["Content-Disposition"] = f'attachment; filename="{rec.original_filename}"'
            return response

    else:
        form = CodeForm()

    return render(request, "fileapp/download.html", {"form": form, "error": error})

def cancel_share(request, code):
    try:
        rec = FileShare.objects.get(code=code)
    except FileShare.DoesNotExist:
        return redirect("home")

    full = rec.file_path
    if os.path.exists(full):
        os.remove(full)

    rec.delete()

    return render(request, "fileapp/cancelled.html")
