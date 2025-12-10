from django.db import models
from django.utils import timezone
from datetime import timedelta

class FileShare(models.Model):
    code = models.CharField(max_length=6, unique=True)
    file_path = models.CharField(max_length=500)
    encrypted_key = models.TextField()
    original_filename = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=2)

    def expiry_time(self):
        return self.created_at + timedelta(minutes=2)
