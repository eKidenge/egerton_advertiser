from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from apps.articles.models import Article

User = get_user_model()

class Advertisement(models.Model):
    POSITION_CHOICES = (
        ('header', 'Header Banner'),
        ('sidebar', 'Sidebar'),
        ('in_article', 'In-Article'),
        ('between_posts', 'Between Posts'),
        ('footer', 'Footer'),
        ('featured_section', 'Featured Section'),
        ('popup', 'Popup'),
        ('video', 'Video Ad'),
        ('sponsored', 'Sponsored Content'),
    )
    
    SIZE_CHOICES = (
        ('leaderboard', '728x90 - Leaderboard'),
        ('banner', '468x60 - Banner'),
        ('half_banner', '234x60 - Half Banner'),
        ('square', '250x250 - Square'),
        ('small_square', '200x200 - Small Square'),
        ('button', '125x125 - Button'),
        ('medium_rectangle', '300x250 - Medium Rectangle'),
        ('large_rectangle', '336x280 - Large Rectangle'),
        ('skyscraper', '120x600 - Skyscraper'),
        ('wide_skyscraper', '160x600 - Wide Skyscraper'),
        ('half_page', '300x600 - Half Page'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('pending', 'Pending Approval'),
        ('scheduled', 'Scheduled'),
        ('paused', 'Paused'),
        ('expired', 'Expired'),
        ('rejected', 'Rejected'),
        ('draft', 'Draft'),
    )
    
    # Basic information
    title = models.CharField(
        max_length=200,
        help_text="Ad title for internal reference"
    )
    description = models.TextField(max_length=500, blank=True)
    
    # Media
    image = models.ImageField(
        upload_to='ads/%Y/%m/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'webp'])],
        help_text="Ad image (supported formats: JPG, PNG, GIF, WEBP)"
    )
    image_alt = models.CharField(max_length=200, blank=True)
    video_url = models.URLField(blank=True, help_text="URL for video ads")
    
    # Links
    link_url = models.URLField(help_text="URL users go to when clicking the ad")
    link_target = models.CharField(
        max_length=10,
        choices=(
            ('_self', 'Same Window'),
            ('_blank', 'New Window'),
        ),
        default='_blank'
    )
    
    # Position and size
    position = models.CharField(max_length=20, choices=POSITION_CHOICES)
    size = models.CharField(max_length=20, choices=SIZE_CHOICES)
    
    # Advertiser information
    advertiser = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ads',
        help_text="Advertiser who owns this ad"
    )
    company_name = models.CharField(max_length=200)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    
    # Schedule
    start_date = models.DateTimeField(help_text="When the ad should start showing")
    end_date = models.DateTimeField(help_text="When the ad should stop showing")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Targeting
    targeted_categories = models.ManyToManyField(
        'categories.Category',
        blank=True,
        related_name='ads',
        help_text="Show ad only on these categories (leave blank for all)"
    )
    targeted_articles = models.ManyToManyField(
        Article,
        blank=True,
        related_name='ads',
        help_text="Show ad only on these specific articles"
    )
    target_countries = models.JSONField(default=list, blank=True)
    target_cities = models.JSONField(default=list, blank=True)
    
    # Budget and pricing
    budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Total budget for this ad campaign"
    )
    cost_per_click = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Cost per click (CPC)"
    )
    cost_per_impression = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Cost per 1000 impressions (CPM)"
    )
    
    # Performance tracking
    views_count = models.PositiveIntegerField(default=0)
    clicks_count = models.PositiveIntegerField(default=0)
    unique_views = models.PositiveIntegerField(default=0)
    unique_clicks = models.PositiveIntegerField(default=0)
    conversion_count = models.PositiveIntegerField(default=0)
    
    # Limits
    max_clicks = models.PositiveIntegerField(
        default=0,
        help_text="Maximum number of clicks (0 for unlimited)"
    )
    max_impressions = models.PositiveIntegerField(
        default=0,
        help_text="Maximum number of impressions (0 for unlimited)"
    )
    daily_limit = models.PositiveIntegerField(
        default=0,
        help_text="Daily impression limit (0 for unlimited)"
    )
    
    # Priority
    priority = models.PositiveIntegerField(
        default=0,
        help_text="Higher priority ads show first (0-100)"
    )
    
    class Meta:
        db_table = 'advertisements'
        ordering = ['-priority', 'views_count']
        indexes = [
            models.Index(fields=['position', 'status']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['advertiser', 'status']),
            models.Index(fields=['priority', 'views_count']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.position} ({self.status})"
    
    def save(self, *args, **kwargs):
        # Auto-update status based on dates
        now = timezone.now()
        if self.status == 'active':
            if now < self.start_date:
                self.status = 'scheduled'
            elif now > self.end_date:
                self.status = 'expired'
        super().save(*args, **kwargs)
    
    def is_active(self):
        now = timezone.now()
        return (self.status == 'active' and 
                self.start_date <= now <= self.end_date and
                (self.max_impressions == 0 or self.views_count < self.max_impressions))
    
    def can_show(self):
        if not self.is_active():
            return False
        
        # Check daily limit
        if self.daily_limit > 0:
            today = timezone.now().date()
            daily_views = AdvertisementView.objects.filter(
                ad=self,
                viewed_at__date=today
            ).count()
            if daily_views >= self.daily_limit:
                return False
        
        return True
    
    def increment_view(self, user=None, request=None):
        if not self.can_show():
            return False
        
        self.views_count += 1
        self.save(update_fields=['views_count'])
        
        # Log view
        view = AdvertisementView.objects.create(
            ad=self,
            user=user,
            ip_address=request.META.get('REMOTE_ADDR') if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT', '') if request else '',
            referer=request.META.get('HTTP_REFERER', '') if request else '',
            session_id=request.session.session_key if request else None,
        )
        
        return True
    
    def increment_click(self, user=None, request=None):
        self.clicks_count += 1
        self.save(update_fields=['clicks_count'])
        
        # Log click
        click = AdvertisementClick.objects.create(
            ad=self,
            user=user,
            ip_address=request.META.get('REMOTE_ADDR') if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT', '') if request else '',
            referer=request.META.get('HTTP_REFERER', '') if request else '',
            session_id=request.session.session_key if request else None,
        )
        
        return True

class AdvertisementView(models.Model):
    ad = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referer = models.URLField(blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'ad_views'
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['ad', 'viewed_at']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"View of {self.ad.title} at {self.viewed_at}"

class AdvertisementClick(models.Model):
    ad = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name='clicks')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    clicked_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referer = models.URLField(blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'ad_clicks'
        ordering = ['-clicked_at']
        indexes = [
            models.Index(fields=['ad', 'clicked_at']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"Click on {self.ad.title} at {self.clicked_at}"