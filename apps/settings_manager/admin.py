from django.contrib import admin
from .models import SiteSetting, ThemeSetting

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'category', 'value_preview', 'is_public', 'updated_at')
    list_filter = ('category', 'is_public', 'created_at')
    search_fields = ('key', 'value', 'description')
    ordering = ('category', 'key')
    
    def value_preview(self, obj):
        return obj.value[:50] + ('...' if len(obj.value) > 50 else '')
    value_preview.short_description = 'Value'

@admin.register(ThemeSetting)
class ThemeSettingAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_global', 'primary_color', 'layout', 'updated_at')
    list_filter = ('is_global', 'layout')
    search_fields = ('user__username',)