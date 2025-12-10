from django.contrib import admin
from .models import FileShare

class FileShareAdmin(admin.ModelAdmin):
    list_display = ("code", "original_filename", "created_at")

admin.site.register(FileShare, FileShareAdmin)
