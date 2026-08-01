from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import SearchQuery, SearchResultClick
from apps.articles.models import Article
from apps.categories.models import Category
from apps.tags.models import Tag
from apps.accounts.models import User

def search(request):
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'all')
    page = request.GET.get('page', 1)
    
    results = {
        'articles': [],
        'categories': [],
        'tags': [],
        'authors': [],
    }
    
    total_results = 0
    query_obj = None
    
    if query:
        # Save search query
        query_obj = SearchQuery.objects.create(
            query=query,
            user=request.user if request.user.is_authenticated else None,
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        
        # Search articles
        if search_type in ['all', 'articles']:
            articles = Article.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query) |
                Q(tags__name__icontains=query) |
                Q(category__name__icontains=query),
                status='published'
            ).distinct().select_related('author', 'category')
            
            results['articles'] = articles
            total_results += articles.count()
        
        # Search categories
        if search_type in ['all', 'categories']:
            categories = Category.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query),
                is_active=True
            )
            results['categories'] = categories
            total_results += categories.count()
        
        # Search tags
        if search_type in ['all', 'tags']:
            tags = Tag.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query),
                is_active=True
            )
            results['tags'] = tags
            total_results += tags.count()
        
        # Search authors
        if search_type in ['all', 'authors']:
            authors = User.objects.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query),
                is_active=True
            )
            results['authors'] = authors
            total_results += authors.count()
        
        # Update search query with results count
        if query_obj:
            query_obj.results_count = total_results
            query_obj.filters = {'search_type': search_type}
            query_obj.save()
    
    # Pagination for articles (the most common search)
    article_paginator = Paginator(results['articles'], 10)
    try:
        articles_page = article_paginator.page(page)
    except PageNotAnInteger:
        articles_page = article_paginator.page(1)
    except EmptyPage:
        articles_page = article_paginator.page(article_paginator.num_pages)
    
    context = {
        'query': query,
        'search_type': search_type,
        'results': results,
        'articles_page': articles_page,
        'total_results': total_results,
        'has_results': total_results > 0,
    }
    
    return render(request, 'search/search_results.html', context)

@login_required
def advanced_search(request):
    if request.method == 'POST':
        query = request.POST.get('q', '')
        category = request.POST.get('category', '')
        author = request.POST.get('author', '')
        date_from = request.POST.get('date_from', '')
        date_to = request.POST.get('date_to', '')
        tags = request.POST.get('tags', '')
        sort_by = request.POST.get('sort_by', '-published_at')
        
        # Build search query
        articles = Article.objects.filter(status='published')
        
        if query:
            articles = articles.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query)
            )
        
        if category:
            articles = articles.filter(category__slug=category)
        
        if author:
            articles = articles.filter(author__username=author)
        
        if date_from:
            articles = articles.filter(published_at__gte=date_from)
        
        if date_to:
            articles = articles.filter(published_at__lte=date_to)
        
        if tags:
            tag_list = [t.strip() for t in tags.split(',')]
            for tag in tag_list:
                articles = articles.filter(tags__name__icontains=tag)
        
        articles = articles.distinct().select_related('author', 'category')
        
        # Sorting
        if sort_by == 'relevance':
            # Default ordering
            articles = articles.order_by('-published_at')
        elif sort_by == 'newest':
            articles = articles.order_by('-published_at')
        elif sort_by == 'oldest':
            articles = articles.order_by('published_at')
        elif sort_by == 'popular':
            articles = articles.order_by('-views_count')
        
        # Pagination
        paginator = Paginator(articles, 20)
        page = request.GET.get('page', 1)
        try:
            articles = paginator.page(page)
        except PageNotAnInteger:
            articles = paginator.page(1)
        except EmptyPage:
            articles = paginator.page(paginator.num_pages)
        
        # Get categories and authors for filters
        categories = Category.objects.filter(is_active=True)
        authors = User.objects.filter(is_active=True)
        
        context = {
            'articles': articles,
            'query': query,
            'category': category,
            'author': author,
            'date_from': date_from,
            'date_to': date_to,
            'tags': tags,
            'sort_by': sort_by,
            'categories': categories,
            'authors': authors,
        }
        
        return render(request, 'search/advanced_search_results.html', context)
    
    # GET request - show advanced search form
    categories = Category.objects.filter(is_active=True)
    authors = User.objects.filter(is_active=True)
    
    context = {
        'categories': categories,
        'authors': authors,
    }
    
    return render(request, 'search/advanced_search.html', context)

@require_http_methods(["POST"])
def track_click(request):
    """Track search result clicks for analytics"""
    try:
        import json
        data = json.loads(request.body)
        
        search_query_id = data.get('search_query_id')
        result_index = data.get('result_index')
        result_type = data.get('result_type')
        result_id = data.get('result_id')
        result_title = data.get('result_title')
        
        if search_query_id:
            search_query = SearchQuery.objects.get(id=search_query_id)
            SearchResultClick.objects.create(
                search_query=search_query,
                result_index=result_index,
                result_type=result_type,
                result_id=result_id,
                result_title=result_title
            )
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@user_passes_test(lambda u: u.can_manage_users)
def search_statistics(request):
    # Search query statistics
    total_searches = SearchQuery.objects.count()
    unique_searches = SearchQuery.objects.values('query').distinct().count()
    avg_results = SearchQuery.objects.aggregate(avg_results=Count('id'))['avg_results'] or 0
    
    # Popular search queries
    popular_queries = SearchQuery.objects.values('query').annotate(
        count=Count('id')
    ).order_by('-count')[:20]
    
    # Searches by day
    daily_searches = SearchQuery.objects.extra(
        {'day': "date(created_at)"}
    ).values('day').annotate(
        count=Count('id')
    ).order_by('-day')[:30]
    
    # Search result clicks
    total_clicks = SearchResultClick.objects.count()
    click_through_rate = (total_clicks / total_searches * 100) if total_searches > 0 else 0
    
    # Top clicked results
    top_results = SearchResultClick.objects.values('result_type', 'result_title').annotate(
        clicks=Count('id')
    ).order_by('-clicks')[:20]
    
    context = {
        'total_searches': total_searches,
        'unique_searches': unique_searches,
        'avg_results': avg_results,
        'popular_queries': list(popular_queries),
        'daily_searches': list(daily_searches),
        'total_clicks': total_clicks,
        'click_through_rate': round(click_through_rate, 2),
        'top_results': list(top_results),
    }
    
    return render(request, 'analytics/search_statistics.html', context)