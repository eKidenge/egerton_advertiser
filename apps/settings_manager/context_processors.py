from .models import SiteSetting
from apps.categories.models import Category
from apps.tags.models import Tag
from django.conf import settings


def site_settings(request):
    """Add site settings to all templates"""
    return {
        'SITE_NAME': get_setting_value('general', 'site_name', 'The Egerton Advertiser'),
        'SITE_TAGLINE': get_setting_value('general', 'site_tagline', 'Your Local News Source'),
        'SITE_URL': get_setting_value('general', 'site_url', 'http://localhost:8000'),
        'SITE_DESCRIPTION': get_setting_value('general', 'site_description', 'Official Gazette of Egerton, Kenya'),
        'GOOGLE_ANALYTICS_ID': get_setting_value('seo', 'google_analytics_id', ''),
        'OPENWEATHER_API_KEY': getattr(settings, 'OPENWEATHER_API_KEY', ''),
        'DEBUG': getattr(settings, 'DEBUG', True),
    }


def category_menu(request):
    """Add category menu to all templates"""
    categories = Category.objects.filter(
        is_active=True, 
        parent__isnull=True
    ).order_by('order')
    
    # Prefetch children for efficiency
    categories = categories.prefetch_related('children')
    
    return {'categories': categories}


def tags_menu(request):
    """Add tags to all templates"""
    tags = Tag.objects.filter(
        is_active=True
    ).order_by('name')[:20]
    
    return {'tags': tags}


def get_setting_value(category, key, default=''):
    """Get a setting value from the database"""
    try:
        setting = SiteSetting.objects.get(category=category, key=key)
        return setting.value
    except SiteSetting.DoesNotExist:
        return default