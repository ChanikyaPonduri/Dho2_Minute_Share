import os
from django.utils import timezone
from datetime import timedelta
from .models import FileShare

def clean_expired():
    expired = FileShare.objects.filter(
        created_at__lt=timezone.now() - timedelta(minutes=2)
    )
    for rec in expired:
        paths = [rec.file1_path, rec.file2_path, rec.file3_path]
        for p in paths:
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except:
                    pass
    expired.delete()
