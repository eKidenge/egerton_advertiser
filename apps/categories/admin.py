from django.contrib import admin
from django.utils.html import format_html
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name_preview', 'slug', 'parent', 'order', 'article_count', 
                   'is_active', 'is_featured', 'created_at')
    list_filter = ('is_active', 'is_featured', 'parent', 'created_at')
    search_fields = ('name', 'description', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('article_count', 'total_views', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'icon', 'color')
        }),
        ('Parent & Ordering', {
            'fields': ('parent', 'order')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Media', {
            'fields': ('image', 'image_alt')
        }),
        ('SEO', {
            'fields': ('seo_title', 'seo_description', 'seo_keywords')
        }),
        ('Statistics', {
            'fields': ('article_count', 'total_views', 'created_at', 'updated_at')
        }),
    )
    
    def name_preview(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            obj.get_absolute_url(),
            obj.name
        )
    name_preview.short_description = 'Category Name'
    
    actions = ['activate_categories', 'deactivate_categories']
    
    def activate_categories(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} categories activated.')
    activate_categories.short_description = 'Activate selected categories'
    
    def deactivate_categories(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} categories deactivated.')
    deactivate_categories.short_description = 'Deactivate selected categories'