from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class DashboardWidget(models.Model):
    WIDGET_TYPES = (
        ('statistics', 'Statistics'),
        ('chart', 'Chart'),
        ('recent_activity', 'Recent Activity'),
        ('recent_articles', 'Recent Articles'),
        ('pending_comments', 'Pending Comments'),
        ('ad_performance', 'Ad Performance'),
        ('quick_actions', 'Quick Actions'),
        ('news_feed', 'News Feed'),
        ('calendar', 'Calendar'),
        ('custom', 'Custom'),
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dashboard_widgets'
    )
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    title = models.CharField(max_length=100)
    position = models.PositiveIntegerField(default=0)
    column = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(4)])
    width = models.PositiveIntegerField(default=12, validators=[MinValueValidator(4), MaxValueValidator(12)])
    settings = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dashboard_widgets'
        ordering = ['column', 'position']
        unique_together = ['user', 'widget_type', 'column']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"

class DashboardPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dashboard_preferences')
    layout = models.JSONField(default=dict)
    theme = models.CharField(max_length=20, default='light')
    default_view = models.CharField(max_length=50, default='grid')
    refresh_interval = models.PositiveIntegerField(default=300)  # seconds
    notifications_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dashboard_preferences'
    
    def __str__(self):
        return f"Preferences for {self.user.username}"

class DashboardMetric(models.Model):
    METRIC_TYPES = (
        ('article_count', 'Article Count'),
        ('view_count', 'View Count'),
        ('comment_count', 'Comment Count'),
        ('ad_revenue', 'Ad Revenue'),
        ('user_growth', 'User Growth'),
        ('engagement_rate', 'Engagement Rate'),
        ('bounce_rate', 'Bounce Rate'),
        ('conversion_rate', 'Conversion Rate'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboard_metrics')
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    value = models.FloatField(default=0)
    previous_value = models.FloatField(default=0)
    change_percentage = models.FloatField(default=0)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'dashboard_metrics'
        ordering = ['-date']
        unique_together = ['user', 'metric_type', 'date']
    
    def __str__(self):
        return f"{self.user.username} - {self.metric_type} - {self.date}"
    
    def save(self, *args, **kwargs):
        if self.previous_value > 0:
            self.change_percentage = ((self.value - self.previous_value) / self.previous_value) * 100
        super().save(*args, **kwargs)

class QuickAction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quick_actions')
    title = models.CharField(max_length=100)
    url = models.CharField(max_length=200)
    icon = models.CharField(max_length=50)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'quick_actions'
        ordering = ['order']
        unique_together = ['user', 'url']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"

class DashboardActivityFeed(models.Model):
    ACTIVITY_TYPES = (
        ('article_created', 'Article Created'),
        ('article_published', 'Article Published'),
        ('comment_received', 'Comment Received'),
        ('ad_clicked', 'Ad Clicked'),
        ('user_registered', 'User Registered'),
        ('ad_purchased', 'Ad Purchased'),
        ('subscriber_added', 'Subscriber Added'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_feed')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    message = models.TextField()
    link = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'dashboard_activity_feed'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.created_at}"