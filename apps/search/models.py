from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class SearchQuery(models.Model):
    query = models.CharField(max_length=200)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='search_queries'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    results_count = models.PositiveIntegerField(default=0)
    filters = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'search_queries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['query']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.query} - {self.created_at}"

class SearchResultClick(models.Model):
    search_query = models.ForeignKey(SearchQuery, on_delete=models.CASCADE, related_name='clicks')
    result_index = models.PositiveIntegerField()
    result_type = models.CharField(max_length=50)  # article, category, tag, etc.
    result_id = models.PositiveIntegerField()
    result_title = models.CharField(max_length=200)
    clicked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'search_result_clicks'
        ordering = ['-clicked_at']
    
    def __str__(self):
        return f"Click on {self.result_title} from search: {self.search_query.query}"