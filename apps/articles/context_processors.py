from apps.categories.models import Category
from apps.tags.models import Tag


def category_menu(request):
    """Add category menu to all templates"""
    categories = Category.objects.filter(
        is_active=True, 
        parent__isnull=True
    ).order_by('order')
    
    return {'categories': categories}


def tags_menu(request):
    """Add tags to all templates"""
    tags = Tag.objects.filter(
        is_active=True
    ).order_by('name')[:20]
    
    return {'tags': tags}