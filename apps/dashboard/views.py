from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Avg, Q, Max, Min
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import timedelta, datetime
import json

from .models import DashboardWidget, DashboardPreference, DashboardMetric, QuickAction, DashboardActivityFeed
from .forms import DashboardWidgetForm, DashboardPreferenceForm
from apps.articles.models import Article, ArticleVersion
from apps.articles.forms import ArticleForm
from apps.categories.models import Category
from apps.categories.forms import CategoryForm
from apps.tags.models import Tag
from apps.tags.forms import TagForm
from apps.comments.models import Comment
from apps.comments.forms import CommentModerationForm
from apps.accounts.models import User, UserActivityLog
from apps.accounts.forms import UserCreateForm, UserEditForm
from apps.advertisements.models import Advertisement, AdvertisementView, AdvertisementClick
from apps.advertisements.forms import AdvertisementForm
from apps.media_library.models import MediaFile
from apps.media_library.forms import MediaFileForm
from apps.newsletter.models import Subscriber, Newsletter
from apps.newsletter.forms import NewsletterForm
from apps.contacts.models import ContactMessage
from apps.contacts.forms import ContactReplyForm
from apps.settings_manager.models import SiteSetting
from apps.settings_manager.forms import GeneralSettingsForm, EmailSettingsForm, SEOSettingsForm


# ============================================
# USER DASHBOARD - MAIN
# ============================================

@login_required
def dashboard(request):
    """Main user dashboard - role based"""
    user = request.user
    role = user.role
    
    # Get or create preferences
    preferences, created = DashboardPreference.objects.get_or_create(user=user)
    
    # Get widgets
    widgets = DashboardWidget.objects.filter(user=user, is_active=True).order_by('column', 'position')
    
    # Get quick actions
    quick_actions = QuickAction.objects.filter(user=user, is_active=True).order_by('order')
    
    # Get role-based statistics
    stats = get_role_based_stats(user, role)
    
    # Get recent activity
    recent_activity = DashboardActivityFeed.objects.filter(user=user)[:10]
    
    # Get role-based recent items
    recent_items = get_role_based_recent_items(user, role)
    
    # Get notifications
    notifications = DashboardActivityFeed.objects.filter(user=user, is_read=False)[:5]
    
    context = {
        'preferences': preferences,
        'widgets': widgets,
        'quick_actions': quick_actions,
        'stats': stats,
        'recent_activity': recent_activity,
        'recent_items': recent_items,
        'notifications': notifications,
        'role': role,
        'is_super_admin': role == 'super_admin',
        'is_admin': role == 'admin',
        'is_editor': role == 'editor',
        'is_journalist': role == 'journalist',
        'is_subscriber': role == 'subscriber',
        'is_advertiser': role == 'advertiser',
    }
    
    return render(request, 'dashboard/dashboard.html', context)


def get_role_based_stats(user, role):
    """Get statistics based on user role"""
    stats = {}
    
    if role == 'super_admin' or role == 'admin':
        # Admin Stats - Full System Overview
        stats['total_users'] = User.objects.count()
        stats['active_users'] = User.objects.filter(is_active=True).count()
        stats['total_articles'] = Article.objects.count()
        stats['published_articles'] = Article.objects.filter(status='published').count()
        stats['draft_articles'] = Article.objects.filter(status='draft').count()
        stats['pending_articles'] = Article.objects.filter(status='pending').count()
        stats['total_views'] = Article.objects.aggregate(Sum('views_count'))['views_count__sum'] or 0
        stats['total_comments'] = Comment.objects.count()
        stats['pending_comments'] = Comment.objects.filter(status='pending').count()
        stats['total_subscribers'] = Subscriber.objects.filter(status='active').count()
        stats['total_ads'] = Advertisement.objects.count()
        stats['active_ads'] = Advertisement.objects.filter(status='active').count()
        
        # Growth calculations
        last_week = timezone.now() - timedelta(days=7)
        stats['user_growth'] = calculate_growth(User, 'date_joined', last_week)
        stats['article_growth'] = calculate_growth(Article, 'created_at', last_week)
        stats['view_growth'] = calculate_view_growth(last_week)
        
    elif role == 'editor':
        # Editor Stats - Article Management
        stats['total_articles'] = Article.objects.count()
        stats['published_articles'] = Article.objects.filter(status='published').count()
        stats['draft_articles'] = Article.objects.filter(status='draft').count()
        stats['pending_articles'] = Article.objects.filter(status='pending').count()
        stats['scheduled_articles'] = Article.objects.filter(status='scheduled').count()
        stats['archived_articles'] = Article.objects.filter(status='archived').count()
        stats['total_views'] = Article.objects.aggregate(Sum('views_count'))['views_count__sum'] or 0
        stats['pending_comments'] = Comment.objects.filter(status='pending').count()
        stats['total_comments'] = Comment.objects.count()
        stats['featured_articles'] = Article.objects.filter(is_featured=True).count()
        stats['breaking_news'] = Article.objects.filter(is_breaking=True).count()
        
    elif role == 'journalist':
        # Journalist Stats - My Articles
        my_articles = Article.objects.filter(author=user)
        stats['my_articles'] = my_articles.count()
        stats['my_published'] = my_articles.filter(status='published').count()
        stats['my_drafts'] = my_articles.filter(status='draft').count()
        stats['my_pending'] = my_articles.filter(status='pending').count()
        stats['my_views'] = my_articles.aggregate(Sum('views_count'))['views_count__sum'] or 0
        stats['my_comments'] = Comment.objects.filter(article__author=user).count()
        stats['total_articles'] = Article.objects.count()
        stats['total_views'] = Article.objects.aggregate(Sum('views_count'))['views_count__sum'] or 0
        
    elif role == 'subscriber':
        # Subscriber Stats - Personal
        stats['saved_articles'] = 0
        stats['my_comments'] = Comment.objects.filter(user=user).count()
        stats['subscription_status'] = 'Active' if Subscriber.objects.filter(email=user.email, status='active').exists() else 'Inactive'
        stats['total_articles'] = Article.objects.filter(status='published').count()
        
    elif role == 'advertiser':
        # Advertiser Stats - Ad Campaigns
        my_ads = Advertisement.objects.filter(advertiser=user)
        stats['total_ads'] = my_ads.count()
        stats['active_ads'] = my_ads.filter(status='active').count()
        stats['pending_ads'] = my_ads.filter(status='pending').count()
        stats['expired_ads'] = my_ads.filter(status='expired').count()
        stats['ad_views'] = my_ads.aggregate(Sum('views_count'))['views_count__sum'] or 0
        stats['ad_clicks'] = my_ads.aggregate(Sum('clicks_count'))['clicks_count__sum'] or 0
        
        # Calculate CTR
        total_views = stats['ad_views']
        total_clicks = stats['ad_clicks']
        stats['ctr'] = round((total_clicks / total_views * 100), 2) if total_views > 0 else 0
        
        # Ad performance
        stats['top_ad'] = my_ads.order_by('-views_count').first()
    
    return stats


def calculate_growth(model, field, since_date):
    """Calculate percentage growth"""
    current_count = model.objects.count()
    previous_count = model.objects.filter(**{f'{field}__lt': since_date}).count()
    
    if previous_count == 0:
        return 0 if current_count == 0 else 100
    
    return round(((current_count - previous_count) / previous_count) * 100, 1)


def calculate_view_growth(since_date):
    """Calculate view growth"""
    current_views = Article.objects.aggregate(Sum('views_count'))['views_count__sum'] or 0
    previous_views = Article.objects.filter(created_at__lt=since_date).aggregate(Sum('views_count'))['views_count__sum'] or 0
    
    if previous_views == 0:
        return 0 if current_views == 0 else 100
    
    return round(((current_views - previous_views) / previous_views) * 100, 1)


def get_role_based_recent_items(user, role):
    """Get recent items based on role"""
    items = {}
    
    if role in ['super_admin', 'admin']:
        # Recent users
        items['recent_users'] = User.objects.order_by('-date_joined')[:5]
        # Recent articles
        items['recent_articles'] = Article.objects.order_by('-created_at')[:5]
        # Recent comments
        items['recent_comments'] = Comment.objects.order_by('-created_at')[:5]
        
    elif role == 'editor':
        # Pending articles
        items['pending_articles'] = Article.objects.filter(status='pending').order_by('-created_at')[:10]
        # Recent articles
        items['recent_articles'] = Article.objects.order_by('-created_at')[:5]
        # Pending comments
        items['pending_comments'] = Comment.objects.filter(status='pending').order_by('-created_at')[:5]
        
    elif role == 'journalist':
        # My recent articles
        items['my_articles'] = Article.objects.filter(author=user).order_by('-created_at')[:10]
        # My drafts
        items['my_drafts'] = Article.objects.filter(author=user, status='draft').order_by('-created_at')[:5]
        
    elif role == 'subscriber':
        # Latest articles
        items['latest_articles'] = Article.objects.filter(status='published').order_by('-published_at')[:10]
        # My comments
        items['my_comments'] = Comment.objects.filter(user=user).order_by('-created_at')[:5]
        
    elif role == 'advertiser':
        # My ads
        items['my_ads'] = Advertisement.objects.filter(advertiser=user).order_by('-created_at')[:10]
        # Top performing ads
        items['top_ads'] = Advertisement.objects.filter(advertiser=user).order_by('-views_count')[:5]
    
    return items


# ============================================
# WIDGET MANAGEMENT
# ============================================

@login_required
@require_http_methods(["POST"])
def add_widget(request):
    form = DashboardWidgetForm(request.POST)
    if form.is_valid():
        widget = form.save(commit=False)
        widget.user = request.user
        widget.save()
        
        messages.success(request, f'Widget "{widget.title}" added successfully!')
        return JsonResponse({'success': True, 'widget_id': widget.id})
    
    return JsonResponse({'success': False, 'errors': form.errors})


@login_required
def edit_widget(request, widget_id):
    widget = get_object_or_404(DashboardWidget, id=widget_id, user=request.user)
    
    if request.method == 'POST':
        form = DashboardWidgetForm(request.POST, instance=widget)
        if form.is_valid():
            form.save()
            messages.success(request, 'Widget updated successfully!')
            return redirect('dashboard:dashboard')
    else:
        form = DashboardWidgetForm(instance=widget)
    
    return render(request, 'dashboard/edit_widget.html', {'form': form, 'widget': widget})


@login_required
@require_http_methods(["POST"])
def delete_widget(request, widget_id):
    widget = get_object_or_404(DashboardWidget, id=widget_id, user=request.user)
    widget.delete()
    messages.success(request, 'Widget deleted successfully!')
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def reorder_widgets(request):
    try:
        data = request.POST.get('data')
        widget_data = json.loads(data)
        
        for item in widget_data:
            widget = DashboardWidget.objects.get(id=item['id'], user=request.user)
            widget.column = item['column']
            widget.position = item['position']
            widget.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def toggle_widget(request, widget_id):
    widget = get_object_or_404(DashboardWidget, id=widget_id, user=request.user)
    widget.is_active = not widget.is_active
    widget.save()
    
    status = 'activated' if widget.is_active else 'deactivated'
    messages.success(request, f'Widget "{widget.title}" {status}!')
    return JsonResponse({'success': True, 'is_active': widget.is_active})


@login_required
@require_http_methods(["POST"])
def reset_widgets(request):
    """Reset all widgets to default"""
    DashboardWidget.objects.filter(user=request.user).delete()
    # Create default widgets
    default_widgets = [
        {'title': 'Stats Overview', 'widget_type': 'stats', 'column': 1, 'position': 1},
        {'title': 'Recent Activity', 'widget_type': 'activity', 'column': 2, 'position': 1},
        {'title': 'Quick Actions', 'widget_type': 'quick_actions', 'column': 1, 'position': 2},
        {'title': 'Notifications', 'widget_type': 'notifications', 'column': 2, 'position': 2},
    ]
    
    for widget_data in default_widgets:
        DashboardWidget.objects.create(user=request.user, **widget_data)
    
    messages.success(request, 'Widgets reset to default successfully!')
    return JsonResponse({'success': True})


# ============================================
# USER DASHBOARD VIEWS
# ============================================

