from django import template
from django.utils.html import mark_safe
import re

register = template.Library()

@register.filter
def truncate_chars(value, max_length):
    """Truncate text to a certain number of characters"""
    if len(value) <= max_length:
        return value
    return value[:max_length] + '...'

@register.filter
def time_to_read(value):
    """Calculate time to read based on word count"""
    words = len(value.split())
    minutes = max(1, round(words / 200))
    return f"{minutes} min read"

@register.filter
def highlight_search(value, query):
    """Highlight search terms in text"""
    if not query:
        return value
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return mark_safe(pattern.sub(r'<mark>\g<0></mark>', value))

@register.simple_tag
def get_article_count(category):
    """Get article count for a category"""
    return category.article_count if hasattr(category, 'article_count') else 0