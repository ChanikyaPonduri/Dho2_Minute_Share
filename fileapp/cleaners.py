import os
from django.utils import timezone
from datetime import timedelta
from .models import FileShare

def clean_expired():
    expired = FileShare.objects.filter(
        created_at__lt=timezone.now() - timedelta(minutes=2)
    )

    for rec in expired:
        full = rec.file_path
        if os.path.exists(full):
            try:
                os.remove(full)
            except:
                pass

    expired.delete()
