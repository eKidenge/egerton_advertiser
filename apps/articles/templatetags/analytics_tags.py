from django import template
from django.conf import settings

register = template.Library()

@register.inclusion_tag('analytics/analytics_code.html')
def analytics_code():
    """Include Google Analytics code"""
    return {
        'GA_ID': settings.GOOGLE_ANALYTICS_ID if hasattr(settings, 'GOOGLE_ANALYTICS_ID') else '',
        'DEBUG': settings.DEBUG
    }