from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
import os

User = get_user_model()

class MediaFile(models.Model):
    MEDIA_TYPES = (
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('uploading', 'Uploading'),
        ('processing', 'Processing'),
        ('available', 'Available'),
        ('failed', 'Failed'),
        ('deleted', 'Deleted'),
    )
    
    # Basic information
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    alt_text = models.CharField(
        max_length=500,  # ✅ Changed from 200 to 500
        blank=True,
        help_text="Alternative text for accessibility (screen readers)"
    )
    
    # File information
    file = models.FileField(
        upload_to='media/%Y/%m/%d/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 
                                           'mp4', 'webm', 'ogg', 'mp3', 'wav', 
                                           'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'])]
    )
    file_type = models.CharField(max_length=20, choices=MEDIA_TYPES)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    mime_type = models.CharField(max_length=100, blank=True)
    file_hash = models.CharField(max_length=64, blank=True, db_index=True)
    
    # Metadata
    width = models.PositiveIntegerField(null=True, blank=True, help_text="Image/Video width in pixels")
    height = models.PositiveIntegerField(null=True, blank=True, help_text="Image/Video height in pixels")
    duration = models.PositiveIntegerField(null=True, blank=True, help_text="Duration in seconds for video/audio")
    
    # EXIF/IPTC data for images
    metadata = models.JSONField(default=dict, blank=True)
    
    # Relationships
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='media_files')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploading')
    
    # Featured flag
    featured = models.BooleanField(
        default=False,
        help_text="Mark this media as featured for display on the homepage and galleries"
    )
    
    # Usage tracking
    usage_count = models.PositiveIntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    
    # Thumbnails
    thumbnail_small = models.ImageField(upload_to='thumbnails/small/', blank=True, null=True)
    thumbnail_medium = models.ImageField(upload_to='thumbnails/medium/', blank=True, null=True)
    thumbnail_large = models.ImageField(upload_to='thumbnails/large/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'media_files'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['file_type', 'status']),
            models.Index(fields=['uploaded_by', 'created_at']),
            models.Index(fields=['file_hash']),
            models.Index(fields=['featured']),  # Added index for featured field
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.file_size and self.file:
            self.file_size = self.file.size
        
        if not self.mime_type and self.file:
            import mimetypes
            self.mime_type = mimetypes.guess_type(self.file.name)[0] or ''
        
        if not self.file_type:
            self.file_type = self.get_file_type()
        
        super().save(*args, **kwargs)
    
    def get_file_type(self):
        if not self.file:
            return 'other'
        
        ext = os.path.splitext(self.file.name)[1].lower()
        image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.ico']
        video_exts = ['.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv']
        audio_exts = ['.mp3', '.wav', '.ogg', '.m4a', '.flac']
        document_exts = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.rtf']
        
        if ext in image_exts:
            return 'image'
        elif ext in video_exts:
            return 'video'
        elif ext in audio_exts:
            return 'audio'
        elif ext in document_exts:
            return 'document'
        else:
            return 'other'
    
    def get_file_url(self):
        return self.file.url if self.file else ''
    
    def get_thumbnail_url(self, size='medium'):
        if size == 'small' and self.thumbnail_small:
            return self.thumbnail_small.url
        elif size == 'medium' and self.thumbnail_medium:
            return self.thumbnail_medium.url
        elif size == 'large' and self.thumbnail_large:
            return self.thumbnail_large.url
        return self.get_file_url()
    
    def increment_usage(self):
        self.usage_count += 1
        self.last_used = timezone.now()
        self.save(update_fields=['usage_count', 'last_used'])

class MediaTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'media_tags'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class MediaCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'media_categories'
        verbose_name_plural = 'Media Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class MediaFileTag(models.Model):
    media_file = models.ForeignKey(MediaFile, on_delete=models.CASCADE, related_name='tags')
    tag = models.ForeignKey(MediaTag, on_delete=models.CASCADE, related_name='media_files')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'media_file_tags'
        unique_together = ['media_file', 'tag']

class MediaFileCategory(models.Model):
    media_file = models.ForeignKey(MediaFile, on_delete=models.CASCADE, related_name='categories')
    category = models.ForeignKey(MediaCategory, on_delete=models.CASCADE, related_name='media_files')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'media_file_categories'
        unique_together = ['media_file', 'category']

class MediaUsage(models.Model):
    media_file = models.ForeignKey(MediaFile, on_delete=models.CASCADE, related_name='usages')
    model_name = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField()
    field_name = models.CharField(max_length=100)
    used_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'media_usages'
        ordering = ['-used_at']
        indexes = [
            models.Index(fields=['media_file', 'model_name', 'object_id']),
            models.Index(fields=['used_at']),
        ]
    
    def __str__(self):
        return f"{self.media_file.title} used in {self.model_name} #{self.object_id}"