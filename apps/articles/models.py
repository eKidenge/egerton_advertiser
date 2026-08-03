from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinLengthValidator, MaxLengthValidator
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from apps.categories.models import Category
from apps.tags.models import Tag
import re

User = get_user_model()

class Article(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('published', 'Published'),
        ('scheduled', 'Scheduled'),
        ('archived', 'Archived'),
        ('trash', 'Trash'),
    )
    
    PUBLISH_NOW = 'publish_now'
    SCHEDULE = 'schedule'
    PUBLISH_OPTIONS = (
        (PUBLISH_NOW, 'Publish Now'),
        (SCHEDULE, 'Schedule'),
    )
    
    # Core content fields
    title = models.CharField(
        max_length=300,
        validators=[MinLengthValidator(5)],
        help_text="Enter a compelling title for your article"
    )
    slug = models.SlugField(
        max_length=350,
        unique=True,
        blank=True,
        help_text="URL-friendly version of the title"
    )
    excerpt = models.TextField(
        max_length=500,
        blank=True,
        help_text="A short summary of the article. Leave blank to auto-generate from content."
    )
    content = RichTextUploadingField(
        config_name='default',
        help_text="Write your article content here"
    )
    
    # Media
    featured_image = models.ImageField(
        upload_to='articles/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text="Main image for the article"
    )
    featured_image_alt = models.CharField(
        max_length=200,
        blank=True,
        help_text="Alternative text for the featured image"
    )
    featured_image_caption = models.CharField(
        max_length=200,
        blank=True,
        help_text="Caption for the featured image"
    )
    
    # Relationships
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='articles',
        help_text="Author of the article"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='articles',
        help_text="Primary category for the article"
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='articles',
        help_text="Tags to categorize the article"
    )
    
    # Status and dates
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    publish_option = models.CharField(
        max_length=20,
        choices=PUBLISH_OPTIONS,
        default=PUBLISH_NOW
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    views_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    bookmarks_count = models.PositiveIntegerField(default=0)
    reading_time = models.PositiveSmallIntegerField(default=0)
    
    # Featured and breaking
    is_featured = models.BooleanField(default=False)
    featured_order = models.PositiveIntegerField(default=0)
    is_breaking = models.BooleanField(default=False)
    is_exclusive = models.BooleanField(default=False)
    is_editor_pick = models.BooleanField(default=False)
    
    # SEO
    seo_title = models.CharField(max_length=150, blank=True)
    seo_description = models.CharField(max_length=200, blank=True)
    seo_keywords = models.CharField(max_length=200, blank=True)
    canonical_url = models.URLField(blank=True)
    
    # Custom fields
    custom_css = models.TextField(blank=True)
    custom_js = models.TextField(blank=True)
    extra_meta = models.JSONField(default=dict, blank=True)
    
    # Related articles
    related_articles = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        through='RelatedArticle'
    )
    
    # Meta fields
    meta_description = models.TextField(max_length=300, blank=True)
    meta_keywords = models.CharField(max_length=300, blank=True)
    
    # Reference
    reference_url = models.URLField(blank=True)
    reference_text = models.CharField(max_length=200, blank=True)
    
    class Meta:
        db_table = 'articles'
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['slug']),
            models.Index(fields=['author', 'status']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['is_featured', 'featured_order']),
            models.Index(fields=['is_breaking']),
            models.Index(fields=['created_at']),
            models.Index(fields=['views_count']),
        ]
        permissions = [
            ("can_publish_article", "Can publish articles"),
            ("can_edit_any_article", "Can edit any article"),
            ("can_delete_any_article", "Can delete any article"),
            ("can_feature_articles", "Can feature articles"),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate slug from title
            self.slug = slugify(self.title)
            
            # Remove any special characters that aren't allowed in URLs
            # Keep only alphanumeric, hyphens, and underscores
            self.slug = re.sub(r'[^a-zA-Z0-9_-]', '', self.slug)
            
            # If slug is empty after cleaning, use a fallback
            if not self.slug:
                self.slug = f"article-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            
            # Ensure unique slug
            original_slug = self.slug
            counter = 1
            while Article.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        # Auto-generate excerpt if not provided
        if not self.excerpt and self.content:
            from django.utils.html import strip_tags
            plain_text = strip_tags(self.content)
            self.excerpt = plain_text[:300] + ('...' if len(plain_text) > 300 else '')
        
        # Calculate reading time (average 200 words per minute)
        if self.content:
            from django.utils.html import strip_tags
            plain_text = strip_tags(self.content)
            word_count = len(plain_text.split())
            self.reading_time = max(1, round(word_count / 200))
        
        # Set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        
        if self.status == 'archived' and not self.archived_at:
            self.archived_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('articles:detail', kwargs={'slug': self.slug})
    
    @property
    def is_published(self):
        return self.status == 'published' and self.published_at
    
    @property
    def word_count(self):
        from django.utils.html import strip_tags
        plain_text = strip_tags(self.content)
        return len(plain_text.split())
    
    def increment_view(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def increment_share(self):
        self.shares_count += 1
        self.save(update_fields=['shares_count'])
    
    def increment_like(self):
        self.likes_count += 1
        self.save(update_fields=['likes_count'])


class ArticleVersion(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    title = models.CharField(max_length=300)
    content = models.TextField()
    excerpt = models.TextField(max_length=500, blank=True)
    slug = models.SlugField(max_length=350)
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    modified_at = models.DateTimeField(auto_now_add=True)
    change_notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'article_versions'
        ordering = ['-version_number']
        unique_together = ['article', 'version_number']
    
    def __str__(self):
        return f"Version {self.version_number} of {self.article.title}"


class RelatedArticle(models.Model):
    source = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='source_relations')
    target = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='target_relations')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'related_articles'
        ordering = ['order']
        unique_together = ['source', 'target']
    
    def __str__(self):
        return f"{self.source.title} → {self.target.title}"


class ArticleStatistics(models.Model):
    article = models.OneToOneField(Article, on_delete=models.CASCADE, related_name='statistics')
    
    # Views by time
    views_today = models.PositiveIntegerField(default=0)
    views_week = models.PositiveIntegerField(default=0)
    views_month = models.PositiveIntegerField(default=0)
    views_year = models.PositiveIntegerField(default=0)
    
    # Engagement
    comments_count = models.PositiveIntegerField(default=0)
    avg_reading_time = models.FloatField(default=0)
    bounce_rate = models.FloatField(default=0)
    
    # Social media
    twitter_shares = models.PositiveIntegerField(default=0)
    facebook_shares = models.PositiveIntegerField(default=0)
    linkedin_shares = models.PositiveIntegerField(default=0)
    whatsapp_shares = models.PositiveIntegerField(default=0)
    
    # Performance
    click_through_rate = models.FloatField(default=0)
    conversion_rate = models.FloatField(default=0)
    engagement_score = models.FloatField(default=0)
    
    # Last updated
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'article_statistics'
    
    def __str__(self):
        return f"Statistics for {self.article.title}"


class ArticleSchedule(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='schedules')
    scheduled_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=(
        ('pending', 'Pending'),
        ('published', 'Published'),
        ('failed', 'Failed'),
    ), default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    executed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'article_schedules'
        ordering = ['scheduled_date']
    
    def __str__(self):
        return f"Schedule for {self.article.title} at {self.scheduled_date}"