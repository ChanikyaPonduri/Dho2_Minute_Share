import os
from django.utils import timezone
from datetime import timedelta
from .models import FileShare
from django.conf import settings

def clean_expired():
    expiration_threshold = timezone.now() - timedelta(minutes=2)
    expired = FileShare.objects.filter(created_at__lt=expiration_threshold)
    for rec in expired:
        try:
            path = rec.file_path
            full = os.path.join(settings.MEDIA_ROOT, path)
            if os.path.exists(full):
                os.remove(full)
        except Exception:
            pass
    expired.delete()
