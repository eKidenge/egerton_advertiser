from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator, MinLengthValidator
from django.core.exceptions import ValidationError
import re


class User(AbstractUser):
    ROLE_CHOICES = (
        ('super_admin', 'Super Administrator'),
        ('admin', 'Administrator'),
        ('editor', 'Editor'),
        ('journalist', 'Journalist'),
        ('subscriber', 'Subscriber'),
        ('advertiser', 'Advertiser'),
    )
    
    DEPARTMENT_CHOICES = (
        ('news', 'News Department'),
        ('politics', 'Political Desk'),
        ('business', 'Business Desk'),
        ('sports', 'Sports Desk'),
        ('entertainment', 'Entertainment Desk'),
        ('editorial', 'Editorial Board'),
        ('advertising', 'Advertising Department'),
        ('administration', 'Administration'),
    )
    
    # Core fields
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters.'
            ),
            MinLengthValidator(3)
        ],
        error_messages={
            'unique': 'A user with that username already exists.',
        }
    )
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    
    # Profile fields
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='subscriber')
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/%Y/%m/', blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    
    # Social media
    social_links = models.JSONField(default=dict, blank=True)
    
    # Status fields
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # Timestamps
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Professional details
    employee_id = models.CharField(max_length=20, blank=True, unique=True, null=True)
    hire_date = models.DateField(null=True, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    
    # Notifications and preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Security
    failed_login_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    two_factor_enabled = models.BooleanField(default=False)
    
    # Meta fields for journalists
    articles_written = models.PositiveIntegerField(default=0)
    total_views = models.PositiveIntegerField(default=0)
    reputation_score = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['department']),
            models.Index(fields=['is_active', 'is_verified']),
        ]
        permissions = [
            ("can_publish_articles", "Can publish articles"),
            ("can_manage_users", "Can manage users"),
            ("can_moderate_comments", "Can moderate comments"),
            ("can_manage_ads", "Can manage advertisements"),
            ("can_view_analytics", "Can view analytics"),
            ("can_manage_settings", "Can manage site settings"),
        ]
    
    def __str__(self):
        return self.get_full_name() or self.username
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name
    
    def clean(self):
        super().clean()
        if self.email:
            self.email = self.email.lower()
        if self.username:
            self.username = self.username.lower()
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def is_editor(self):
        return self.role in ['super_admin', 'admin', 'editor']
    
    @property
    def can_publish(self):
        return self.role in ['super_admin', 'admin', 'editor', 'journalist']
    
    @property
    def can_manage_users(self):
        return self.role in ['super_admin', 'admin']
    
    @property
    def is_advertiser(self):
        return self.role == 'advertiser'
    
    def lock_account(self, duration_minutes=30):
        self.locked_until = timezone.now() + timezone.timedelta(minutes=duration_minutes)
        self.save(update_fields=['locked_until'])
    
    def unlock_account(self):
        self.locked_until = None
        self.failed_login_attempts = 0
        self.save(update_fields=['locked_until', 'failed_login_attempts'])
    
    def increment_failed_attempts(self):
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.lock_account()
        self.save(update_fields=['failed_login_attempts'])
    
    def is_account_locked(self):
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False


class UserActivityLog(models.Model):
    ACTION_CHOICES = (
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('publish', 'Publish'),
        ('view', 'View'),
        ('comment', 'Comment'),
        ('share', 'Share'),
        ('download', 'Download'),
        ('subscribe', 'Subscribe'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referer = models.URLField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_activity_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"


class UserProfile(models.Model):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal information
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Professional
    organization = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    expertise_areas = models.JSONField(default=list, blank=True)
    
    # Preferences
    preferred_categories = models.JSONField(default=list, blank=True)
    notification_preferences = models.JSONField(default=dict, blank=True)
    
    # Verification
    id_document = models.FileField(upload_to='verification/documents/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True)
    
    # Additional
    newsletter_subscription = models.BooleanField(default=True)
    marketing_consent = models.BooleanField(default=False)
    terms_accepted = models.BooleanField(default=False)
    terms_accepted_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"Profile of {self.user.username}"