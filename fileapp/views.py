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
            uploaded = request.FILES.getlist("files")
            uploaded = uploaded[:3]

            enc_dir = "/tmp/encrypted"
            os.makedirs(enc_dir, exist_ok=True)

            filepaths = []
            originals = []
            key = None

            for f in uploaded:
                data = f.read()
                payload, wrapped = encrypt_bytes(data)
                if key is None:
                    key = wrapped

                filename = f"{uuid.uuid4().hex}.enc"
                fullpath = f"/tmp/encrypted/{filename}"

                with open(fullpath, "wb") as fh:
                    fh.write(payload)

                filepaths.append(fullpath)
                originals.append(f.name)

            while len(filepaths) < 3:
                filepaths.append(None)
                originals.append(None)

            code = _generate_unique_code()

            FileShare.objects.create(
                code=code,
                encrypted_key=key,
                file1_path=filepaths[0],
                file2_path=filepaths[1],
                file3_path=filepaths[2],
                file1_original=originals[0],
                file2_original=originals[1],
                file3_original=originals[2],
            )

            return render(request, "fileapp/success.html", {"code": code})
    else:
        form = UploadForm()

    return render(request, "fileapp/upload.html", {"form": form})

def download_view(request):
    clean_expired()
    if request.method == "POST":
        form = CodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]

            try:
                rec = FileShare.objects.get(code=code)
            except:
                return render(request, "fileapp/not_found.html")

            if rec.is_expired():
                return render(request, "fileapp/not_found.html")

            files = [
                (rec.file1_path, rec.file1_original),
                (rec.file2_path, rec.file2_original),
                (rec.file3_path, rec.file3_original),
            ]

            outputs = []

            for path, name in files:
                if path and os.path.exists(path):
                    with open(path, "rb") as fh:
                        payload = fh.read()
                    plain = decrypt_bytes(payload, rec.encrypted_key)
                    outputs.append((plain, name))

            if not outputs:
                return render(request, "fileapp/not_found.html")

            if len(outputs) == 1:
                data, name = outputs[0]
                resp = HttpResponse(data, content_type="application/octet-stream")
                resp["Content-Disposition"] = f'attachment; filename="{name}"'
                return resp

            import zipfile
            import io
            z = io.BytesIO()
            with zipfile.ZipFile(z, "w") as zipf:
                for data, name in outputs:
                    zipf.writestr(name, data)
            z.seek(0)

            resp = HttpResponse(z.read(), content_type="application/zip")
            resp["Content-Disposition"] = 'attachment; filename="files.zip"'
            return resp
    else:
        form = CodeForm()

    return render(request, "fileapp/download.html", {"form": form})

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
