from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import EmailValidator, MinLengthValidator
from ckeditor.fields import RichTextField
from apps.articles.models import Article

User = get_user_model()

class Subscriber(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('unsubscribed', 'Unsubscribed'),
        ('bounced', 'Bounced'),
        ('spam', 'Marked as Spam'),
    )
    
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        help_text="Subscriber's email address"
    )
    name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Subscriber's full name"
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # User association
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subscribers'
    )
    
    # Preferences
    categories = models.ManyToManyField(
        'categories.Category',
        blank=True,
        related_name='subscribers',
        help_text="Categories this subscriber wants to receive"
    )
    tags = models.ManyToManyField(
        'tags.Tag',
        blank=True,
        related_name='subscribers',
        help_text="Tags this subscriber wants to receive"
    )
    frequency = models.CharField(
        max_length=20,
        choices=(
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('instant', 'Instant'),
        ),
        default='daily',
        help_text="How often to send newsletters"
    )
    
    # Tracking
    confirmation_token = models.CharField(max_length=100, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    confirmed_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # Statistics
    opens = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    unsubscribes = models.PositiveIntegerField(default=0)
    
    # Sources
    source = models.CharField(
        max_length=100,
        blank=True,
        help_text="Where this subscriber came from (e.g., website, social media, manual)"
    )
    source_url = models.URLField(blank=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referer = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sent = models.DateTimeField(null=True, blank=True)
    last_opened = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'subscribers'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['frequency', 'status']),
        ]
    
    def __str__(self):
        return f"{self.email} ({self.status})"
    
    def confirm(self, ip=None):
        self.status = 'active'
        self.confirmed_at = timezone.now()
        self.confirmed_ip = ip
        self.save(update_fields=['status', 'confirmed_at', 'confirmed_ip'])
    
    def unsubscribe(self):
        self.status = 'unsubscribed'
        self.save(update_fields=['status'])
    
    def record_open(self):
        self.opens += 1
        self.last_opened = timezone.now()
        self.save(update_fields=['opens', 'last_opened'])
    
    def record_click(self):
        self.clicks += 1
        self.save(update_fields=['clicks'])

class Newsletter(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('scheduled', 'Scheduled'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )
    
    TEMPLATE_CHOICES = (
        ('default', 'Default'),
        ('minimal', 'Minimal'),
        ('featured', 'Featured'),
        ('digest', 'Digest'),
        ('custom', 'Custom'),
    )
    
    # Basic information
    subject = models.CharField(
        max_length=200,
        help_text="Email subject line"
    )
    preview_text = models.CharField(
        max_length=200,
        blank=True,
        help_text="Preview text shown in email clients"
    )
    
    # Content
    content = RichTextField(
        help_text="Email content - HTML supported"
    )
    plain_text = models.TextField(
        blank=True,
        help_text="Plain text version of the email"
    )
    
    # Template
    template = models.CharField(
        max_length=20,
        choices=TEMPLATE_CHOICES,
        default='default'
    )
    template_custom = models.TextField(
        blank=True,
        help_text="Custom HTML template"
    )
    
    # Articles
    articles = models.ManyToManyField(
        Article,
        blank=True,
        related_name='newsletters',
        help_text="Articles to include in this newsletter"
    )
    
    # Scheduling
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_for = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Audience
    subscribers_count = models.PositiveIntegerField(default=0)
    target_categories = models.ManyToManyField(
        'categories.Category',
        blank=True,
        related_name='newsletters',
        help_text="Send only to subscribers of these categories"
    )
    
    # Tracking
    opens_count = models.PositiveIntegerField(default=0)
    clicks_count = models.PositiveIntegerField(default=0)
    unsubscribe_count = models.PositiveIntegerField(default=0)
    bounce_count = models.PositiveIntegerField(default=0)
    spam_reports = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_newsletters'
    )
    sent_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_newsletters'
    )
    
    # Headers
    from_email = models.EmailField(blank=True)
    from_name = models.CharField(max_length=200, blank=True)
    reply_to = models.EmailField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'newsletters'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'scheduled_for']),
            models.Index(fields=['created_by']),
            models.Index(fields=['sent_at']),
        ]
    
    def __str__(self):
        return f"{self.subject} - {self.status}"
    
    def send(self, test=False):
        """Send the newsletter to all active subscribers"""
        if self.status == 'sent':
            return False
        
        # Get active subscribers
        subscribers = Subscriber.objects.filter(status='active')
        
        # Filter by categories
        if self.target_categories.exists():
            subscribers = subscribers.filter(categories__in=self.target_categories).distinct()
        
        self.subscribers_count = subscribers.count()
        
        if self.subscribers_count == 0:
            self.status = 'failed'
            self.save()
            return False
        
        self.status = 'sending'
        self.save()
        
        # In production, this would use a bulk email service like SendGrid, MailChimp, etc.
        # For now, we'll just mark it as sent
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        from django.conf import settings
        
        try:
            # Send to each subscriber (in production, use bulk sending)
            for subscriber in subscribers[:10]:  # Limit for demo
                html_content = render_to_string('newsletter/emails/newsletter.html', {
                    'newsletter': self,
                    'subscriber': subscriber,
                    'unsubscribe_link': subscriber.email,
                })
                plain_content = strip_tags(html_content)
                
                send_mail(
                    self.subject,
                    plain_content,
                    settings.DEFAULT_FROM_EMAIL,
                    [subscriber.email],
                    html_message=html_content,
                    fail_silently=True
                )
            
            self.status = 'sent'
            self.sent_at = timezone.now()
            self.save()
            return True
        except Exception as e:
            self.status = 'failed'
            self.save()
            print(f"Failed to send newsletter: {e}")
            return False

class NewsletterTracking(models.Model):
    ACTION_CHOICES = (
        ('open', 'Opened'),
        ('click', 'Clicked'),
        ('unsubscribe', 'Unsubscribed'),
        ('bounce', 'Bounced'),
        ('spam', 'Marked as Spam'),
    )
    
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE, related_name='tracking')
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name='tracking')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referer = models.URLField(blank=True)
    link = models.URLField(blank=True, help_text="Link clicked (if action is 'click')")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'newsletter_tracking'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['newsletter', 'action']),
            models.Index(fields=['subscriber']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.subscriber.email} - {self.action} - {self.created_at}"