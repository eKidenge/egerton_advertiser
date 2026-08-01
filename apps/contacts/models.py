from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import EmailValidator

User = get_user_model()

class ContactMessage(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('archived', 'Archived'),
        ('spam', 'Spam'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    # Sender information
    name = models.CharField(max_length=100)
    email = models.EmailField(validators=[EmailValidator()])
    phone = models.CharField(max_length=20, blank=True)
    
    # Message content
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # User association (if logged in)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contact_messages'
    )
    
    # Response
    response = models.TextField(blank=True)
    responded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contact_responses'
    )
    responded_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referer = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'contact_messages'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['email']),
            models.Index(fields=['created_at']),
            models.Index(fields=['priority', 'status']),
        ]
    
    def __str__(self):
        return f"{self.subject} - {self.name}"
    
    def mark_as_read(self):
        self.status = 'read'
        self.save(update_fields=['status'])
    
    def reply(self, response, user):
        self.response = response
        self.responded_by = user
        self.responded_at = timezone.now()
        self.status = 'replied'
        self.save()
    
    def archive(self):
        self.status = 'archived'
        self.save(update_fields=['status'])
    
    def mark_as_spam(self):
        self.status = 'spam'
        self.save(update_fields=['status'])