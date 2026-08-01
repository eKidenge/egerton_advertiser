from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class SiteSetting(models.Model):
    SETTING_TYPES = (
        ('general', 'General'),
        ('appearance', 'Appearance'),
        ('seo', 'SEO'),
        ('email', 'Email'),
        ('social_media', 'Social Media'),
        ('advertisement', 'Advertisement'),
        ('security', 'Security'),
        ('performance', 'Performance'),
        ('integration', 'Integration'),
    )
    
    # Basic
    category = models.CharField(max_length=20, choices=SETTING_TYPES)
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    
    # Metadata
    is_public = models.BooleanField(default=False)
    is_encrypted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'site_settings'
        ordering = ['category', 'key']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['key']),
        ]
    
    def __str__(self):
        return f"{self.category} - {self.key}"

class ThemeSetting(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='theme_settings',
        null=True,
        blank=True
    )
    is_global = models.BooleanField(default=False)
    
    # Colors
    primary_color = models.CharField(max_length=7, default='#007bff')
    secondary_color = models.CharField(max_length=7, default='#6c757d')
    success_color = models.CharField(max_length=7, default='#28a745')
    danger_color = models.CharField(max_length=7, default='#dc3545')
    warning_color = models.CharField(max_length=7, default='#ffc107')
    info_color = models.CharField(max_length=7, default='#17a2b8')
    light_color = models.CharField(max_length=7, default='#f8f9fa')
    dark_color = models.CharField(max_length=7, default='#343a40')
    
    # Fonts
    font_family = models.CharField(max_length=100, default='system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif')
    font_size = models.CharField(max_length=10, default='16px')
    
    # Layout
    layout = models.CharField(
        max_length=20,
        choices=(
            ('boxed', 'Boxed'),
            ('full_width', 'Full Width'),
        ),
        default='full_width'
    )
    sidebar_position = models.CharField(
        max_length=20,
        choices=(
            ('left', 'Left'),
            ('right', 'Right'),
        ),
        default='left'
    )
    
    # Custom CSS
    custom_css = models.TextField(blank=True)
    custom_js = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'theme_settings'
    
    def __str__(self):
        if self.user:
            return f"Theme settings for {self.user.username}"
        return "Global theme settings"