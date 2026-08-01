from django.contrib import admin
from .models import Tag

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'article_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('article_count', 'total_views', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'color')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Statistics', {
            'fields': ('article_count', 'total_views', 'created_at', 'updated_at')
        }),
    )