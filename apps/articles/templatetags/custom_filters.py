from django import template
from django.utils.html import mark_safe
import re

register = template.Library()

@register.filter
def truncate_chars(value, max_length):
    """Truncate text to a certain number of characters"""
    if not value:
        return ''
    if len(value) <= max_length:
        return value
    return value[:max_length] + '...'

@register.filter
def time_to_read(value):
    """Calculate time to read based on word count"""
    if not value:
        return '1 min read'
    words = len(value.split())
    minutes = max(1, round(words / 200))
    return f"{minutes} min read"

@register.filter
def highlight_search(value, query):
    """Highlight search terms in text"""
    if not value or not query:
        return value
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return mark_safe(pattern.sub(r'<mark>\g<0></mark>', value))

@register.filter
def intcomma(value):
    """Add commas to numbers"""
    if value is None:
        return '0'
    return f"{value:,}"

@register.simple_tag
def get_article_count(category):
    """Get article count for a category"""
    if hasattr(category, 'article_count'):
        return category.article_count
    return 0

@register.filter
def truncatewords(value, num_words):
    """Truncate text to a certain number of words"""
    if not value:
        return ''
    words = value.split()
    if len(words) <= num_words:
        return value
    return ' '.join(words[:num_words]) + '...'