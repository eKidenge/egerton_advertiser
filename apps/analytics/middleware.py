from .models import AnalyticsRealTime
from django.utils import timezone


class AnalyticsMiddleware:
    """Track real-time visitors"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Update real-time visitor tracking
        if not request.path.startswith('/admin/') and not request.path.startswith('/static/'):
            session_id = request.session.session_key
            if session_id:
                visitor, created = AnalyticsRealTime.objects.get_or_create(
                    session_id=session_id,
                    defaults={
                        'current_page': request.path,
                        'current_path': request.path,
                        'ip_address': request.META.get('REMOTE_ADDR'),
                        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    }
                )
                if not created:
                    visitor.current_page = request.build_absolute_uri()
                    visitor.current_path = request.path
                    visitor.referer = request.META.get('HTTP_REFERER', '')
                    visitor.last_activity = timezone.now()
                    visitor.save(update_fields=['current_page', 'current_path', 'referer', 'last_activity'])
        
        return response