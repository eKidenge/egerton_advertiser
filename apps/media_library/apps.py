from django.contrib import admin
from django.utils.html import format_html
from .models import MediaFile, MediaTag, MediaCategory, MediaFileTag, MediaFileCategory, MediaUsage

@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ('title_preview', 'file_type', 'file_size', 'uploaded_by', 'status', 'usage_count', 'created_at')
    list_filter = ('file_type', 'status', 'created_at')
    search_fields = ('title', 'description', 'alt_text', 'uploaded_by__username')
    readonly_fields = ('file_size', 'mime_type', 'file_hash', 'usage_count', 'last_used', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'alt_text')
        }),
        ('File', {
            'fields': ('file', 'file_type', 'file_size', 'mime_type', 'file_hash')
        }),
        ('Metadata', {
            'fields': ('width', 'height', 'duration', 'metadata')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Thumbnails', {
            'fields': ('thumbnail_small', 'thumbnail_medium', 'thumbnail_large')
        }),
        ('Usage', {
            'fields': ('usage_count', 'last_used')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def title_preview(self, obj):
        if obj.file_type in ['image', 'video']:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />',
                obj.get_thumbnail_url('small')
            )
        return obj.title[:50]
    title_preview.short_description = 'Preview'

@admin.register(MediaTag)
class MediaTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(MediaCategory)
class MediaCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(MediaUsage)
class MediaUsageAdmin(admin.ModelAdmin):
    list_display = ('media_file', 'model_name', 'object_id', 'field_name', 'used_by', 'used_at')
    list_filter = ('model_name', 'used_at')
    search_fields = ('media_file__title', 'model_name')