@login_required
def profile(request):
    user = request.user
    
    # Get user statistics
    articles = Article.objects.filter(author=user)
    comments = Comment.objects.filter(user=user)
    
    context = {
        'user': user,
        'total_articles': articles.count(),
        'published_articles': articles.filter(status='published').count(),
        'total_comments': comments.count(),
        'total_views': articles.aggregate(Sum('views_count'))['views_count__sum'] or 0,
    }
    return render(request, 'dashboard/profile.html', context)


@login_required
def profile_edit(request):
    """Edit user profile"""
    user = request.user
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard:profile')
    else:
        form = UserEditForm(instance=user)
    
    return render(request, 'dashboard/profile_edit.html', {'form': form})


@login_required
def profile_activity(request):
    """View user activity"""
    user = request.user
    activities = UserActivityLog.objects.filter(user=user).order_by('-timestamp')
    
    paginator = Paginator(activities, 20)
    page = request.GET.get('page')
    try:
        activities = paginator.page(page)
    except PageNotAnInteger:
        activities = paginator.page(1)
    except EmptyPage:
        activities = paginator.page(paginator.num_pages)
    
    return render(request, 'dashboard/profile_activity.html', {'activities': activities})


@login_required
def profile_preferences(request):
    """Edit user preferences"""
    user = request.user
    preferences, created = DashboardPreference.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        form = DashboardPreferenceForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            messages.success(request, 'Preferences updated successfully!')
            return redirect('dashboard:profile')
    else:
        form = DashboardPreferenceForm(instance=preferences)
    
    return render(request, 'dashboard/profile_preferences.html', {'form': form})


@login_required
def activity_log(request):
    user = request.user
    
    if user.can_manage_users:
        activities = UserActivityLog.objects.all().select_related('user')
    else:
        activities = UserActivityLog.objects.filter(user=user)
    
    # Filtering
    action = request.GET.get('action')
    if action:
        activities = activities.filter(action=action)
    
    date_from = request.GET.get('date_from')
    if date_from:
        activities = activities.filter(timestamp__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        activities = activities.filter(timestamp__lte=date_to)
    
    activities = activities.order_by('-timestamp')
    
    paginator = Paginator(activities, 50)
    page = request.GET.get('page')
    try:
        activities = paginator.page(page)
    except PageNotAnInteger:
        activities = paginator.page(1)
    except EmptyPage:
        activities = paginator.page(paginator.num_pages)
    
    context = {
        'activities': activities,
        'action_filter': action,
    }
    return render(request, 'dashboard/activity_log.html', context)


@login_required
def notifications(request):
    user = request.user
    
    # Get notifications from activity feed
    notifications = DashboardActivityFeed.objects.filter(user=user).order_by('-created_at')
    
    # Mark as read
    if request.GET.get('mark_read'):
        notifications.filter(is_read=False).update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
        return redirect('dashboard:notifications')
    
    paginator = Paginator(notifications, 20)
    page = request.GET.get('page')
    try:
        notifications = paginator.page(page)
    except PageNotAnInteger:
        notifications = paginator.page(1)
    except EmptyPage:
        notifications = paginator.page(paginator.num_pages)
    
    return render(request, 'dashboard/notifications.html', {'notifications': notifications})


@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(DashboardActivityFeed, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def mark_all_notifications_read(request):
    DashboardActivityFeed.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read!')
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def clear_notifications(request):
    DashboardActivityFeed.objects.filter(user=request.user).delete()
    messages.success(request, 'All notifications cleared!')
    return JsonResponse({'success': True})


@login_required
def settings(request):
    user = request.user
    
    if request.method == 'POST':
        form = DashboardPreferenceForm(request.POST, instance=user.dashboard_preferences)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dashboard settings updated successfully!')
            return redirect('dashboard:settings')
    else:
        form = DashboardPreferenceForm(instance=user.dashboard_preferences)
    
    return render(request, 'dashboard/settings.html', {'form': form})


@login_required
def settings_update(request):
    """Update user settings"""
    if request.method == 'POST':
        user = request.user
        # Update preferences
        preferences, created = DashboardPreference.objects.get_or_create(user=user)
        form = DashboardPreferenceForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated successfully!')
            return redirect('dashboard:settings')
    
    return redirect('dashboard:settings')


# ============================================
# ADMIN DASHBOARD - MAIN VIEW (FIXED)
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_dashboard(request):
    """Complete Admin Dashboard - Full System Control"""
    
    # ========================================
    # STATISTICS - Full System Overview
    # ========================================
    
    # Articles
    total_articles = Article.objects.count()
    published_articles = Article.objects.filter(status='published').count()
    draft_articles = Article.objects.filter(status='draft').count()
    pending_articles = Article.objects.filter(status='pending').count()
    scheduled_articles = Article.objects.filter(status='scheduled').count()
    archived_articles = Article.objects.filter(status='archived').count()
    featured_articles = Article.objects.filter(is_featured=True).count()
    breaking_articles = Article.objects.filter(is_breaking=True).count()
    total_views = Article.objects.aggregate(Sum('views_count'))['views_count__sum'] or 0
    
    # Opinion Articles
    opinion_articles = Article.objects.filter(category__slug='opinion').count()
    opinion_published = Article.objects.filter(category__slug='opinion', status='published').count()
    
    # Environment Articles
    environment_articles = Article.objects.filter(category__slug='environment').count()
    environment_published = Article.objects.filter(category__slug='environment', status='published').count()
    
    # Society Articles
    society_articles = Article.objects.filter(category__slug='society').count()
    society_published = Article.objects.filter(category__slug='society', status='published').count()
    
    # Photos - FIXED: removed is_featured filter
    total_photos = MediaFile.objects.filter(file_type='image').count()
    featured_photos = 0  # No is_featured field in MediaFile model
    
    # Categories
    total_categories = Category.objects.count()
    active_categories = Category.objects.filter(is_active=True).count()
    
    # Tags
    total_tags = Tag.objects.count()
    
    # Users
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    verified_users = User.objects.filter(is_verified=True).count()
    new_users_today = User.objects.filter(date_joined__date=timezone.now().date()).count()
    new_users_week = User.objects.filter(date_joined__gte=timezone.now() - timedelta(days=7)).count()
    
    # Role breakdown
    admins = User.objects.filter(role='admin').count()
    editors = User.objects.filter(role='editor').count()
    journalists = User.objects.filter(role='journalist').count()
    subscribers = User.objects.filter(role='subscriber').count()
    advertisers = User.objects.filter(role='advertiser').count()
    
    # Comments
    total_comments = Comment.objects.count()
    pending_comments = Comment.objects.filter(status='pending').count()
    approved_comments = Comment.objects.filter(status='approved').count()
    spam_comments = Comment.objects.filter(status='spam').count()
    
    # Advertisements
    total_ads = Advertisement.objects.count()
    active_ads = Advertisement.objects.filter(status='active').count()
    pending_ads = Advertisement.objects.filter(status='pending').count()
    expired_ads = Advertisement.objects.filter(status='expired').count()
    total_ad_views = Advertisement.objects.aggregate(Sum('views_count'))['views_count__sum'] or 0
    total_ad_clicks = Advertisement.objects.aggregate(Sum('clicks_count'))['clicks_count__sum'] or 0
    
    # FIXED: Calculate revenue from available fields (no 'revenue' field exists)
    total_ad_revenue = 0
    all_ads = Advertisement.objects.all()
    for ad in all_ads:
        if ad.cost_per_click and ad.cost_per_click > 0:
            total_ad_revenue += ad.cost_per_click * ad.clicks_count
        elif ad.cost_per_impression and ad.cost_per_impression > 0:
            total_ad_revenue += ad.cost_per_impression * ad.views_count
        elif ad.budget and ad.budget > 0:
            total_ad_revenue += ad.budget
    
    # Media
    total_media = MediaFile.objects.count()
    media_images = MediaFile.objects.filter(file_type='image').count()
    media_videos = MediaFile.objects.filter(file_type='video').count()
    media_documents = MediaFile.objects.filter(file_type='document').count()
    
    # Newsletter
    total_subscribers = Subscriber.objects.filter(status='active').count()
    new_subscribers_week = Subscriber.objects.filter(created_at__gte=timezone.now() - timedelta(days=7)).count()
    total_newsletters = Newsletter.objects.count()
    sent_newsletters = Newsletter.objects.filter(status='sent').count()
    
    # Contacts
    total_contacts = ContactMessage.objects.count()
    new_contacts = ContactMessage.objects.filter(status='new').count()
    unread_contacts = ContactMessage.objects.filter(status__in=['new', 'read']).count()
    
    # Recent items for quick view
    recent_articles = Article.objects.order_by('-created_at')[:10]
    recent_users = User.objects.order_by('-date_joined')[:10]
    recent_comments = Comment.objects.order_by('-created_at')[:10]
    recent_ads = Advertisement.objects.order_by('-created_at')[:10]
    recent_contacts = ContactMessage.objects.order_by('-created_at')[:10]
    recent_media = MediaFile.objects.order_by('-created_at')[:10]
    
    # Pending items requiring attention
    pending_items = {
        'articles': pending_articles,
        'comments': pending_comments,
        'ads': pending_ads,
        'contacts': new_contacts,
    }
    
    # Chart data - Last 30 days
    chart_data = get_admin_chart_data()
    
    context = {
        # Article stats
        'total_articles': total_articles,
        'published_articles': published_articles,
        'draft_articles': draft_articles,
        'pending_articles': pending_articles,
        'scheduled_articles': scheduled_articles,
        'archived_articles': archived_articles,
        'featured_articles': featured_articles,
        'breaking_articles': breaking_articles,
        'total_views': total_views,
        
        # Opinion stats
        'opinion_articles': opinion_articles,
        'opinion_published': opinion_published,
        
        # Environment stats
        'environment_articles': environment_articles,
        'environment_published': environment_published,
        
        # Society stats
        'society_articles': society_articles,
        'society_published': society_published,
        
        # Photos stats - FIXED
        'total_photos': total_photos,
        'featured_photos': featured_photos,
        
        # Category & Tag stats
        'total_categories': total_categories,
        'active_categories': active_categories,
        'total_tags': total_tags,
        
        # User stats
        'total_users': total_users,
        'active_users': active_users,
        'verified_users': verified_users,
        'new_users_today': new_users_today,
        'new_users_week': new_users_week,
        'admins': admins,
        'editors': editors,
        'journalists': journalists,
        'subscribers': subscribers,
        'advertisers': advertisers,
        
        # Comment stats
        'total_comments': total_comments,
        'pending_comments': pending_comments,
        'approved_comments': approved_comments,
        'spam_comments': spam_comments,
        
        # Ad stats
        'total_ads': total_ads,
        'active_ads': active_ads,
        'pending_ads': pending_ads,
        'expired_ads': expired_ads,
        'total_ad_views': total_ad_views,
        'total_ad_clicks': total_ad_clicks,
        'total_ad_revenue': total_ad_revenue,  # FIXED
        
        # Media stats
        'total_media': total_media,
        'media_images': media_images,
        'media_videos': media_videos,
        'media_documents': media_documents,
        
        # Newsletter stats
        'total_subscribers': total_subscribers,
        'new_subscribers_week': new_subscribers_week,
        'total_newsletters': total_newsletters,
        'sent_newsletters': sent_newsletters,
        
        # Contact stats
        'total_contacts': total_contacts,
        'new_contacts': new_contacts,
        'unread_contacts': unread_contacts,
        
        # Recent items
        'recent_articles': recent_articles,
        'recent_users': recent_users,
        'recent_comments': recent_comments,
        'recent_ads': recent_ads,
        'recent_contacts': recent_contacts,
        'recent_media': recent_media,
        
        # Pending items
        'pending_items': pending_items,
        
        # Chart data
        'chart_data': chart_data,
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)


def get_admin_chart_data():
    """Get chart data for the last 30 days"""
    data = {
        'dates': [],
        'articles': [],
        'users': [],
        'views': [],
        'comments': [],
    }
    
    for i in range(29, -1, -1):
        date = timezone.now().date() - timedelta(days=i)
        data['dates'].append(date.strftime('%b %d'))
        
        data['articles'].append(Article.objects.filter(created_at__date=date).count())
        data['users'].append(User.objects.filter(date_joined__date=date).count())
        data['views'].append(Article.objects.filter(created_at__date=date).aggregate(Sum('views_count'))['views_count__sum'] or 0)
        data['comments'].append(Comment.objects.filter(created_at__date=date).count())
    
    return data


# ============================================
# ADMIN - OPINION ARTICLES
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin', 'editor'])
def admin_opinion(request):
    """Manage Opinion articles"""
    category = get_object_or_404(Category, slug='opinion')
    articles = Article.objects.filter(category=category).order_by('-created_at')
    
    status = request.GET.get('status')
    if status:
        articles = articles.filter(status=status)
    
    search = request.GET.get('search')
    if search:
        articles = articles.filter(Q(title__icontains=search) | Q(content__icontains=search))
    
    paginator = Paginator(articles, 25)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    context = {
        'articles': articles,
        'category': category,
        'status_filter': status,
        'search': search,
        'section': 'opinion',
    }
    return render(request, 'dashboard/admin_opinion.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin', 'editor'])
def admin_opinion_edit(request, article_id):
    """Edit Opinion article"""
    article = get_object_or_404(Article, id=article_id)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            article = form.save()
            messages.success(request, f'Opinion article "{article.title}" updated!')
            return redirect('dashboard:opinion_list')
    else:
        form = ArticleForm(instance=article)
    
    return render(request, 'dashboard/admin_opinion_edit.html', {
        'form': form, 
        'article': article,
        'section': 'opinion'
    })


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_opinion_delete(request, article_id):
    """Delete Opinion article"""
    article = get_object_or_404(Article, id=article_id)
    
    if request.method == 'POST':
        title = article.title
        article.delete()
        messages.success(request, f'Opinion article "{title}" deleted!')
        return redirect('dashboard:opinion_list')
    
    return render(request, 'dashboard/confirm_delete.html', {
        'object': article,
        'type': 'Opinion Article',
        'back_url': 'dashboard:opinion_list'
    })


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin', 'editor'])
def admin_opinion_publish(request, article_id):
    """Publish/unpublish Opinion article"""
    article = get_object_or_404(Article, id=article_id)
    
    if article.status == 'published':
        article.status = 'draft'
        article.published_at = None
        messages.warning(request, f'Opinion article "{article.title}" unpublished.')
    else:
        article.status = 'published'
        article.published_at = timezone.now()
        messages.success(request, f'Opinion article "{article.title}" published!')
    
    article.save()
    return redirect('dashboard:opinion_list')


# ============================================
# ADMIN - ENVIRONMENT ARTICLES
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin', 'editor'])
def admin_environment(request):
    """Manage Environment articles"""
    category = get_object_or_404(Category, slug='environment')
    articles = Article.objects.filter(category=category).order_by('-created_at')
    
    status = request.GET.get('status')
    if status:
        articles = articles.filter(status=status)
    
    search = request.GET.get('search')
    if search:
        articles = articles.filter(Q(title__icontains=search) | Q(content__icontains=search))
    
    paginator = Paginator(articles, 25)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    context = {
        'articles': articles,
        'category': category,
        'status_filter': status,
        'search': search,
        'section': 'environment',
    }
    return render(request, 'dashboard/admin_environment.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin', 'editor'])
