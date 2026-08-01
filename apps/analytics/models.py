from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class AnalyticsEvent(models.Model):
    EVENT_TYPES = (
        ('page_view', 'Page View'),
        ('article_view', 'Article View'),
        ('click', 'Click'),
        ('scroll', 'Scroll'),
        ('time_on_page', 'Time on Page'),
        ('conversion', 'Conversion'),
        ('download', 'Download'),
        ('search', 'Search'),
    )
    
    # Event information
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    event_name = models.CharField(max_length=100, blank=True)
    event_value = models.FloatField(null=True, blank=True)
    
    # Target
    url = models.URLField()
    path = models.CharField(max_length=500)
    referer = models.URLField(blank=True)
    title = models.CharField(max_length=200, blank=True)
    
    # User
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='analytics_events'
    )
    session_id = models.CharField(max_length=100, blank=True)
    user_id = models.CharField(max_length=100, blank=True)
    
    # Device and browser
    user_agent = models.TextField(blank=True)
    browser = models.CharField(max_length=50, blank=True)
    browser_version = models.CharField(max_length=20, blank=True)
    os = models.CharField(max_length=50, blank=True)
    os_version = models.CharField(max_length=20, blank=True)
    device_type = models.CharField(max_length=20, blank=True)
    device_brand = models.CharField(max_length=50, blank=True)
    device_model = models.CharField(max_length=50, blank=True)
    
    # Location
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    # Additional data
    data = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'analytics_events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['url']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['session_id']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.path} - {self.created_at}"

class AnalyticsPageView(models.Model):
    """Aggregated page view statistics"""
    url = models.URLField()
    path = models.CharField(max_length=500)
    title = models.CharField(max_length=200, blank=True)
    
    # Article reference
    article = models.ForeignKey(
        'articles.Article',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='analytics_views'
    )
    
    # Counts
    views = models.PositiveIntegerField(default=0)
    unique_views = models.PositiveIntegerField(default=0)
    avg_time_on_page = models.FloatField(default=0)
    bounce_count = models.PositiveIntegerField(default=0)
    
    # Dates
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analytics_page_views'
        unique_together = ['url', 'date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['path']),
            models.Index(fields=['article', 'date']),
        ]
    
    def __str__(self):
        return f"{self.path} - {self.date} - {self.views} views"

class AnalyticsTrafficSource(models.Model):
    """Track where traffic comes from"""
    SOURCE_TYPES = (
        ('direct', 'Direct'),
        ('search', 'Search Engine'),
        ('social', 'Social Media'),
        ('referral', 'Referral'),
        ('email', 'Email'),
        ('ad', 'Advertisement'),
        ('other', 'Other'),
    )
    
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    source_name = models.CharField(max_length=200, blank=True)
    source_url = models.URLField(blank=True)
    
    # Counts
    visits = models.PositiveIntegerField(default=0)
    unique_visits = models.PositiveIntegerField(default=0)
    conversions = models.PositiveIntegerField(default=0)
    
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analytics_traffic_sources'
        unique_together = ['source_type', 'source_name', 'date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['source_type']),
        ]
    
    def __str__(self):
        return f"{self.source_type} - {self.source_name} - {self.date}"

class AnalyticsRealTime(models.Model):
    """Real-time visitor tracking"""
    session_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    current_page = models.URLField()
    current_path = models.CharField(max_length=500)
    referer = models.URLField(blank=True)
    
    # Device info
    user_agent = models.TextField(blank=True)
    device_type = models.CharField(max_length=20, blank=True)
    
    # Location
    ip_address = models.GenericIPAddressField()
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analytics_realtime'
        indexes = [
            models.Index(fields=['last_activity']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"{self.session_id} - {self.current_path}"