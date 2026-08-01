from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import timedelta, datetime
from .models import AnalyticsEvent, AnalyticsPageView, AnalyticsTrafficSource, AnalyticsRealTime
from .forms import AnalyticsFilterForm
from apps.articles.models import Article
from apps.accounts.models import User

@login_required
@user_passes_test(lambda u: u.can_view_analytics)
def analytics_dashboard(request):
    # Date range
    date_range = request.GET.get('range', '7d')
    end_date = timezone.now().date()
    
    if date_range == '24h':
        start_date = end_date - timedelta(days=1)
    elif date_range == '7d':
        start_date = end_date - timedelta(days=7)
    elif date_range == '30d':
        start_date = end_date - timedelta(days=30)
    elif date_range == '90d':
        start_date = end_date - timedelta(days=90)
    else:
        start_date = end_date - timedelta(days=7)
    
    # Get events in date range
    events = AnalyticsEvent.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    )
    
    # Statistics
    total_page_views = events.filter(event_type='page_view').count()
    unique_visitors = events.values('user_id').distinct().count()
    total_visits = events.values('session_id').distinct().count()
    bounce_rate = calculate_bounce_rate(events)
    avg_time_on_site = calculate_avg_time_on_site(events)
    
    # Page views by day
    daily_views = events.filter(
        event_type='page_view'
    ).extra(
        {'day': "date(created_at)"}
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    # Most viewed articles
    popular_articles = Article.objects.filter(
        analytics_views__date__gte=start_date
    ).annotate(
        views=Sum('analytics_views__views')
    ).order_by('-views')[:10]
    
    # Traffic sources
    traffic_sources = AnalyticsTrafficSource.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    ).values('source_type').annotate(
        total_visits=Sum('visits')
    ).order_by('-total_visits')
    
    # Real-time visitors
    realtime_visitors = AnalyticsRealTime.objects.filter(
        last_activity__gte=timezone.now() - timedelta(minutes=5)
    ).count()
    
    context = {
        'total_page_views': total_page_views,
        'unique_visitors': unique_visitors,
        'total_visits': total_visits,
        'bounce_rate': round(bounce_rate, 2),
        'avg_time_on_site': avg_time_on_site,
        'daily_views': list(daily_views),
        'popular_articles': popular_articles,
        'traffic_sources': list(traffic_sources),
        'realtime_visitors': realtime_visitors,
        'date_range': date_range,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'analytics/analytics_dashboard.html', context)

def calculate_bounce_rate(events):
    """Calculate bounce rate (sessions with only one page view)"""
    sessions = events.values('session_id').annotate(
        page_count=Count('id')
    )
    bounced = sessions.filter(page_count=1).count()
    total = sessions.count()
    
    if total > 0:
        return (bounced / total) * 100
    return 0

def calculate_avg_time_on_site(events):
    """Calculate average time on site (in seconds)"""
    # Group by session and calculate time difference
    sessions = events.values('session_id').annotate(
        first_event=Min('created_at'),
        last_event=Max('created_at')
    )
    
    total_time = 0
    count = 0
    
    for session in sessions:
        time_diff = (session['last_event'] - session['first_event']).total_seconds()
        if time_diff > 0:
            total_time += time_diff
            count += 1
    
    if count > 0:
        return round(total_time / count, 0)
    return 0

@login_required
@user_passes_test(lambda u: u.can_view_analytics)
def visitor_statistics(request):
    date_range = request.GET.get('range', '30d')
    end_date = timezone.now().date()
    
    if date_range == '7d':
        start_date = end_date - timedelta(days=7)
    elif date_range == '30d':
        start_date = end_date - timedelta(days=30)
    elif date_range == '90d':
        start_date = end_date - timedelta(days=90)
    else:
        start_date = end_date - timedelta(days=30)
    
    # Daily unique visitors
    daily_visitors = AnalyticsEvent.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).extra(
        {'day': "date(created_at)"}
    ).values('day').annotate(
        unique_visitors=Count('user_id', distinct=True),
        total_views=Count('id')
    ).order_by('day')
    
    # Device statistics
    device_stats = AnalyticsEvent.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).values('device_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Browser statistics
    browser_stats = AnalyticsEvent.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).values('browser').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # OS statistics
    os_stats = AnalyticsEvent.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).values('os').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Country statistics
    country_stats = AnalyticsEvent.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).values('country').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    context = {
        'daily_visitors': list(daily_visitors),
        'device_stats': list(device_stats),
        'browser_stats': list(browser_stats),
        'os_stats': list(os_stats),
        'country_stats': list(country_stats),
        'date_range': date_range,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'analytics/visitor_statistics.html', context)