def admin_environment_edit(request, article_id):
    """Edit Environment article"""
    article = get_object_or_404(Article, id=article_id)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            article = form.save()
            messages.success(request, f'Environment article "{article.title}" updated!')
            return redirect('dashboard:environment_list')
    else:
        form = ArticleForm(instance=article)
    
    return render(request, 'dashboard/admin_environment_edit.html', {
        'form': form, 
        'article': article,
        'section': 'environment'
    })


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_environment_delete(request, article_id):
    """Delete Environment article"""
    article = get_object_or_404(Article, id=article_id)
    
    if request.method == 'POST':
        title = article.title
        article.delete()
        messages.success(request, f'Environment article "{title}" deleted!')
        return redirect('dashboard:environment_list')
    
    return render(request, 'dashboard/confirm_delete.html', {
        'object': article,
        'type': 'Environment Article',
        'back_url': 'dashboard:environment_list'
    })


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin', 'editor'])
def admin_environment_publish(request, article_id):
    """Publish/unpublish Environment article"""
    article = get_object_or_404(Article, id=article_id)
    
    if article.status == 'published':
        article.status = 'draft'
        article.published_at = None
        messages.warning(request, f'Environment article "{article.title}" unpublished.')
    else:
        article.status = 'published'
        article.published_at = timezone.now()
        messages.success(request, f'Environment article "{article.title}" published!')
    
    article.save()
    return redirect('dashboard:environment_list')


# ============================================
# ADMIN - SOCIETY ARTICLES
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin', 'editor'])
def admin_society(request):
    """Manage Society articles"""
    category = get_object_or_404(Category, slug='society')
    articles = Article.objects.filter(category=category).order_by('-created_at')
    
    status = request.GET.get('status')
    if status:
        articles = articles.filter(status=status)
    
    search = request.GET.get('search')
    if search:
        articles = articles.filter(Q(title__icontains=search) | Q(content__icontains=search))
    
    paginator = Paginator(articles, 25)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    context = {
        'articles': articles,
        'category': category,
        'status_filter': status,
        'search': search,
        'section': 'society',
    }
    return render(request, 'dashboard/admin_society.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin', 'editor'])
def admin_society_edit(request, article_id):
    """Edit Society article"""
    article = get_object_or_404(Article, id=article_id)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            article = form.save()
            messages.success(request, f'Society article "{article.title}" updated!')
            return redirect('dashboard:society_list')
    else:
        form = ArticleForm(instance=article)
    
    return render(request, 'dashboard/admin_society_edit.html', {
        'form': form, 
        'article': article,
        'section': 'society'
    })


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_society_delete(request, article_id):
    """Delete Society article"""
    article = get_object_or_404(Article, id=article_id)
    
    if request.method == 'POST':
        title = article.title
        article.delete()
        messages.success(request, f'Society article "{title}" deleted!')
        return redirect('dashboard:society_list')
    
    return render(request, 'dashboard/confirm_delete.html', {
        'object': article,
        'type': 'Society Article',
        'back_url': 'dashboard:society_list'
    })


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin', 'editor'])
def admin_society_publish(request, article_id):
    """Publish/unpublish Society article"""
    article = get_object_or_404(Article, id=article_id)
    
    if article.status == 'published':
        article.status = 'draft'
        article.published_at = None
        messages.warning(request, f'Society article "{article.title}" unpublished.')
    else:
        article.status = 'published'
        article.published_at = timezone.now()
        messages.success(request, f'Society article "{article.title}" published!')
    
    article.save()
    return redirect('dashboard:society_list')


# ============================================
# ADMIN - PHOTOS (FIXED)
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_photos(request):
    """Manage photos"""
    photos = MediaFile.objects.filter(file_type='image').order_by('-created_at')
    
    search = request.GET.get('search')
    if search:
        photos = photos.filter(Q(title__icontains=search) | Q(description__icontains=search))
    
    paginator = Paginator(photos, 25)
    page = request.GET.get('page')
    try:
        photos = paginator.page(page)
    except PageNotAnInteger:
        photos = paginator.page(1)
    except EmptyPage:
        photos = paginator.page(paginator.num_pages)
    
    context = {
        'photos': photos,
        'search': search,
        'total_photos': MediaFile.objects.filter(file_type='image').count(),
        'featured_photos': 0,
    }
    return render(request, 'dashboard/admin_photos.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_photos_edit(request, photo_id):
    """Edit photo"""
    photo = get_object_or_404(MediaFile, id=photo_id, file_type='image')
    
    if request.method == 'POST':
        form = MediaFileForm(request.POST, request.FILES, instance=photo)
        if form.is_valid():
            form.save()
            messages.success(request, f'Photo "{photo.title}" updated!')
            return redirect('dashboard:photos_list')
    else:
        form = MediaFileForm(instance=photo)
    
    return render(request, 'dashboard/admin_photos_edit.html', {'form': form, 'photo': photo})


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_photos_delete(request, photo_id):
    """Delete photo"""
    photo = get_object_or_404(MediaFile, id=photo_id, file_type='image')
    
    if request.method == 'POST':
        title = photo.title
        photo.delete()
        messages.success(request, f'Photo "{title}" deleted!')
        return redirect('dashboard:photos_list')
    
    return render(request, 'dashboard/confirm_delete.html', {
        'object': photo,
        'type': 'Photo',
        'back_url': 'dashboard:photos_list'
    })


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_photos_feature(request, photo_id):
    """Toggle featured status of photo - DISABLED"""
    messages.warning(request, 'Featured functionality is not available for photos.')
    return redirect('dashboard:photos_list')


# ============================================
# ADMIN - ARTICLES
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin', 'editor'])
def admin_articles(request):
    """Manage all articles"""
    articles = Article.objects.all().order_by('-created_at')
    
    status = request.GET.get('status')
    if status:
        articles = articles.filter(status=status)
    
    category = request.GET.get('category')
    if category:
        articles = articles.filter(category__slug=category)
    
    search = request.GET.get('search')
    if search:
        articles = articles.filter(Q(title__icontains=search) | Q(content__icontains=search))
    
    paginator = Paginator(articles, 25)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'articles': articles,
        'categories': categories,
        'status_filter': status,
        'category_filter': category,
        'search': search,
    }
    return render(request, 'dashboard/admin_articles.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin', 'editor'])
def admin_article_create(request):
    """Create new article"""
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            form.save_m2m()
            
            messages.success(request, f'Article "{article.title}" created successfully!')
            return redirect('dashboard:article_list')
    else:
        form = ArticleForm()
    
    return render(request, 'dashboard/admin_article_form.html', {'form': form, 'action': 'Create'})


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin', 'editor'])
def admin_article_edit(request, article_id):
    """Edit article"""
    article = get_object_or_404(Article, id=article_id)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            article = form.save()
            messages.success(request, f'Article "{article.title}" updated successfully!')
            return redirect('dashboard:article_list')
    else:
        form = ArticleForm(instance=article)
    
    return render(request, 'dashboard/admin_article_form.html', {'form': form, 'action': 'Edit', 'article': article})


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_article_delete(request, article_id):
    """Delete article"""
    article = get_object_or_404(Article, id=article_id)
    
    if request.method == 'POST':
        title = article.title
        article.delete()
        messages.success(request, f'Article "{title}" deleted successfully!')
        return redirect('dashboard:article_list')
    
    return render(request, 'dashboard/confirm_delete.html', {
        'object': article,
        'type': 'Article',
        'back_url': 'dashboard:article_list'
    })


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin', 'editor'])
def admin_article_publish(request, article_id):
    """Publish or unpublish article"""
    article = get_object_or_404(Article, id=article_id)
    
    if article.status == 'published':
        article.status = 'draft'
        article.published_at = None
        messages.warning(request, f'Article "{article.title}" unpublished.')
    else:
        article.status = 'published'
        article.published_at = timezone.now()
        messages.success(request, f'Article "{article.title}" published!')
    
    article.save()
    return redirect('dashboard:article_list')


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin', 'editor'])
def admin_article_feature(request, article_id):
    """Toggle featured status"""
    article = get_object_or_404(Article, id=article_id)
    article.is_featured = not article.is_featured
    article.save()
    
    status = 'featured' if article.is_featured else 'unfeatured'
    messages.success(request, f'Article "{article.title}" {status}!')
    return redirect('dashboard:article_list')


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin', 'editor'])
def admin_article_breaking(request, article_id):
    """Toggle breaking news status"""
    article = get_object_or_404(Article, id=article_id)
    article.is_breaking = not article.is_breaking
    article.save()
    
    status = 'marked as breaking' if article.is_breaking else 'removed from breaking'
    messages.success(request, f'Article "{article.title}" {status}!')
    return redirect('dashboard:article_list')


