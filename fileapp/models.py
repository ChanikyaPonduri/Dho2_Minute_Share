from django.db import models
from django.utils import timezone
from datetime import timedelta

class FileShare(models.Model):
    code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    encrypted_key = models.BinaryField()
    file1_path = models.CharField(max_length=500, blank=True, null=True)
    file2_path = models.CharField(max_length=500, blank=True, null=True)
    file3_path = models.CharCharField(max_length=500, blank=True, null=True)
    file1_original = models.CharField(max_length=255, blank=True, null=True)
    file2_original = models.CharField(max_length=255, blank=True, null=True)
    file3_original = models.CharField(max_length=255, blank=True, null=True)

    def is_expired(self):
        return self.created_at < timezone.now() - timedelta(minutes=2)
