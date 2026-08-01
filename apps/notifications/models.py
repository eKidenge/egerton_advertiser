from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('mention', 'Mention'),
        ('comment', 'Comment'),
        ('like', 'Like'),
        ('share', 'Share'),
        ('follow', 'Follow'),
        ('article_published', 'Article Published'),
        ('ad_approved', 'Ad Approved'),
        ('subscription', 'Subscription'),
    )
    
    # Target user
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    # Notification type and content
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Link
    link = models.URLField(blank=True)
    link_text = models.CharField(max_length=100, blank=True)
    
    # Actor (who triggered the notification)
    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='triggered_notifications'
    )
    
    # Object reference
    object_type = models.CharField(max_length=100, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    is_seen = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Priority
    priority = models.PositiveIntegerField(default=0)
    
    # Channels
    email_sent = models.BooleanField(default=False)
    push_sent = models.BooleanField(default=False)
    sms_sent = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title} - {self.created_at}"
    
    def mark_as_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=['is_read', 'read_at'])
    
    def mark_as_seen(self):
        self.is_seen = True
        self.save(update_fields=['is_seen'])
    
    @classmethod
    def create_notification(cls, user, notification_type, title, message, **kwargs):
        return cls.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            **kwargs
        )

class NotificationPreference(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    # Email notifications
    email_comments = models.BooleanField(default=True)
    email_likes = models.BooleanField(default=True)
    email_mentions = models.BooleanField(default=True)
    email_article_published = models.BooleanField(default=True)
    email_subscriptions = models.BooleanField(default=True)
    email_digest = models.BooleanField(default=True)
    
    # Push notifications
    push_comments = models.BooleanField(default=True)
    push_likes = models.BooleanField(default=True)
    push_mentions = models.BooleanField(default=True)
    push_article_published = models.BooleanField(default=True)
    push_ads = models.BooleanField(default=True)
    
    # In-app notifications
    in_app_comments = models.BooleanField(default=True)
    in_app_likes = models.BooleanField(default=True)
    in_app_mentions = models.BooleanField(default=True)
    in_app_article_published = models.BooleanField(default=True)
    in_app_ads = models.BooleanField(default=True)
    
    # Digest settings
    digest_frequency = models.CharField(
        max_length=20,
        choices=(
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('never', 'Never'),
        ),
        default='daily'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
    
    def __str__(self):
        return f"Preferences for {self.user.username}"