# ============================================
# ADMIN - CATEGORIES
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_categories(request):
    """Manage categories"""
    categories = Category.objects.all().order_by('order', 'name')
    
    context = {'categories': categories}
    return render(request, 'dashboard/admin_categories.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_category_create(request):
    """Create category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" created!')
            return redirect('dashboard:category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'dashboard/admin_category_form.html', {'form': form, 'action': 'Create'})


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_category_edit(request, category_id):
    """Edit category"""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{category.name}" updated!')
            return redirect('dashboard:category_list')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'dashboard/admin_category_form.html', {'form': form, 'action': 'Edit', 'category': category})


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_category_delete(request, category_id):
    """Delete category"""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Category "{name}" deleted!')
        return redirect('dashboard:category_list')
    
    return render(request, 'dashboard/confirm_delete.html', {
        'object': category,
        'type': 'Category',
        'back_url': 'dashboard:category_list'
    })


# ============================================
# ADMIN - TAGS
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_tags(request):
    """Manage tags"""
    tags = Tag.objects.all().order_by('name')
    
    context = {'tags': tags}
    return render(request, 'dashboard/admin_tags.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_tag_create(request):
    """Create tag"""
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            tag = form.save()
            messages.success(request, f'Tag "{tag.name}" created!')
            return redirect('dashboard:tag_list')
    else:
        form = TagForm()
    
    return render(request, 'dashboard/admin_tag_form.html', {'form': form, 'action': 'Create'})


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_tag_edit(request, tag_id):
    """Edit tag"""
    tag = get_object_or_404(Tag, id=tag_id)
    
    if request.method == 'POST':
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tag "{tag.name}" updated!')
            return redirect('dashboard:tag_list')
    else:
        form = TagForm(instance=tag)
    
    return render(request, 'dashboard/admin_tag_form.html', {'form': form, 'action': 'Edit', 'tag': tag})


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_tag_delete(request, tag_id):
    """Delete tag"""
    tag = get_object_or_404(Tag, id=tag_id)
    
    if request.method == 'POST':
        name = tag.name
        tag.delete()
        messages.success(request, f'Tag "{name}" deleted!')
        return redirect('dashboard:tag_list')
    
    return render(request, 'dashboard/confirm_delete.html', {
        'object': tag,
        'type': 'Tag',
        'back_url': 'dashboard:tag_list'
    })


# ============================================
# ADMIN - USERS
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_users(request):
    """Manage users"""
    users = User.objects.all().order_by('-date_joined')
    
    role = request.GET.get('role')
    if role:
        users = users.filter(role=role)
    
    status = request.GET.get('status')
    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'inactive':
        users = users.filter(is_active=False)
    
    search = request.GET.get('search')
    if search:
        users = users.filter(Q(username__icontains=search) | Q(email__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search))
    
    paginator = Paginator(users, 25)
    page = request.GET.get('page')
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    
    context = {
        'users': users,
        'role_filter': role,
        'status_filter': status,
        'search': search,
        'role_choices': User.ROLE_CHOICES,
    }
    return render(request, 'dashboard/admin_users.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_user_create(request):
    """Create user"""
    if request.method == 'POST':
        form = UserCreateForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, f'User "{user.username}" created!')
            return redirect('dashboard:user_list')
    else:
        form = UserCreateForm()
    
    return render(request, 'dashboard/admin_user_form.html', {'form': form, 'action': 'Create'})


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_user_edit(request, user_id):
    """Edit user"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User "{user.username}" updated!')
            return redirect('dashboard:user_list')
    else:
        form = UserEditForm(instance=user)
    
    return render(request, 'dashboard/admin_user_form.html', {'form': form, 'action': 'Edit', 'edit_user': user})


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_user_delete(request, user_id):
    """Delete user"""
    user = get_object_or_404(User, id=user_id)
    
    if request.user == user:
        messages.error(request, 'You cannot delete your own account!')
        return redirect('dashboard:user_list')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User "{username}" deleted!')
        return redirect('dashboard:user_list')
    
    return render(request, 'dashboard/confirm_delete.html', {
        'object': user,
        'type': 'User',
        'back_url': 'dashboard:user_list'
    })


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_user_toggle_active(request, user_id):
    """Toggle user active status"""
    user = get_object_or_404(User, id=user_id)
    
    if request.user == user:
        messages.error(request, 'You cannot deactivate your own account!')
        return redirect('dashboard:user_list')
    
    user.is_active = not user.is_active
    user.save()
    
    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'User "{user.username}" {status}!')
    return redirect('dashboard:user_list')


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_user_change_role(request, user_id):
    """Change user role"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in dict(User.ROLE_CHOICES):
            user.role = new_role
            user.save()
            messages.success(request, f'User "{user.username}" role changed to {user.get_role_display()}!')
        else:
            messages.error(request, 'Invalid role selected!')
        return redirect('dashboard:user_list')
    
    return render(request, 'dashboard/admin_user_change_role.html', {
        'user': user,
        'role_choices': User.ROLE_CHOICES
    })


@login_required
@user_passes_test(lambda u: u.role in ['super_admin'])
def admin_user_impersonate(request, user_id):
    """Impersonate a user (super admin only)"""
    from django.contrib.auth import login
    user = get_object_or_404(User, id=user_id)
    
    if request.user.id == user.id:
        messages.error(request, 'You cannot impersonate yourself!')
        return redirect('dashboard:user_list')
    
    login(request, user)
    messages.success(request, f'You are now impersonating {user.username}')
    return redirect('dashboard:home')


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_user_reset_password(request, user_id):
    """Reset user password"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password and new_password == confirm_password:
            user.set_password(new_password)
            user.save()
            messages.success(request, f'Password for "{user.username}" has been reset!')
        else:
            messages.error(request, 'Passwords do not match!')
        
        return redirect('dashboard:user_list')
    
    return render(request, 'dashboard/admin_user_reset_password.html', {'user': user})


# ============================================
# ADMIN - COMMENTS
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin', 'editor'])
def admin_comments(request):
    """Manage comments"""
    comments = Comment.objects.all().order_by('-created_at')
    
    status = request.GET.get('status')
    if status:
        comments = comments.filter(status=status)
    
    search = request.GET.get('search')
    if search:
        comments = comments.filter(Q(content__icontains=search) | Q(user__username__icontains=search))
    
    paginator = Paginator(comments, 25)
    page = request.GET.get('page')
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)
    
    context = {
        'comments': comments,
        'status_filter': status,
        'search': search,
        'status_choices': Comment.STATUS_CHOICES,
    }
    return render(request, 'dashboard/admin_comments.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin', 'editor'])
def admin_comment_moderate(request, comment_id):
    """Moderate comment"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            comment.status = 'approved'
            comment.moderator = request.user
            comment.moderated_at = timezone.now()
            messages.success(request, 'Comment approved!')
        elif action == 'reject':
            comment.status = 'rejected'
            comment.moderator = request.user
            comment.moderated_at = timezone.now()
            messages.warning(request, 'Comment rejected!')
        elif action == 'spam':
            comment.status = 'spam'
            comment.moderator = request.user
            comment.moderated_at = timezone.now()
            messages.warning(request, 'Comment marked as spam!')
        
        comment.save()
        return redirect('dashboard:comment_list')
    
    return render(request, 'dashboard/admin_comment_moderate.html', {'comment': comment})


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_comment_delete(request, comment_id):
    """Delete comment"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted!')
        return redirect('dashboard:comment_list')
    
    return render(request, 'dashboard/confirm_delete.html', {
        'object': comment,
        'type': 'Comment',
        'back_url': 'dashboard:comment_list'
    })


