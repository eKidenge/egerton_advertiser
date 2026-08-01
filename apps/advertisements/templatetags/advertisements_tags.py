from django import template
from ..models import Advertisement
from django.utils import timezone

register = template.Library()

@register.simple_tag
def get_ad_by_position(position):
    """Get an ad by position"""
    ads = Advertisement.objects.filter(
        position=position,
        status='active',
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    ).order_by('-priority')
    
    for ad in ads:
        if ad.can_show():
            return ad
    return None

@register.inclusion_tag('advertisements/ad_banner.html')
def show_ad(position, width='full', css_class=''):
    """Display an ad in a specific position"""
    ad = get_ad_by_position(position)
    return {
        'ad': ad,
        'position': position,
        'width': width,
        'css_class': css_class
    }