@login_required
@user_passes_test(lambda u: u.can_view_analytics)
def article_statistics(request):
    date_range = request.GET.get('range', '30d')
    end_date = timezone.now().date()
    
    if date_range == '7d':
        start_date = end_date - timedelta(days=7)
    elif date_range == '30d':
        start_date = end_date - timedelta(days=30)
    elif date_range == '90d':
        start_date = end_date - timedelta(days=90)
    else:
        start_date = end_date - timedelta(days=30)
    
    # Top articles
    top_articles = Article.objects.filter(
        status='published',
        published_at__gte=start_date
    ).annotate(
        views=Sum('analytics_views__views')
    ).filter(views__gt=0).order_by('-views')[:20]
    
    # Article views by category
    category_stats = Article.objects.filter(
        status='published',
        published_at__gte=start_date
    ).values('category__name').annotate(
        total_views=Sum('analytics_views__views'),
        article_count=Count('id')
    ).order_by('-total_views')
    
    # Daily article views
    daily_article_views = AnalyticsEvent.objects.filter(
        event_type='article_view',
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).extra(
        {'day': "date(created_at)"}
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    context = {
        'top_articles': top_articles,
        'category_stats': list(category_stats),
        'daily_article_views': list(daily_article_views),
        'date_range': date_range,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'analytics/article_statistics.html', context)

@login_required
@user_passes_test(lambda u: u.can_view_analytics)
def traffic_sources(request):
    date_range = request.GET.get('range', '30d')
    end_date = timezone.now().date()
    
    if date_range == '7d':
        start_date = end_date - timedelta(days=7)
    elif date_range == '30d':
        start_date = end_date - timedelta(days=30)
    elif date_range == '90d':
        start_date = end_date - timedelta(days=90)
    else:
        start_date = end_date - timedelta(days=30)
    
    # Traffic sources summary
    sources = AnalyticsTrafficSource.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    ).values('source_type').annotate(
        total_visits=Sum('visits'),
        total_unique_visits=Sum('unique_visits'),
        total_conversions=Sum('conversions')
    ).order_by('-total_visits')
    
    # Daily traffic by source
    daily_traffic = AnalyticsTrafficSource.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    ).values('source_type', 'date').annotate(
        visits=Sum('visits')
    ).order_by('date')
    
    # Top referral sources
    top_referrals = AnalyticsTrafficSource.objects.filter(
        source_type='referral',
        date__gte=start_date,
        date__lte=end_date
    ).values('source_name').annotate(
        total_visits=Sum('visits')
    ).order_by('-total_visits')[:20]
    
    context = {
        'sources': list(sources),
        'daily_traffic': list(daily_traffic),
        'top_referrals': list(top_referrals),
        'date_range': date_range,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'analytics/traffic_sources.html', context)

@login_required
@user_passes_test(lambda u: u.can_view_analytics)
def realtime_data(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Return real-time data as JSON
        visitors = AnalyticsRealTime.objects.filter(
            last_activity__gte=timezone.now() - timedelta(minutes=5)
        )
        
        data = {
            'total_visitors': visitors.count(),
            'current_pages': [],
            'top_countries': [],
        }
        
        # Current pages
        page_data = visitors.values('current_path').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        data['current_pages'] = list(page_data)
        
        # Top countries
        country_data = visitors.values('country').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        data['top_countries'] = list(country_data)
        
        return JsonResponse(data)
    
    return render(request, 'analytics/realtime.html')

@require_http_methods(["POST"])
def track_event(request):
    """API endpoint to track events from frontend"""
    try:
        import json
        data = json.loads(request.body)
        
        event = AnalyticsEvent.objects.create(
            event_type=data.get('event_type', 'page_view'),
            event_name=data.get('event_name', ''),
            event_value=data.get('event_value'),
            url=data.get('url', request.META.get('HTTP_REFERER', '')),
            path=data.get('path', ''),
            referer=data.get('referer', request.META.get('HTTP_REFERER', '')),
            title=data.get('title', ''),
            user=request.user if request.user.is_authenticated else None,
            session_id=data.get('session_id', request.session.session_key),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            browser=data.get('browser', ''),
            os=data.get('os', ''),
            device_type=data.get('device_type', ''),
            ip_address=request.META.get('REMOTE_ADDR'),
            country=data.get('country', ''),
            city=data.get('city', ''),
            data=data.get('data', {})
        )
        
        return JsonResponse({'success': True, 'event_id': event.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)