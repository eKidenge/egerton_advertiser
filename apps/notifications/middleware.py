from django.utils import timezone
from .models import Notification


class NotificationMiddleware:
    """Add notification context to requests"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process request
        response = self.get_response(request)
        
        # Add notification count to request
        if request.user.is_authenticated:
            request.unread_notifications = Notification.objects.filter(
                user=request.user, 
                is_read=False
            ).count()
        
        return response