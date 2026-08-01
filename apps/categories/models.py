from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinLengthValidator

class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        validators=[MinLengthValidator(2)],
        help_text="Category name (e.g., Politics, Business, Sports)"
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
        help_text="URL-friendly version of the category name"
    )
    description = models.TextField(
        max_length=500,
        blank=True,
        help_text="Brief description of the category"
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="FontAwesome icon class (e.g., fa-gavel for Politics)"
    )
    color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Hex color code for the category (e.g., #FF0000)"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        help_text="Parent category if this is a sub-category"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order in navigation"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this category is active and visible"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Whether to show this category in featured sections"
    )
    
    # Meta fields
    seo_title = models.CharField(max_length=150, blank=True)
    seo_description = models.CharField(max_length=200, blank=True)
    seo_keywords = models.CharField(max_length=200, blank=True)
    
    # Image
    image = models.ImageField(
        upload_to='categories/%Y/%m/',
        blank=True,
        null=True,
        help_text="Category image for featured sections"
    )
    image_alt = models.CharField(max_length=200, blank=True)
    
    # Statistics
    article_count = models.PositiveIntegerField(default=0)
    total_views = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['parent', 'is_active']),
            models.Index(fields=['order']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure unique slug
            original_slug = self.slug
            counter = 1
            while Category.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('categories:detail', kwargs={'slug': self.slug})
    
    def get_children(self):
        return self.children.filter(is_active=True)
    
    @property
    def is_parent(self):
        return self.children.exists()
    
    @property
    def level(self):
        level = 0
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent
        return level
    
    def update_article_count(self):
        from apps.articles.models import Article
        count = Article.objects.filter(category=self, status='published').count()
        self.article_count = count
        self.save(update_fields=['article_count'])