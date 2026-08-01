from .models import SiteSetting
from apps.categories.models import Category
from apps.tags.models import Tag

def site_settings(request):
    """Add site settings to all templates"""
    return {
        'SITE_NAME': get_setting_value('general', 'site_name', 'The Egerton Advertiser'),
        'SITE_TAGLINE': get_setting_value('general', 'site_tagline', 'Your Local News Source'),
        'SITE_URL': get_setting_value('general', 'site_url', 'http://localhost:8000'),
        'GOOGLE_ANALYTICS_ID': get_setting_value('seo', 'google_analytics_id', ''),
    }

def category_menu(request):
    """Add category menu to all templates"""
    categories = Category.objects.filter(is_active=True, parent__isnull=True).order_by('order')
    return {'categories': categories}

def get_setting_value(category, key, default=''):
    try:
        setting = SiteSetting.objects.get(category=category, key=key)
        return setting.value
    except SiteSetting.DoesNotExist:
        return default