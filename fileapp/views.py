import os
import uuid
import random
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from .forms import UploadForm, CodeForm
from .models import FileShare
from .encryption import encrypt_bytes, decrypt_bytes
from .cleaners import clean_expired
import zipfile
import io

def home_view(request):
    return render(request, "fileapp/home.html")

def _generate_unique_code():
    for _ in range(1000):
        code = f"{random.randint(0, 999999):06d}"
        if not FileShare.objects.filter(code=code, created_at__gt=timezone.now() - timezone.timedelta(minutes=2)).exists():
            return code
    return f"{random.randint(0, 999999):06d}"

def upload_view(request):
    clean_expired()
    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist("files")
            files = files[:3]

            enc_dir = "/tmp/encrypted"
            os.makedirs(enc_dir, exist_ok=True)

            saved_paths = []
            orig_names = []
            wrapped_key = None

            for f in files:
                data = f.read()
                payload, wrapped = encrypt_bytes(data)
                if wrapped_key is None:
                    wrapped_key = wrapped

                name = f"{uuid.uuid4().hex}.enc"
                fullpath = f"/tmp/encrypted/{name}"

                with open(fullpath, "wb") as fh:
                    fh.write(payload)

                saved_paths.append(fullpath)
                orig_names.append(f.name)

            while len(saved_paths) < 3:
                saved_paths.append(None)
                orig_names.append(None)

            code = _generate_unique_code()

            FileShare.objects.create(
                code=code,
                encrypted_key=wrapped_key,
                file1_path=saved_paths[0],
                file2_path=saved_paths[1],
                file3_path=saved_paths[2],
                file1_original=orig_names[0],
                file2_original=orig_names[1],
                file3_original=orig_names[2],
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

            entries = [
                (rec.file1_path, rec.file1_original),
                (rec.file2_path, rec.file2_original),
                (rec.file3_path, rec.file3_original),
            ]

            outputs = []
            for path, name in entries:
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
