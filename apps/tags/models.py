from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinLengthValidator

class Tag(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        validators=[MinLengthValidator(2)],
        help_text="Tag name (e.g., Election, Economy, World Cup)"
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
        help_text="URL-friendly version of the tag name"
    )
    description = models.TextField(
        max_length=300,
        blank=True,
        help_text="Brief description of the tag"
    )
    color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Hex color code for the tag"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this tag is active and visible"
    )
    
    # Statistics
    article_count = models.PositiveIntegerField(default=0)
    total_views = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tags'
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure unique slug
            original_slug = self.slug
            counter = 1
            while Tag.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('tags:detail', kwargs={'slug': self.slug})
    
    def update_article_count(self):
        from apps.articles.models import Article
        count = Article.objects.filter(tags=self, status='published').count()
        self.article_count = count
        self.save(update_fields=['article_count'])