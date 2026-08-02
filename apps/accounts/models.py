from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator, MinLengthValidator
from django.core.exceptions import ValidationError
from django.urls import reverse
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
            models.Index(fields=['username']),  # Added for faster lookups
        ]
        permissions = [
            ("can_publish_articles", "Can publish articles"),
            ("can_manage_users", "Can manage users"),
            ("can_moderate_comments", "Can moderate comments"),
            ("can_manage_ads", "Can manage advertisements"),
            ("can_view_analytics", "Can view analytics"),
            ("can_manage_settings", "Can manage site settings"),
            ("can_manage_media", "Can manage media files"),  # Added
            ("can_manage_newsletter", "Can manage newsletter"),  # Added
        ]
        ordering = ['-date_joined']  # Added for default ordering
    
    def __str__(self):
        return self.get_full_name() or self.username
    
    def get_full_name(self):
        """Return the full name of the user."""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        """Return the short name of the user."""
        return self.first_name
    
    def get_absolute_url(self):
        """Get the URL for this user's profile."""
        return reverse('accounts:profile', kwargs={'user_id': self.id})
    
    def get_role_display(self):
        """Get the display name for the user's role."""
        return dict(self.ROLE_CHOICES).get(self.role, self.role)
    
    def get_department_display(self):
        """Get the display name for the user's department."""
        return dict(self.DEPARTMENT_CHOICES).get(self.department, self.department)
    
    def clean(self):
        super().clean()
        if self.email:
            self.email = self.email.lower()
        if self.username:
            self.username = self.username.lower()
        
        # Validate email format
        if self.email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', self.email):
            raise ValidationError({'email': 'Enter a valid email address.'})
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def is_editor(self):
        """Check if user has editor privileges."""
        return self.role in ['super_admin', 'admin', 'editor']
    
    @property
    def can_publish(self):
        """Check if user can publish articles."""
        return self.role in ['super_admin', 'admin', 'editor', 'journalist']
    
    @property
    def can_manage_users(self):
        """Check if user can manage other users."""
        return self.role in ['super_admin', 'admin']
    
    @property
    def is_advertiser(self):
        """Check if user is an advertiser."""
        return self.role == 'advertiser'
    
    @property
    def is_journalist(self):
        """Check if user is a journalist."""
        return self.role == 'journalist'
    
    @property
    def is_subscriber(self):
        """Check if user is a subscriber."""
        return self.role == 'subscriber'
    
    @property
    def is_admin(self):
        """Check if user is an admin or super admin."""
        return self.role in ['super_admin', 'admin']
    
    @property
    def is_super_admin(self):
        """Check if user is a super admin."""
        return self.role == 'super_admin'
    
    @property
    def dashboard_url(self):
        """Get the appropriate dashboard URL for this user."""
        if self.role in ['super_admin', 'admin']:
            return reverse('dashboard:admin_dashboard')
        return reverse('dashboard:dashboard')
    
    def lock_account(self, duration_minutes=30):
        """Lock the user account for a specified duration."""
        self.locked_until = timezone.now() + timezone.timedelta(minutes=duration_minutes)
        self.save(update_fields=['locked_until'])
    
    def unlock_account(self):
        """Unlock the user account."""
        self.locked_until = None
        self.failed_login_attempts = 0
        self.save(update_fields=['locked_until', 'failed_login_attempts'])
    
    def increment_failed_attempts(self):
        """Increment failed login attempts and lock if exceeded."""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.lock_account()
        self.save(update_fields=['failed_login_attempts'])
    
    def is_account_locked(self):
        """Check if the account is currently locked."""
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False
    
    def get_remaining_lock_time(self):
        """Get the remaining lock time in minutes."""
        if self.locked_until and self.locked_until > timezone.now():
            remaining = self.locked_until - timezone.now()
            return int(remaining.total_seconds() / 60)
        return 0
    
    def update_reputation(self, score_change):
        """Update user's reputation score."""
        self.reputation_score += score_change
        self.save(update_fields=['reputation_score'])
    
    def increment_articles_written(self):
        """Increment the articles written counter."""
        self.articles_written += 1
        self.save(update_fields=['articles_written'])
    
    def add_views(self, views_count):
        """Add views to the user's total views."""
        self.total_views += views_count
        self.save(update_fields=['total_views'])
    
    @classmethod
    def get_active_users(cls):
        """Get all active users."""
        return cls.objects.filter(is_active=True)
    
    @classmethod
    def get_verified_users(cls):
        """Get all verified users."""
        return cls.objects.filter(is_verified=True)
    
    @classmethod
    def get_by_role(cls, role):
        """Get users by role."""
        return cls.objects.filter(role=role)
    
    @classmethod
    def get_recent_users(cls, limit=10):
        """Get recently joined users."""
        return cls.objects.order_by('-date_joined')[:limit]


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
        ('unsubscribe', 'Unsubscribe'),  # Added
        ('password_change', 'Password Change'),  # Added
        ('profile_update', 'Profile Update'),  # Added
        ('article_created', 'Article Created'),  # Added
        ('article_updated', 'Article Updated'),  # Added
        ('article_deleted', 'Article Deleted'),  # Added
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
            models.Index(fields=['model_name', 'object_id']),  # Added for faster lookups
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"
    
    @classmethod
    def log_activity(cls, user, action, model_name, object_id=None, description='', 
                     ip_address=None, user_agent=None, referer=None):
        """Helper method to create activity logs."""
        return cls.objects.create(
            user=user,
            action=action,
            model_name=model_name,
            object_id=object_id,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            referer=referer
        )
    
    @classmethod
    def get_user_activities(cls, user, limit=50):
        """Get recent activities for a user."""
        return cls.objects.filter(user=user)[:limit]
    
    @classmethod
    def get_recent_activities(cls, limit=100):
        """Get recent activities across all users."""
        return cls.objects.all()[:limit]


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
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='verified_profiles'
    )  # Added
    
    # Additional
    newsletter_subscription = models.BooleanField(default=True)
    marketing_consent = models.BooleanField(default=False)
    terms_accepted = models.BooleanField(default=False)
    terms_accepted_date = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)  # Allow null
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)      # Allow null
    
    class Meta:
        db_table = 'user_profiles'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['country']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        return f"Profile of {self.user.username}"
    
    def get_age(self):
        """Calculate user's age."""
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    def verify_profile(self, verified_by, notes=''):
        """Mark profile as verified."""
        self.is_verified = True
        self.verification_date = timezone.now()
        self.verification_notes = notes
        self.verified_by = verified_by
        self.save(update_fields=['is_verified', 'verification_date', 'verification_notes', 'verified_by'])
        
        # Also update the user's verified status
        self.user.is_verified = True
        self.user.save(update_fields=['is_verified'])
    
    def unverify_profile(self, notes=''):
        """Mark profile as unverified."""
        self.is_verified = False
        self.verification_date = None
        self.verification_notes = notes
        self.verified_by = None
        self.save(update_fields=['is_verified', 'verification_date', 'verification_notes', 'verified_by'])
        
        # Also update the user's verified status
        self.user.is_verified = False
        self.user.save(update_fields=['is_verified'])
    
    def update_preferences(self, preferences):
        """Update user preferences."""
        if preferences:
            self.notification_preferences.update(preferences)
            self.save(update_fields=['notification_preferences'])
    
    def add_expertise(self, expertise):
        """Add an expertise area."""
        if expertise and expertise not in self.expertise_areas:
            self.expertise_areas.append(expertise)
            self.save(update_fields=['expertise_areas'])
    
    def remove_expertise(self, expertise):
        """Remove an expertise area."""
        if expertise in self.expertise_areas:
            self.expertise_areas.remove(expertise)
            self.save(update_fields=['expertise_areas'])
    
    def add_preferred_category(self, category):
        """Add a preferred category."""
        if category and category not in self.preferred_categories:
            self.preferred_categories.append(category)
            self.save(update_fields=['preferred_categories'])
    
    def remove_preferred_category(self, category):
        """Remove a preferred category."""
        if category in self.preferred_categories:
            self.preferred_categories.remove(category)
            self.save(update_fields=['preferred_categories'])
    
    @classmethod
    def get_unverified_profiles(cls):
        """Get all unverified profiles."""
        return cls.objects.filter(is_verified=False)
    
    @classmethod
    def get_verified_profiles(cls):
        """Get all verified profiles."""
        return cls.objects.filter(is_verified=True)