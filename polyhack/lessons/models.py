from django.db import models
from django.core.validators import FileExtensionValidator
from classes.models import Class
import os
from django.conf import settings
from django.utils.text import slugify

def video_upload_path(instance, filename):
    base, ext = os.path.splitext(filename)
    safe_name = f"{slugify(base)}{ext}"
    return os.path.join('lessons', 'videos', safe_name)

def pdf_upload_path(instance, filename):
    base, ext = os.path.splitext(filename)
    safe_name = f"{slugify(base)}{ext}"
    return os.path.join('lessons', 'pdfs', safe_name)

def model_upload_path(instance, filename):
    base, ext = os.path.splitext(filename)
    safe_name = f"{slugify(base)}{ext}"
    return os.path.join('lessons', 'models', safe_name)

class Lesson(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(
        help_text="Brief description of the lesson",
        null=True,
        blank=True
    )
    class_instance = models.ForeignKey(
        Class, 
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    pdf_content = models.FileField(
        upload_to=pdf_upload_path,
        validators=[FileExtensionValidator(['pdf'])],
        null=True,
        blank=True,
        help_text="Upload PDF material for the lesson"
    )
    video_content = models.FileField(
        upload_to=video_upload_path,
        validators=[FileExtensionValidator(['mp4', 'webm', 'mkv'])],
        null=True,
        blank=True,
        help_text="Upload video recording of the session"
    )
    video_summary = models.TextField(
        null=True,
        blank=True,
        help_text="AI-generated summary of the video content"
    )
    has_simulation = models.BooleanField(default=False)
    simulation_url = models.URLField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    has_3d_model = models.BooleanField(default=False)
    model_file = models.FileField(
        upload_to=model_upload_path,
        validators=[FileExtensionValidator(['glb', 'gltf'])],
        null=True,
        blank=True,
        help_text="Upload 3D model file (GLB format)"
    )
    model_poster = models.ImageField(
        upload_to=model_upload_path,
        null=True,
        blank=True,
        help_text="Upload poster image for 3D model"
    )

    def __str__(self):
        return f"{self.title} - {self.class_instance.name}"

    class Meta:
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'
        ordering = ['-created_at']

    def has_content(self):
        return bool(self.pdf_content or self.video_content) 