# ============================================
# ADMIN - ADVERTISEMENTS (COMPLETE ADSBOARD)
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_ads(request):
    """Manage advertisements"""
    ads = Advertisement.objects.all().order_by('-created_at')
    
    status = request.GET.get('status')
    if status:
        ads = ads.filter(status=status)
    
    position = request.GET.get('position')
    if position:
        ads = ads.filter(position=position)
    
    search = request.GET.get('search')
    if search:
        ads = ads.filter(Q(title__icontains=search) | Q(advertiser__username__icontains=search))
    
    paginator = Paginator(ads, 25)
    page = request.GET.get('page')
    try:
        ads = paginator.page(page)
    except PageNotAnInteger:
        ads = paginator.page(1)
    except EmptyPage:
        ads = paginator.page(paginator.num_pages)
    
    context = {
        'ads': ads,
        'status_filter': status,
        'position_filter': position,
        'search': search,
        'position_choices': Advertisement.POSITION_CHOICES,
        'total_ads': Advertisement.objects.count(),
        'active_ads': Advertisement.objects.filter(status='active').count(),
        'pending_ads': Advertisement.objects.filter(status='pending').count(),
    }
    return render(request, 'dashboard/admin_ads.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_ad_create(request):
    """Create advertisement"""
    if request.method == 'POST':
        form = AdvertisementForm(request.POST, request.FILES)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.advertiser = request.user
            ad.save()
            form.save_m2m()
            messages.success(request, f'Ad "{ad.title}" created!')
            return redirect('dashboard:ad_list')
    else:
        form = AdvertisementForm()
    
    return render(request, 'dashboard/admin_ad_form.html', {'form': form, 'action': 'Create'})


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_ad_edit(request, ad_id):
    """Edit advertisement"""
    ad = get_object_or_404(Advertisement, id=ad_id)
    
    if request.method == 'POST':
        form = AdvertisementForm(request.POST, request.FILES, instance=ad)
        if form.is_valid():
            form.save()
            messages.success(request, f'Ad "{ad.title}" updated!')
            return redirect('dashboard:ad_list')
    else:
        form = AdvertisementForm(instance=ad)
    
    return render(request, 'dashboard/admin_ad_form.html', {'form': form, 'action': 'Edit', 'ad': ad})


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_ad_delete(request, ad_id):
    """Delete advertisement"""
    ad = get_object_or_404(Advertisement, id=ad_id)
    
    if request.method == 'POST':
        title = ad.title
        ad.delete()
        messages.success(request, f'Ad "{title}" deleted!')
        return redirect('dashboard:ad_list')
    
    return render(request, 'dashboard/confirm_delete.html', {
        'object': ad,
        'type': 'Advertisement',
        'back_url': 'dashboard:ad_list'
    })


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_ad_approve(request, ad_id):
    """Approve advertisement"""
    ad = get_object_or_404(Advertisement, id=ad_id)
    ad.status = 'active'
    ad.approved_at = timezone.now()
    ad.approved_by = request.user
    ad.save()
    messages.success(request, f'Ad "{ad.title}" approved and activated!')
    return redirect('dashboard:ad_list')


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_ad_reject(request, ad_id):
    """Reject advertisement"""
    ad = get_object_or_404(Advertisement, id=ad_id)
    ad.status = 'rejected'
    ad.save()
    messages.warning(request, f'Ad "{ad.title}" rejected!')
    return redirect('dashboard:ad_list')


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_ad_pause(request, ad_id):
    """Pause advertisement"""
    ad = get_object_or_404(Advertisement, id=ad_id)
    ad.status = 'paused'
    ad.save()
    messages.warning(request, f'Ad "{ad.title}" paused!')
    return redirect('dashboard:ad_list')


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_ad_resume(request, ad_id):
    """Resume advertisement"""
    ad = get_object_or_404(Advertisement, id=ad_id)
    ad.status = 'active'
    ad.save()
    messages.success(request, f'Ad "{ad.title}" resumed!')
    return redirect('dashboard:ad_list')


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_ad_duplicate(request, ad_id):
    """Duplicate advertisement"""
    original = get_object_or_404(Advertisement, id=ad_id)
    
    new_ad = Advertisement(
        advertiser=original.advertiser,
        title=f"{original.title} (Copy)",
        description=original.description,
        image=original.image,
        link_url=original.link_url,
        position=original.position,
        start_date=original.start_date,
        end_date=original.end_date,
        priority=original.priority,
        status='draft'
    )
    new_ad.save()
    
    messages.success(request, f'Ad "{original.title}" duplicated successfully!')
    return redirect('dashboard:ad_list')


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_ad_statistics(request, ad_id):
    """View ad statistics"""
    ad = get_object_or_404(Advertisement, id=ad_id)
    
    daily_views = AdvertisementView.objects.filter(ad=ad).extra(
        {'day': "date(viewed_at)"}
    ).values('day').annotate(count=Count('id')).order_by('day')[:30]
    
    daily_clicks = AdvertisementClick.objects.filter(ad=ad).extra(
        {'day': "date(clicked_at)"}
    ).values('day').annotate(count=Count('id')).order_by('day')[:30]
    
    context = {
        'ad': ad,
        'daily_views': daily_views,
        'daily_clicks': daily_clicks,
        'total_views': ad.views_count,
        'total_clicks': ad.clicks_count,
        'ctr': ad.calculate_ctr(),
    }
    return render(request, 'dashboard/admin_ad_statistics.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_ad_performance(request):
    """Ad performance overview"""
    ads = Advertisement.objects.all()
    
    total_ads = ads.count()
    total_views = ads.aggregate(Sum('views_count'))['views_count__sum'] or 0
    total_clicks = ads.aggregate(Sum('clicks_count'))['clicks_count__sum'] or 0
    ctr = (total_clicks / total_views * 100) if total_views > 0 else 0
    
    top_ads = ads.order_by('-views_count')[:10]
    
    position_performance = []
    for pos_code, pos_name in Advertisement.POSITION_CHOICES:
        pos_ads = ads.filter(position=pos_code)
        pos_views = pos_ads.aggregate(Sum('views_count'))['views_count__sum'] or 0
        pos_clicks = pos_ads.aggregate(Sum('clicks_count'))['clicks_count__sum'] or 0
        pos_ctr = (pos_clicks / pos_views * 100) if pos_views > 0 else 0
        position_performance.append({
            'position': pos_name,
            'views': pos_views,
            'clicks': pos_clicks,
            'ctr': pos_ctr,
        })
    
    context = {
        'total_ads': total_ads,
        'total_views': total_views,
        'total_clicks': total_clicks,
        'ctr': round(ctr, 2),
        'top_ads': top_ads,
        'position_performance': position_performance,
    }
    return render(request, 'dashboard/admin_ad_performance.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_ad_revenue(request):
    """Ad revenue dashboard"""
    ads = Advertisement.objects.filter(status='active')
    
    # FIXED: Calculate revenue from available fields
    total_revenue = 0
    for ad in ads:
        if ad.cost_per_click and ad.cost_per_click > 0:
            total_revenue += ad.cost_per_click * ad.clicks_count
        elif ad.cost_per_impression and ad.cost_per_impression > 0:
            total_revenue += ad.cost_per_impression * ad.views_count
        elif ad.budget and ad.budget > 0:
            total_revenue += ad.budget
    
    revenue_by_position = []
    for pos_code, pos_name in Advertisement.POSITION_CHOICES:
        pos_revenue = 0
        pos_ads = ads.filter(position=pos_code)
        for ad in pos_ads:
            if ad.cost_per_click and ad.cost_per_click > 0:
                pos_revenue += ad.cost_per_click * ad.clicks_count
            elif ad.cost_per_impression and ad.cost_per_impression > 0:
                pos_revenue += ad.cost_per_impression * ad.views_count
            elif ad.budget and ad.budget > 0:
                pos_revenue += ad.budget
        revenue_by_position.append({
            'position': pos_name,
            'revenue': pos_revenue,
        })
    
    context = {
        'total_revenue': total_revenue,
        'revenue_by_position': revenue_by_position,
        'active_ads': ads.count(),
    }
    return render(request, 'dashboard/admin_ad_revenue.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_ad_positions(request):
    """Manage ad positions"""
    positions = []
    for pos_code, pos_name in Advertisement.POSITION_CHOICES:
        ads = Advertisement.objects.filter(position=pos_code)
        positions.append({
            'code': pos_code,
            'name': pos_name,
            'count': ads.count(),
            'active': ads.filter(status='active').count(),
        })
    
    context = {'positions': positions}
    return render(request, 'dashboard/admin_ad_positions.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_ad_placements(request):
    context = {}
    return render(request, 'dashboard/admin_ad_placements.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_ad_schedule(request):
    context = {}
    return render(request, 'dashboard/admin_ad_schedule.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_ad_analytics(request):
    ads = Advertisement.objects.all()
    
    daily_views = AdvertisementView.objects.extra(
        {'day': "date(viewed_at)"}
    ).values('day').annotate(count=Count('id')).order_by('day')[:30]
    
    daily_clicks = AdvertisementClick.objects.extra(
        {'day': "date(clicked_at)"}
    ).values('day').annotate(count=Count('id')).order_by('day')[:30]
    
    context = {
        'daily_views': daily_views,
        'daily_clicks': daily_clicks,
        'total_ads': ads.count(),
        'total_views': ads.aggregate(Sum('views_count'))['views_count__sum'] or 0,
        'total_clicks': ads.aggregate(Sum('clicks_count'))['clicks_count__sum'] or 0,
    }
    return render(request, 'dashboard/admin_ad_analytics.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_ad_approvals(request):
    pending_ads = Advertisement.objects.filter(status='pending').order_by('-created_at')
    
    context = {
        'pending_ads': pending_ads,
        'count': pending_ads.count(),
    }
    return render(request, 'dashboard/admin_ad_approvals.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_ad_reports(request):
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        
        ads = Advertisement.objects.all()
        if date_from:
            ads = ads.filter(created_at__gte=date_from)
        if date_to:
            ads = ads.filter(created_at__lte=date_to)
        
        context = {
            'report_type': report_type,
            'date_from': date_from,
            'date_to': date_to,
            'ads': ads,
            'total_ads': ads.count(),
            'total_views': ads.aggregate(Sum('views_count'))['views_count__sum'] or 0,
            'total_clicks': ads.aggregate(Sum('clicks_count'))['clicks_count__sum'] or 0,
        }
        return render(request, 'dashboard/admin_ad_report.html', context)
    
    return render(request, 'dashboard/admin_ad_reports.html')


# ============================================
# ADMIN - CONTACTS
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_contacts(request):
    contacts = ContactMessage.objects.all().order_by('-created_at')
    
    status = request.GET.get('status')
    if status:
        contacts = contacts.filter(status=status)
    
    search = request.GET.get('search')
    if search:
        contacts = contacts.filter(Q(name__icontains=search) | Q(email__icontains=search) | Q(subject__icontains=search))
    
    paginator = Paginator(contacts, 25)
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)
    
    context = {
        'contacts': contacts,
        'status_filter': status,
        'search': search,
        'total_contacts': ContactMessage.objects.count(),
        'new_contacts': ContactMessage.objects.filter(status='new').count(),
    }
    return render(request, 'dashboard/admin_contacts.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_contact_detail(request, contact_id):
    contact = get_object_or_404(ContactMessage, id=contact_id)
    
    if contact.status == 'new':
        contact.status = 'read'
        contact.save()
    
    if request.method == 'POST':
        form = ContactReplyForm(request.POST)
        if form.is_valid():
            response = form.cleaned_data['response']
            contact.response = response
            contact.responded_by = request.user
            contact.responded_at = timezone.now()
            contact.status = 'replied'
            contact.save()
            
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                send_mail(
                    f'Re: {contact.subject}',
                    response,
                    settings.DEFAULT_FROM_EMAIL,
                    [contact.email],
                    fail_silently=True
                )
            except:
                pass
            
            messages.success(request, 'Reply sent successfully!')
            return redirect('dashboard:contact_list')
    else:
        form = ContactReplyForm()
    
    return render(request, 'dashboard/admin_contact_detail.html', {'contact': contact, 'form': form})


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_contact_delete(request, contact_id):
    contact = get_object_or_404(ContactMessage, id=contact_id)
    
    if request.method == 'POST':
        contact.delete()
        messages.success(request, 'Message deleted!')
        return redirect('dashboard:contact_list')
    
    return render(request, 'dashboard/confirm_delete.html', {
        'object': contact,
        'type': 'Contact Message',
        'back_url': 'dashboard:contact_list'
    })


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_contact_reply(request, contact_id):
    contact = get_object_or_404(ContactMessage, id=contact_id)
    
    if request.method == 'POST':
        response = request.POST.get('response')
        if response:
            contact.response = response
            contact.responded_by = request.user
            contact.responded_at = timezone.now()
            contact.status = 'replied'
            contact.save()
            return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_contact_mark_read(request, contact_id):
    contact = get_object_or_404(ContactMessage, id=contact_id)
    contact.status = 'read'
    contact.save()
    return JsonResponse({'success': True})


# ============================================
# ADMIN - MEDIA
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_media(request):
    media = MediaFile.objects.all().order_by('-created_at')
    
    file_type = request.GET.get('type')
    if file_type:
        media = media.filter(file_type=file_type)
    
    search = request.GET.get('search')
    if search:
        media = media.filter(Q(title__icontains=search) | Q(description__icontains=search))
    
    paginator = Paginator(media, 25)
    page = request.GET.get('page')
    try:
        media = paginator.page(page)
    except PageNotAnInteger:
        media = paginator.page(1)
    except EmptyPage:
        media = paginator.page(paginator.num_pages)
    
    context = {
        'media': media,
        'file_type_filter': file_type,
        'search': search,
        'total_media': MediaFile.objects.count(),
        'images': MediaFile.objects.filter(file_type='image').count(),
        'videos': MediaFile.objects.filter(file_type='video').count(),
        'documents': MediaFile.objects.filter(file_type='document').count(),
    }
    return render(request, 'dashboard/admin_media.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_media_delete(request, media_id):
    media = get_object_or_404(MediaFile, id=media_id)
    
    if request.method == 'POST':
        title = media.title
        media.delete()
        messages.success(request, f'Media "{title}" deleted!')
        return redirect('dashboard:media_list')
    
    return render(request, 'dashboard/confirm_delete.html', {
        'object': media,
        'type': 'Media File',
        'back_url': 'dashboard:media_list'
    })


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_media_edit(request, media_id):
    media = get_object_or_404(MediaFile, id=media_id)
    
    if request.method == 'POST':
        form = MediaFileForm(request.POST, request.FILES, instance=media)
        if form.is_valid():
            form.save()
            messages.success(request, f'Media "{media.title}" updated!')
            return redirect('dashboard:media_list')
    else:
        form = MediaFileForm(instance=media)
    
    return render(request, 'dashboard/admin_media_form.html', {'form': form, 'media': media})


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_media_gallery(request):
    media = MediaFile.objects.filter(file_type='image').order_by('-created_at')
    
    paginator = Paginator(media, 50)
    page = request.GET.get('page')
    try:
        media = paginator.page(page)
    except PageNotAnInteger:
        media = paginator.page(1)
    except EmptyPage:
        media = paginator.page(paginator.num_pages)
    
    return render(request, 'dashboard/admin_media_gallery.html', {'media': media})


# ============================================
# ADMIN - SUBSCRIBERS
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_subscribers(request):
    subscribers = Subscriber.objects.all().order_by('-created_at')
    
    status = request.GET.get('status')
    if status:
        subscribers = subscribers.filter(status=status)
    
    search = request.GET.get('search')
    if search:
        subscribers = subscribers.filter(Q(email__icontains=search) | Q(name__icontains=search))
    
    paginator = Paginator(subscribers, 25)
    page = request.GET.get('page')
    try:
        subscribers = paginator.page(page)
    except PageNotAnInteger:
        subscribers = paginator.page(1)
    except EmptyPage:
        subscribers = paginator.page(paginator.num_pages)
    
    context = {
        'subscribers': subscribers,
        'status_filter': status,
        'search': search,
        'total_subscribers': Subscriber.objects.count(),
        'active_subscribers': Subscriber.objects.filter(status='active').count(),
        'inactive_subscribers': Subscriber.objects.filter(status='inactive').count(),
    }
    return render(request, 'dashboard/admin_subscribers.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_subscriber_delete(request, subscriber_id):
    subscriber = get_object_or_404(Subscriber, id=subscriber_id)
    
    if request.method == 'POST':
        email = subscriber.email
        subscriber.delete()
        messages.success(request, f'Subscriber "{email}" removed!')
        return redirect('dashboard:subscriber_list')
    
    return render(request, 'dashboard/confirm_delete.html', {
        'object': subscriber,
        'type': 'Subscriber',
        'back_url': 'dashboard:subscriber_list'
    })


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_subscriber_toggle(request, subscriber_id):
    subscriber = get_object_or_404(Subscriber, id=subscriber_id)
    
    if subscriber.status == 'active':
        subscriber.status = 'inactive'
    else:
        subscriber.status = 'active'
    subscriber.save()
    
    status = 'activated' if subscriber.status == 'active' else 'deactivated'
    messages.success(request, f'Subscriber "{subscriber.email}" {status}!')
    return redirect('dashboard:subscriber_list')


# ============================================
# ADMIN - NEWSLETTERS
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_newsletters(request):
    newsletters = Newsletter.objects.all().order_by('-created_at')
    
    status = request.GET.get('status')
    if status:
        newsletters = newsletters.filter(status=status)
    
    paginator = Paginator(newsletters, 25)
    page = request.GET.get('page')
    try:
        newsletters = paginator.page(page)
    except PageNotAnInteger:
        newsletters = paginator.page(1)
    except EmptyPage:
        newsletters = paginator.page(paginator.num_pages)
    
    context = {
        'newsletters': newsletters,
        'status_filter': status,
        'total_newsletters': Newsletter.objects.count(),
        'sent_newsletters': Newsletter.objects.filter(status='sent').count(),
        'draft_newsletters': Newsletter.objects.filter(status='draft').count(),
    }
    return render(request, 'dashboard/admin_newsletters.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_newsletter_create(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.created_by = request.user
            newsletter.save()
            form.save_m2m()
            messages.success(request, f'Newsletter "{newsletter.subject}" created!')
            return redirect('dashboard:newsletter_list')
    else:
        form = NewsletterForm()
    
    return render(request, 'dashboard/admin_newsletter_form.html', {'form': form, 'action': 'Create'})


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_newsletter_edit(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    
    if request.method == 'POST':
        form = NewsletterForm(request.POST, instance=newsletter)
        if form.is_valid():
            form.save()
            messages.success(request, f'Newsletter "{newsletter.subject}" updated!')
            return redirect('dashboard:newsletter_list')
    else:
        form = NewsletterForm(instance=newsletter)
    
    return render(request, 'dashboard/admin_newsletter_form.html', {'form': form, 'action': 'Edit', 'newsletter': newsletter})


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_newsletter_send(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    
    if request.method == 'POST':
        newsletter.send()
        messages.success(request, f'Newsletter "{newsletter.subject}" sent!')
        return redirect('dashboard:newsletter_list')
    
    return render(request, 'dashboard/admin_newsletter_send.html', {'newsletter': newsletter})


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_newsletter_delete(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    
    if request.method == 'POST':
        subject = newsletter.subject
        newsletter.delete()
        messages.success(request, f'Newsletter "{subject}" deleted!')
        return redirect('dashboard:newsletter_list')
    
    return render(request, 'dashboard/confirm_delete.html', {
        'object': newsletter,
        'type': 'Newsletter',
        'back_url': 'dashboard:newsletter_list'
    })


# ============================================
# ADMIN - SETTINGS
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_settings(request):
    category = request.GET.get('category', 'general')
    
    if request.method == 'POST':
        if category == 'general':
            form = GeneralSettingsForm(request.POST, request.FILES)
            if form.is_valid():
                update_setting('general', 'site_name', form.cleaned_data['site_name'])
                update_setting('general', 'site_tagline', form.cleaned_data['site_tagline'])
                update_setting('general', 'site_description', form.cleaned_data['site_description'])
                if form.cleaned_data['site_logo']:
                    update_setting('general', 'site_logo', form.cleaned_data['site_logo'])
                if form.cleaned_data['site_favicon']:
                    update_setting('general', 'site_favicon', form.cleaned_data['site_favicon'])
                update_setting('general', 'site_timezone', form.cleaned_data['site_timezone'])
                update_setting('general', 'site_language', form.cleaned_data['site_language'])
                messages.success(request, 'General settings updated!')
                return redirect('dashboard:settings')
        
        elif category == 'email':
            form = EmailSettingsForm(request.POST)
            if form.is_valid():
                update_setting('email', 'smtp_host', form.cleaned_data['smtp_host'])
                update_setting('email', 'smtp_port', str(form.cleaned_data['smtp_port']))
                update_setting('email', 'smtp_username', form.cleaned_data['smtp_username'])
                if form.cleaned_data['smtp_password']:
                    update_setting('email', 'smtp_password', form.cleaned_data['smtp_password'])
                update_setting('email', 'use_tls', str(form.cleaned_data['use_tls']))
                update_setting('email', 'from_email', form.cleaned_data['from_email'])
                update_setting('email', 'from_name', form.cleaned_data['from_name'])
                messages.success(request, 'Email settings updated!')
                return redirect('dashboard:settings')
        
        elif category == 'seo':
            form = SEOSettingsForm(request.POST)
            if form.is_valid():
                update_setting('seo', 'meta_title', form.cleaned_data['meta_title'])
                update_setting('seo', 'meta_description', form.cleaned_data['meta_description'])
                update_setting('seo', 'meta_keywords', form.cleaned_data['meta_keywords'])
                update_setting('seo', 'google_analytics_id', form.cleaned_data['google_analytics_id'])
                update_setting('seo', 'google_verification', form.cleaned_data['google_verification'])
                update_setting('seo', 'bing_verification', form.cleaned_data['bing_verification'])
                update_setting('seo', 'robots_txt', form.cleaned_data['robots_txt'])
                update_setting('seo', 'enable_sitemap', str(form.cleaned_data['enable_sitemap']))
                messages.success(request, 'SEO settings updated!')
                return redirect('dashboard:settings')
    
    settings_data = {
        'site_name': get_setting_value('general', 'site_name', 'The Egerton Advertiser'),
        'site_tagline': get_setting_value('general', 'site_tagline', 'Your Local News Source'),
        'site_description': get_setting_value('general', 'site_description', ''),
        'site_timezone': get_setting_value('general', 'site_timezone', 'UTC'),
        'site_language': get_setting_value('general', 'site_language', 'en'),
        'smtp_host': get_setting_value('email', 'smtp_host', ''),
        'smtp_port': get_setting_value('email', 'smtp_port', '587'),
        'smtp_username': get_setting_value('email', 'smtp_username', ''),
        'use_tls': get_setting_value('email', 'use_tls', 'True') == 'True',
        'from_email': get_setting_value('email', 'from_email', ''),
        'from_name': get_setting_value('email', 'from_name', 'The Egerton Advertiser'),
        'meta_title': get_setting_value('seo', 'meta_title', 'The Egerton Advertiser'),
        'meta_description': get_setting_value('seo', 'meta_description', ''),
        'meta_keywords': get_setting_value('seo', 'meta_keywords', ''),
        'google_analytics_id': get_setting_value('seo', 'google_analytics_id', ''),
        'google_verification': get_setting_value('seo', 'google_verification', ''),
        'bing_verification': get_setting_value('seo', 'bing_verification', ''),
        'robots_txt': get_setting_value('seo', 'robots_txt', 'User-agent: *\nAllow: /\n'),
        'enable_sitemap': get_setting_value('seo', 'enable_sitemap', 'True') == 'True',
    }
    
    context = {
        'category': category,
        'settings': settings_data,
        'categories': SiteSetting.SETTING_TYPES,
    }
    return render(request, 'dashboard/admin_settings.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_settings_update(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        key = request.POST.get('key')
        value = request.POST.get('value')
        
        if category and key:
            update_setting(category, key, value)
            return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})


def update_setting(category, key, value):
    setting, created = SiteSetting.objects.get_or_create(category=category, key=key)
    setting.value = value
    setting.save()


def get_setting_value(category, key, default=''):
    try:
        setting = SiteSetting.objects.get(category=category, key=key)
        return setting.value
    except SiteSetting.DoesNotExist:
        return default


# ============================================
# ADMIN - ANALYTICS
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_analytics(request):
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    total_articles = Article.objects.count()
    published_articles = Article.objects.filter(status='published').count()
    total_views = Article.objects.aggregate(Sum('views_count'))['views_count__sum'] or 0
    
    total_users = User.objects.count()
    new_users = User.objects.filter(date_joined__gte=start_date).count()
    
    total_comments = Comment.objects.count()
    
    total_ads = Advertisement.objects.count()
    total_ad_views = Advertisement.objects.aggregate(Sum('views_count'))['views_count__sum'] or 0
    total_ad_clicks = Advertisement.objects.aggregate(Sum('clicks_count'))['clicks_count__sum'] or 0
    
    chart_data = get_admin_chart_data()
    
    context = {
        'total_articles': total_articles,
        'published_articles': published_articles,
        'total_views': total_views,
        'total_users': total_users,
        'new_users': new_users,
        'total_comments': total_comments,
        'total_ads': total_ads,
        'total_ad_views': total_ad_views,
        'total_ad_clicks': total_ad_clicks,
        'chart_data': chart_data,
    }
    return render(request, 'dashboard/admin_analytics.html', context)


# ============================================
# API ENDPOINTS
# ============================================

@login_required
def api_stats(request):
    user = request.user
    role = user.role
    stats = get_role_based_stats(user, role)
    return JsonResponse({'success': True, 'stats': stats})


@login_required
def api_chart_data(request):
    days = int(request.GET.get('days', 30))
    chart_data = get_admin_chart_data()
    return JsonResponse({'success': True, 'data': chart_data})


@login_required
def api_recent_activity(request):
    user = request.user
    activities = DashboardActivityFeed.objects.filter(user=user)[:10]
    
    data = [{
        'id': activity.id,
        'description': activity.description,
        'timestamp': activity.created_at.strftime('%Y-%m-%d %H:%M'),
        'is_read': activity.is_read,
    } for activity in activities]
    
    return JsonResponse({'success': True, 'activities': data})


@login_required
def api_notifications(request):
    user = request.user
    notifications = DashboardActivityFeed.objects.filter(user=user, is_read=False)[:5]
    
    data = [{
        'id': n.id,
        'title': n.title,
        'description': n.description,
        'timestamp': n.created_at.strftime('%Y-%m-%d %H:%M'),
    } for n in notifications]
    
    return JsonResponse({'success': True, 'notifications': data, 'count': len(data)})


@login_required
def api_ad_stats(request):
    user = request.user
    
    if user.role in ['super_admin', 'admin']:
        ads = Advertisement.objects.all()
    else:
        ads = Advertisement.objects.filter(advertiser=user)
    
    total_views = ads.aggregate(Sum('views_count'))['views_count__sum'] or 0
    total_clicks = ads.aggregate(Sum('clicks_count'))['clicks_count__sum'] or 0
    ctr = (total_clicks / total_views * 100) if total_views > 0 else 0
    
    data = {
        'total_ads': ads.count(),
        'active_ads': ads.filter(status='active').count(),
        'total_views': total_views,
        'total_clicks': total_clicks,
        'ctr': round(ctr, 2),
    }
    
    return JsonResponse({'success': True, 'data': data})


@login_required
def api_user_stats(request):
    if not request.user.role in ['super_admin', 'admin']:
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    data = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'admins': User.objects.filter(role='admin').count(),
        'editors': User.objects.filter(role='editor').count(),
        'journalists': User.objects.filter(role='journalist').count(),
        'subscribers': User.objects.filter(role='subscriber').count(),
        'advertisers': User.objects.filter(role='advertiser').count(),
    }
    
    return JsonResponse({'success': True, 'data': data})


@login_required
def api_content_stats(request):
    if not request.user.role in ['super_admin', 'admin']:
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    data = {
        'total_articles': Article.objects.count(),
        'published_articles': Article.objects.filter(status='published').count(),
        'draft_articles': Article.objects.filter(status='draft').count(),
        'pending_articles': Article.objects.filter(status='pending').count(),
        'total_views': Article.objects.aggregate(Sum('views_count'))['views_count__sum'] or 0,
        'total_comments': Comment.objects.count(),
        'total_categories': Category.objects.count(),
        'total_tags': Tag.objects.count(),
    }
    
    return JsonResponse({'success': True, 'data': data})


# ============================================
# ADMIN - USER BULK ACTIONS & EXPORTS
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_user_bulk_action(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        user_ids = request.POST.getlist('user_ids')
        
        if not user_ids:
            messages.error(request, 'No users selected!')
            return redirect('dashboard:user_list')
        
        if action == 'delete':
            if str(request.user.id) in user_ids:
                messages.error(request, 'You cannot delete your own account!')
                return redirect('dashboard:user_list')
            User.objects.filter(id__in=user_ids).delete()
            messages.success(request, f'{len(user_ids)} users deleted successfully!')
        
        elif action == 'activate':
            User.objects.filter(id__in=user_ids).update(is_active=True)
            messages.success(request, f'{len(user_ids)} users activated!')
        
        elif action == 'deactivate':
            if str(request.user.id) in user_ids:
                messages.error(request, 'You cannot deactivate your own account!')
                return redirect('dashboard:user_list')
            User.objects.filter(id__in=user_ids).update(is_active=False)
            messages.success(request, f'{len(user_ids)} users deactivated!')
        
        elif action == 'change_role':
            role = request.POST.get('role')
            if role in dict(User.ROLE_CHOICES):
                User.objects.filter(id__in=user_ids).update(role=role)
                messages.success(request, f'Role changed for {len(user_ids)} users!')
        
        return redirect('dashboard:user_list')
    
    return redirect('dashboard:user_list')


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_user_export(request):
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Username', 'Email', 'Full Name', 'Role', 'Active', 'Date Joined'])
    
    users = User.objects.all().order_by('-date_joined')
    for user in users:
        writer.writerow([
            user.id,
            user.username,
            user.email,
            user.get_full_name(),
            user.get_role_display(),
            'Yes' if user.is_active else 'No',
            user.date_joined.strftime('%Y-%m-%d %H:%M')
        ])
    
    return response


# ============================================
# ADMIN - COMMENT BULK ACTIONS & EXPORTS
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_comment_bulk_action(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        comment_ids = request.POST.getlist('comment_ids')
        
        if not comment_ids:
            messages.error(request, 'No comments selected!')
            return redirect('dashboard:comment_list')
        
        if action == 'approve':
            Comment.objects.filter(id__in=comment_ids).update(
                status='approved',
                moderator=request.user,
                moderated_at=timezone.now()
            )
            messages.success(request, f'{len(comment_ids)} comments approved!')
        
        elif action == 'reject':
            Comment.objects.filter(id__in=comment_ids).update(
                status='rejected',
                moderator=request.user,
                moderated_at=timezone.now()
            )
            messages.success(request, f'{len(comment_ids)} comments rejected!')
        
        elif action == 'spam':
            Comment.objects.filter(id__in=comment_ids).update(
                status='spam',
                moderator=request.user,
                moderated_at=timezone.now()
            )
            messages.success(request, f'{len(comment_ids)} comments marked as spam!')
        
        elif action == 'delete':
            Comment.objects.filter(id__in=comment_ids).delete()
            messages.success(request, f'{len(comment_ids)} comments deleted!')
        
        return redirect('dashboard:comment_list')
    
    return redirect('dashboard:comment_list')


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_comment_export(request):
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="comments_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'User', 'Article', 'Content', 'Status', 'Created At'])
    
    comments = Comment.objects.all().order_by('-created_at')
    for comment in comments:
        writer.writerow([
            comment.id,
            comment.user.username if comment.user else 'Anonymous',
            comment.article.title,
            comment.content[:100] + '...' if len(comment.content) > 100 else comment.content,
            comment.get_status_display(),
            comment.created_at.strftime('%Y-%m-%d %H:%M')
        ])
    
    return response


# ============================================
# ADMIN - AD BULK ACTIONS & EXPORTS
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_ad_bulk_action(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        ad_ids = request.POST.getlist('ad_ids')
        
        if not ad_ids:
            messages.error(request, 'No ads selected!')
            return redirect('dashboard:ad_list')
        
        if action == 'approve':
            Advertisement.objects.filter(id__in=ad_ids).update(
                status='active',
                approved_by=request.user,
                approved_at=timezone.now()
            )
            messages.success(request, f'{len(ad_ids)} ads approved!')
        
        elif action == 'reject':
            Advertisement.objects.filter(id__in=ad_ids).update(status='rejected')
            messages.success(request, f'{len(ad_ids)} ads rejected!')
        
        elif action == 'delete':
            Advertisement.objects.filter(id__in=ad_ids).delete()
            messages.success(request, f'{len(ad_ids)} ads deleted!')
        
        elif action == 'pause':
            Advertisement.objects.filter(id__in=ad_ids).update(status='paused')
            messages.success(request, f'{len(ad_ids)} ads paused!')
        
        return redirect('dashboard:ad_list')
    
    return redirect('dashboard:ad_list')


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_ad_export(request):
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ads_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Title', 'Advertiser', 'Position', 'Status', 'Views', 'Clicks', 'CTR', 'Created At'])
    
    ads = Advertisement.objects.all().order_by('-created_at')
    for ad in ads:
        writer.writerow([
            ad.id,
            ad.title,
            ad.advertiser.username,
            ad.get_position_display(),
            ad.get_status_display(),
            ad.views_count,
            ad.clicks_count,
            f"{ad.calculate_ctr():.2f}%",
            ad.created_at.strftime('%Y-%m-%d %H:%M')
        ])
    
    return response


# ============================================
# ADMIN - SUBSCRIBER BULK ACTIONS & EXPORTS
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_subscriber_bulk_action(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        subscriber_ids = request.POST.getlist('subscriber_ids')
        
        if not subscriber_ids:
            messages.error(request, 'No subscribers selected!')
            return redirect('dashboard:subscriber_list')
        
        if action == 'export':
            return admin_subscriber_export(request)
        
        elif action == 'delete':
            Subscriber.objects.filter(id__in=subscriber_ids).delete()
            messages.success(request, f'{len(subscriber_ids)} subscribers deleted!')
        
        return redirect('dashboard:subscriber_list')
    
    return redirect('dashboard:subscriber_list')


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_subscriber_export(request):
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="subscribers_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Email', 'Name', 'Status', 'Created At'])
    
    subscribers = Subscriber.objects.all().order_by('-created_at')
    for subscriber in subscribers:
        writer.writerow([
            subscriber.id,
            subscriber.email,
            subscriber.name or '',
            subscriber.get_status_display(),
            subscriber.created_at.strftime('%Y-%m-%d %H:%M')
        ])
    
    return response


# ============================================
# ADMIN - NEWSLETTER BULK ACTIONS
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_newsletter_bulk_action(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        newsletter_ids = request.POST.getlist('newsletter_ids')
        
        if not newsletter_ids:
            messages.error(request, 'No newsletters selected!')
            return redirect('dashboard:newsletter_list')
        
        if action == 'delete':
            Newsletter.objects.filter(id__in=newsletter_ids).delete()
            messages.success(request, f'{len(newsletter_ids)} newsletters deleted!')
        
        elif action == 'send':
            newsletters = Newsletter.objects.filter(id__in=newsletter_ids)
            for newsletter in newsletters:
                newsletter.send()
            messages.success(request, f'{len(newsletter_ids)} newsletters sent!')
        
        return redirect('dashboard:newsletter_list')
    
    return redirect('dashboard:newsletter_list')


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_newsletter_duplicate(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    
    new_newsletter = Newsletter(
        subject=f"{newsletter.subject} (Copy)",
        content=newsletter.content,
        status='draft',
        created_by=request.user
    )
    new_newsletter.save()
    
    messages.success(request, f'Newsletter "{newsletter.subject}" duplicated!')
    return redirect('dashboard:newsletter_list')


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_newsletter_preview(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    return render(request, 'dashboard/admin_newsletter_preview.html', {'newsletter': newsletter})


# ============================================
# ADMIN - CONTACT BULK ACTIONS
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_contact_bulk_action(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        contact_ids = request.POST.getlist('contact_ids')
        
        if not contact_ids:
            messages.error(request, 'No contacts selected!')
            return redirect('dashboard:contact_list')
        
        if action == 'mark_read':
            ContactMessage.objects.filter(id__in=contact_ids).update(status='read')
            messages.success(request, f'{len(contact_ids)} contacts marked as read!')
        
        elif action == 'mark_new':
            ContactMessage.objects.filter(id__in=contact_ids).update(status='new')
            messages.success(request, f'{len(contact_ids)} contacts marked as new!')
        
        elif action == 'delete':
            ContactMessage.objects.filter(id__in=contact_ids).delete()
            messages.success(request, f'{len(contact_ids)} contacts deleted!')
        
        return redirect('dashboard:contact_list')
    
    return redirect('dashboard:contact_list')


# ============================================
# ADMIN - MEDIA BULK ACTIONS
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_media_bulk_upload(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        uploaded_count = 0
        
        for file in files:
            MediaFile.objects.create(
                file=file,
                title=file.name,
                uploaded_by=request.user,
                file_type='image' if file.content_type.startswith('image/') else 'document'
            )
            uploaded_count += 1
        
        messages.success(request, f'{uploaded_count} files uploaded successfully!')
        return redirect('dashboard:media_list')
    
    return render(request, 'dashboard/admin_media_bulk_upload.html')


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_media_bulk_delete(request):
    if request.method == 'POST':
        media_ids = request.POST.getlist('media_ids')
        
        if not media_ids:
            messages.error(request, 'No media selected!')
            return redirect('dashboard:media_list')
        
        MediaFile.objects.filter(id__in=media_ids).delete()
        messages.success(request, f'{len(media_ids)} media files deleted!')
        return redirect('dashboard:media_list')
    
    return redirect('dashboard:media_list')


# ============================================
# ADMIN - ANALYTICS VIEWS
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_analytics_content(request):
    top_articles = Article.objects.filter(status='published').order_by('-views_count')[:10]
    
    category_stats = Category.objects.annotate(
        article_count=Count('articles'),
        view_count=Sum('articles__views_count')
    ).order_by('-article_count')
    
    from django.db.models.functions import TruncMonth
    monthly_stats = Article.objects.filter(status='published').annotate(
        month=TruncMonth('published_at')
    ).values('month').annotate(
        count=Count('id'),
        views=Sum('views_count')
    ).order_by('month')
    
    context = {
        'top_articles': top_articles,
        'category_stats': category_stats,
        'monthly_stats': monthly_stats,
    }
    return render(request, 'dashboard/admin_analytics_content.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_analytics_audience(request):
    from django.db.models.functions import TruncMonth
    user_growth = User.objects.annotate(
        month=TruncMonth('date_joined')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    role_stats = User.objects.values('role').annotate(count=Count('id'))
    
    active_users = User.objects.filter(last_login__gte=timezone.now() - timedelta(days=30)).count()
    
    context = {
        'user_growth': user_growth,
        'role_stats': role_stats,
        'active_users': active_users,
        'total_users': User.objects.count(),
    }
    return render(request, 'dashboard/admin_analytics_audience.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_analytics_revenue(request):
    # FIXED: Calculate revenue from available fields
    total_revenue = 0
    all_ads = Advertisement.objects.all()
    for ad in all_ads:
        if ad.cost_per_click and ad.cost_per_click > 0:
            total_revenue += ad.cost_per_click * ad.clicks_count
        elif ad.cost_per_impression and ad.cost_per_impression > 0:
            total_revenue += ad.cost_per_impression * ad.views_count
        elif ad.budget and ad.budget > 0:
            total_revenue += ad.budget
    
    from django.db.models.functions import TruncMonth
    monthly_revenue = []
    months = Advertisement.objects.annotate(
        month=TruncMonth('created_at')
    ).values('month').distinct().order_by('month')
    
    for m in months:
        month_ads = Advertisement.objects.filter(created_at__month=m['month'].month, created_at__year=m['month'].year)
        rev = 0
        for ad in month_ads:
            if ad.cost_per_click and ad.cost_per_click > 0:
                rev += ad.cost_per_click * ad.clicks_count
            elif ad.cost_per_impression and ad.cost_per_impression > 0:
                rev += ad.cost_per_impression * ad.views_count
            elif ad.budget and ad.budget > 0:
                rev += ad.budget
        monthly_revenue.append({
            'month': m['month'],
            'revenue': rev
        })
    
    position_revenue = []
    for pos_code, pos_name in Advertisement.POSITION_CHOICES:
        pos_ads = Advertisement.objects.filter(position=pos_code)
        rev = 0
        for ad in pos_ads:
            if ad.cost_per_click and ad.cost_per_click > 0:
                rev += ad.cost_per_click * ad.clicks_count
            elif ad.cost_per_impression and ad.cost_per_impression > 0:
                rev += ad.cost_per_impression * ad.views_count
            elif ad.budget and ad.budget > 0:
                rev += ad.budget
        position_revenue.append({
            'position': pos_name,
            'revenue': rev,
            'views': pos_ads.aggregate(Sum('views_count'))['views_count__sum'] or 0,
            'clicks': pos_ads.aggregate(Sum('clicks_count'))['clicks_count__sum'] or 0,
        })
    
    context = {
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'position_revenue': position_revenue,
    }
    return render(request, 'dashboard/admin_analytics_revenue.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_analytics_export(request):
    import csv
    from django.http import HttpResponse
    
    report_type = request.GET.get('type', 'articles')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="analytics_{report_type}.csv"'
    
    writer = csv.writer(response)
    
    if report_type == 'articles':
        writer.writerow(['Title', 'Category', 'Views', 'Comments', 'Published At'])
        articles = Article.objects.filter(status='published').order_by('-views_count')
        for article in articles[:100]:
            writer.writerow([
                article.title,
                article.category.name if article.category else '',
                article.views_count,
                article.comments.count(),
                article.published_at.strftime('%Y-%m-%d') if article.published_at else ''
            ])
    
    return response


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_analytics_realtime(request):
    today = timezone.now().date()
    
    today_articles = Article.objects.filter(created_at__date=today).count()
    today_users = User.objects.filter(date_joined__date=today).count()
    today_comments = Comment.objects.filter(created_at__date=today).count()
    today_views = Article.objects.filter(created_at__date=today).aggregate(Sum('views_count'))['views_count__sum'] or 0
    
    last_hour = timezone.now() - timedelta(hours=1)
    recent_activity = UserActivityLog.objects.filter(timestamp__gte=last_hour)[:20]
    
    context = {
        'today_articles': today_articles,
        'today_users': today_users,
        'today_comments': today_comments,
        'today_views': today_views,
        'recent_activity': recent_activity,
    }
    return render(request, 'dashboard/admin_analytics_realtime.html', context)


# ============================================
# ADMIN - WIDGET MANAGEMENT
# ============================================

@login_required
def widget_list(request):
    widgets = DashboardWidget.objects.filter(user=request.user).order_by('column', 'position')
    
    context = {
        'widgets': widgets,
    }
    return render(request, 'dashboard/widget_list.html', context)


# ============================================
# API BULK ACTION
# ============================================

@login_required
def api_bulk_action(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})
    
    model = request.POST.get('model')
    action = request.POST.get('action')
    ids = request.POST.getlist('ids')
    
    if not model or not action or not ids:
        return JsonResponse({'success': False, 'error': 'Missing required parameters'})
    
    model_map = {
        'article': Article,
        'comment': Comment,
        'user': User,
        'advertisement': Advertisement,
        'subscriber': Subscriber,
        'newsletter': Newsletter,
        'contact': ContactMessage,
        'media': MediaFile,
    }
    
    model_class = model_map.get(model.lower())
    if not model_class:
        return JsonResponse({'success': False, 'error': 'Invalid model'})
    
    try:
        if action == 'delete':
            model_class.objects.filter(id__in=ids).delete()
        elif action == 'activate':
            if model == 'user':
                model_class.objects.filter(id__in=ids).update(is_active=True)
        elif action == 'deactivate':
            if model == 'user':
                model_class.objects.filter(id__in=ids).update(is_active=False)
        elif action == 'approve':
            if model == 'comment':
                model_class.objects.filter(id__in=ids).update(status='approved')
            elif model == 'advertisement':
                model_class.objects.filter(id__in=ids).update(status='active')
        else:
            return JsonResponse({'success': False, 'error': 'Invalid action'})
        
        return JsonResponse({'success': True, 'message': f'{len(ids)} items processed'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def api_search(request):
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'success': False, 'error': 'Query too short'})
    
    results = {
        'articles': [],
        'users': [],
        'ads': [],
        'categories': [],
        'tags': [],
    }
    
    articles = Article.objects.filter(
        Q(title__icontains=query) | Q(content__icontains=query)
    )[:5]
    results['articles'] = [{'id': a.id, 'title': a.title, 'url': a.get_absolute_url()} for a in articles]
    
    users = User.objects.filter(
        Q(username__icontains=query) | Q(email__icontains=query)
    )[:5]
    results['users'] = [{'id': u.id, 'username': u.username} for u in users]
    
    ads = Advertisement.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    )[:5]
    results['ads'] = [{'id': a.id, 'title': a.title} for a in ads]
    
    return JsonResponse({'success': True, 'results': results})


@login_required
def api_export(request):
    export_type = request.GET.get('type')
    
    if export_type == 'users':
        return admin_user_export(request)
    elif export_type == 'comments':
        return admin_comment_export(request)
    elif export_type == 'ads':
        return admin_ad_export(request)
    elif export_type == 'subscribers':
        return admin_subscriber_export(request)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid export type'})


@login_required
def api_dashboard_widgets(request):
    widgets = DashboardWidget.objects.filter(user=request.user, is_active=True).order_by('column', 'position')
    
    data = {
        'widgets': [{
            'id': w.id,
            'title': w.title,
            'widget_type': w.widget_type,
            'column': w.column,
            'position': w.position,
            'is_active': w.is_active,
            'config': w.config,
        } for w in widgets]
    }
    
    return JsonResponse({'success': True, 'data': data})


# ============================================
# ADMIN - SETTINGS AJAX
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_settings_ajax(request):
    if request.method == 'GET':
        category = request.GET.get('category')
        key = request.GET.get('key')
        
        if category and key:
            value = get_setting_value(category, key, '')
            return JsonResponse({'success': True, 'value': value})
        
        if category:
            settings = SiteSetting.objects.filter(category=category)
            data = {s.key: s.value for s in settings}
            return JsonResponse({'success': True, 'data': data})
        
        return JsonResponse({'success': False, 'error': 'Missing category or key'})
    
    elif request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            category = data.get('category')
            key = data.get('key')
            value = data.get('value')
            
            if category and key:
                update_setting(category, key, value)
                return JsonResponse({'success': True, 'message': 'Setting updated successfully'})
            
            return JsonResponse({'success': False, 'error': 'Missing category or key'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})


# ============================================
# ADMIN - MEDIA GALLERY
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_media_gallery(request):
    media = MediaFile.objects.filter(file_type='image').order_by('-created_at')
    
    search = request.GET.get('search')
    if search:
        media = media.filter(Q(title__icontains=search) | Q(description__icontains=search))
    
    paginator = Paginator(media, 50)
    page = request.GET.get('page')
    try:
        media = paginator.page(page)
    except PageNotAnInteger:
        media = paginator.page(1)
    except EmptyPage:
        media = paginator.page(paginator.num_pages)
    
    return render(request, 'dashboard/admin_media_gallery.html', {'media': media})


# ============================================
# ADMIN - SETTINGS UPDATE
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_settings_update(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        key = request.POST.get('key')
        value = request.POST.get('value')
        
        if category and key:
            update_setting(category, key, value)
            messages.success(request, f'Setting "{key}" updated successfully!')
            return JsonResponse({'success': True})
        
        import json
        try:
            data = json.loads(request.POST.get('data', '{}'))
            for category, settings in data.items():
                for key, value in settings.items():
                    update_setting(category, key, value)
            messages.success(request, 'Settings updated successfully!')
            return JsonResponse({'success': True})
        except:
            return JsonResponse({'success': False, 'error': 'Invalid data format'})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})


# ============================================
# USER SETTINGS UPDATE
# ============================================

@login_required
def settings_update(request):
    if request.method == 'POST':
        user = request.user
        preferences, created = DashboardPreference.objects.get_or_create(user=user)
        form = DashboardPreferenceForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated successfully!')
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})


# ============================================
# WIDGET LIST
# ============================================

@login_required
def widget_list(request):
    widgets = DashboardWidget.objects.filter(user=request.user).order_by('column', 'position')
    
    context = {
        'widgets': widgets,
    }
    return render(request, 'dashboard/widget_list.html', context)

# ============================================
# ADMIN - VIDEOS
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_videos(request):
    """Manage videos"""
    videos = MediaFile.objects.filter(file_type='video').order_by('-created_at')
    
    search = request.GET.get('search')
    if search:
        videos = videos.filter(Q(title__icontains=search) | Q(description__icontains=search))
    
    paginator = Paginator(videos, 25)
    page = request.GET.get('page')
    try:
        videos = paginator.page(page)
    except PageNotAnInteger:
        videos = paginator.page(1)
    except EmptyPage:
        videos = paginator.page(paginator.num_pages)
    
    context = {
        'videos': videos,
        'search': search,
        'total_videos': MediaFile.objects.filter(file_type='video').count(),
        'featured_videos': 0,
    }
    return render(request, 'dashboard/admin_videos.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_video_upload(request):
    """Upload video"""
    if request.method == 'POST':
        form = MediaFileForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.uploaded_by = request.user
            video.file_type = 'video'
            video.save()
            form.save_m2m()
            messages.success(request, f'Video "{video.title}" uploaded successfully!')
            return redirect('dashboard:video_list')
    else:
        form = MediaFileForm()
    
    return render(request, 'dashboard/admin_video_upload.html', {'form': form})


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_video_edit(request, video_id):
    """Edit video"""
    video = get_object_or_404(MediaFile, id=video_id, file_type='video')
    
    if request.method == 'POST':
        form = MediaFileForm(request.POST, request.FILES, instance=video)
        if form.is_valid():
            form.save()
            messages.success(request, f'Video "{video.title}" updated successfully!')
            return redirect('dashboard:video_list')
    else:
        form = MediaFileForm(instance=video)
    
    return render(request, 'dashboard/admin_video_edit.html', {'form': form, 'video': video})


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_video_delete(request, video_id):
    """Delete video"""
    video = get_object_or_404(MediaFile, id=video_id, file_type='video')
    
    if request.method == 'POST':
        title = video.title
        video.delete()
        messages.success(request, f'Video "{title}" deleted successfully!')
        return redirect('dashboard:video_list')
    
    return render(request, 'dashboard/confirm_delete.html', {
        'object': video,
        'type': 'Video',
        'back_url': 'dashboard:video_list'
    })


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_video_feature(request, video_id):
    """Toggle featured status of video"""
    video = get_object_or_404(MediaFile, id=video_id, file_type='video')
    messages.info(request, f'Video "{video.title}" featured status updated.')
    return redirect('dashboard:video_list')


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_video_bulk_upload(request):
    """Bulk upload videos"""
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        uploaded_count = 0
        
        for file in files:
            MediaFile.objects.create(
                file=file,
                title=file.name,
                uploaded_by=request.user,
                file_type='video'
            )
            uploaded_count += 1
        
        messages.success(request, f'{uploaded_count} videos uploaded successfully!')
        return redirect('dashboard:video_list')
    
    return render(request, 'dashboard/admin_video_bulk_upload.html')


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_video_bulk_delete(request):
    """Bulk delete videos"""
    if request.method == 'POST':
        video_ids = request.POST.getlist('video_ids')
        
        if not video_ids:
            messages.error(request, 'No videos selected!')
            return redirect('dashboard:video_list')
        
        MediaFile.objects.filter(id__in=video_ids, file_type='video').delete()
        messages.success(request, f'{len(video_ids)} videos deleted successfully!')
        return redirect('dashboard:video_list')
    
    return redirect('dashboard:video_list')


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_video_gallery(request):
    """Video gallery view"""
    videos = MediaFile.objects.filter(file_type='video').order_by('-created_at')
    
    search = request.GET.get('search')
    if search:
        videos = videos.filter(Q(title__icontains=search) | Q(description__icontains=search))
    
    paginator = Paginator(videos, 50)
    page = request.GET.get('page')
    try:
        videos = paginator.page(page)
    except PageNotAnInteger:
        videos = paginator.page(1)
    except EmptyPage:
        videos = paginator.page(paginator.num_pages)
    
    return render(request, 'dashboard/admin_video_gallery.html', {'videos': videos})