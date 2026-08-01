from django.utils import timezone
from .models import UserActivityLog


class ActivityLogMiddleware:
    """Log user activity"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if request.user.is_authenticated and request.method == 'GET':
            # Log page views for authenticated users
            if not request.path.startswith('/admin/') and not request.path.startswith('/static/'):
                UserActivityLog.objects.create(
                    user=request.user,
                    action='view',
                    model_name='Page',
                    description=f'Viewed page: {request.path}',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    referer=request.META.get('HTTP_REFERER', '')
                )
        
        return response