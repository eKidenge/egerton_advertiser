from django import template
from django.conf import settings

register = template.Library()

@register.inclusion_tag('analytics/analytics_code.html')
def analytics_code():
    """Include Google Analytics code"""
    return {
        'GA_ID': getattr(settings, 'GOOGLE_ANALYTICS_ID', ''),
        'DEBUG': getattr(settings, 'DEBUG', True)
    }

@register.simple_tag
def get_ga_id():
    """Get Google Analytics ID"""
    return getattr(settings, 'GOOGLE_ANALYTICS_ID', '')

@register.filter
def format_duration(seconds):
    """Format duration in seconds to readable format"""
    if not seconds:
        return '0s'
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    if minutes > 0:
        return f'{minutes}m {seconds}s'
    return f'{seconds}s'