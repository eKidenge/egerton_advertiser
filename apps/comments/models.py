from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.html import escape
from apps.articles.models import Article

User = get_user_model()

class Comment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('spam', 'Marked as Spam'),
        ('trash', 'In Trash'),
    )
    
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="Article this comment belongs to"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="User who made the comment"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        help_text="Parent comment if this is a reply"
    )
    
    content = models.TextField(
        max_length=2000,
        help_text="Comment content"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Moderation
    moderator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='moderated_comments'
    )
    moderation_notes = models.TextField(blank=True)
    moderated_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referer = models.URLField(blank=True)
    
    # Engagement
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)
    reports = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'comments'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['article', 'status']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['parent']),
        ]
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.article.title}"
    
    def save(self, *args, **kwargs):
        # Escape content for security
        self.content = escape(self.content)
        super().save(*args, **kwargs)
    
    def approve(self, moderator):
        self.status = 'approved'
        self.moderator = moderator
        self.moderated_at = timezone.now()
        self.save()
    
    def reject(self, moderator, notes=''):
        self.status = 'rejected'
        self.moderator = moderator
        self.moderated_at = timezone.now()
        self.moderation_notes = notes
        self.save()
    
    def mark_as_spam(self, moderator):
        self.status = 'spam'
        self.moderator = moderator
        self.moderated_at = timezone.now()
        self.save()
    
    def get_replies(self):
        return self.replies.filter(status='approved')

class CommentVote(models.Model):
    VOTE_CHOICES = (
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    )
    
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_votes')
    vote_type = models.CharField(max_length=10, choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'comment_votes'
        unique_together = ['comment', 'user']
        indexes = [
            models.Index(fields=['comment', 'user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} {self.vote_type} on comment {self.comment.id}"