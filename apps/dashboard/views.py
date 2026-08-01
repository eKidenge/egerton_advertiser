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
from apps.advertisements.models import Advertisement
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
# ADMIN DASHBOARD - MAIN VIEW
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
# ARTICLE MANAGEMENT - FULL CRUD
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin', 'editor'])
def admin_articles(request):
    """Manage all articles"""
    articles = Article.objects.all().order_by('-created_at')
    
    # Filters
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
            return redirect('dashboard:admin_articles')
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
            return redirect('dashboard:admin_articles')
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
        return redirect('dashboard:admin_articles')
    
    return render(request, 'dashboard/admin_confirm_delete.html', {
        'object': article,
        'type': 'Article',
        'back_url': 'dashboard:admin_articles'
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
    return redirect('dashboard:admin_articles')


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin', 'editor'])
def admin_article_feature(request, article_id):
    """Toggle featured status"""
    article = get_object_or_404(Article, id=article_id)
    article.is_featured = not article.is_featured
    article.save()
    
    status = 'featured' if article.is_featured else 'unfeatured'
    messages.success(request, f'Article "{article.title}" {status}!')
    return redirect('dashboard:admin_articles')


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin', 'editor'])
def admin_article_breaking(request, article_id):
    """Toggle breaking news status"""
    article = get_object_or_404(Article, id=article_id)
    article.is_breaking = not article.is_breaking
    article.save()
    
    status = 'marked as breaking' if article.is_breaking else 'removed from breaking'
    messages.success(request, f'Article "{article.title}" {status}!')
    return redirect('dashboard:admin_articles')


# ============================================
# CATEGORY MANAGEMENT - FULL CRUD
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
            return redirect('dashboard:admin_categories')
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
            return redirect('dashboard:admin_categories')
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
        return redirect('dashboard:admin_categories')
    
    return render(request, 'dashboard/admin_confirm_delete.html', {
        'object': category,
        'type': 'Category',
        'back_url': 'dashboard:admin_categories'
    })


# ============================================
# TAG MANAGEMENT - FULL CRUD
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
            return redirect('dashboard:admin_tags')
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
            return redirect('dashboard:admin_tags')
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
        return redirect('dashboard:admin_tags')
    
    return render(request, 'dashboard/admin_confirm_delete.html', {
        'object': tag,
        'type': 'Tag',
        'back_url': 'dashboard:admin_tags'
    })


# ============================================
# USER MANAGEMENT - FULL CRUD
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_users(request):
    """Manage users"""
    users = User.objects.all().order_by('-date_joined')
    
    # Filters
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
            return redirect('dashboard:admin_users')
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
            return redirect('dashboard:admin_users')
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
        return redirect('dashboard:admin_users')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User "{username}" deleted!')
        return redirect('dashboard:admin_users')
    
    return render(request, 'dashboard/admin_confirm_delete.html', {
        'object': user,
        'type': 'User',
        'back_url': 'dashboard:admin_users'
    })


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_user_toggle_active(request, user_id):
    """Toggle user active status"""
    user = get_object_or_404(User, id=user_id)
    
    if request.user == user:
        messages.error(request, 'You cannot deactivate your own account!')
        return redirect('dashboard:admin_users')
    
    user.is_active = not user.is_active
    user.save()
    
    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'User "{user.username}" {status}!')
    return redirect('dashboard:admin_users')


# ============================================
# COMMENT MANAGEMENT - FULL CRUD
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
        return redirect('dashboard:admin_comments')
    
    return render(request, 'dashboard/admin_comment_moderate.html', {'comment': comment})


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_comment_delete(request, comment_id):
    """Delete comment"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted!')
        return redirect('dashboard:admin_comments')
    
    return render(request, 'dashboard/admin_confirm_delete.html', {
        'object': comment,
        'type': 'Comment',
        'back_url': 'dashboard:admin_comments'
    })


# ============================================
# ADVERTISEMENT MANAGEMENT - FULL CRUD
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
        'position_choices': Advertisement.POSITION_CHOICES,
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
            return redirect('dashboard:admin_ads')
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
            return redirect('dashboard:admin_ads')
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
        return redirect('dashboard:admin_ads')
    
    return render(request, 'dashboard/admin_confirm_delete.html', {
        'object': ad,
        'type': 'Advertisement',
        'back_url': 'dashboard:admin_ads'
    })


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_ad_approve(request, ad_id):
    """Approve or reject advertisement"""
    ad = get_object_or_404(Advertisement, id=ad_id)
    
    action = request.GET.get('action')
    
    if action == 'approve':
        ad.status = 'active'
        ad.save()
        messages.success(request, f'Ad "{ad.title}" approved and activated!')
    elif action == 'reject':
        ad.status = 'rejected'
        ad.save()
        messages.warning(request, f'Ad "{ad.title}" rejected!')
    
    return redirect('dashboard:admin_ads')


# ============================================
# CONTACT MESSAGE MANAGEMENT - FULL CRUD
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_contacts(request):
    """Manage contact messages"""
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
    }
    return render(request, 'dashboard/admin_contacts.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_contact_detail(request, contact_id):
    """View and reply to contact message"""
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
            
            # Send email reply
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
            return redirect('dashboard:admin_contacts')
    else:
        form = ContactReplyForm()
    
    return render(request, 'dashboard/admin_contact_detail.html', {'contact': contact, 'form': form})


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_contact_delete(request, contact_id):
    """Delete contact message"""
    contact = get_object_or_404(ContactMessage, id=contact_id)
    
    if request.method == 'POST':
        contact.delete()
        messages.success(request, 'Message deleted!')
        return redirect('dashboard:admin_contacts')
    
    return render(request, 'dashboard/admin_confirm_delete.html', {
        'object': contact,
        'type': 'Contact Message',
        'back_url': 'dashboard:admin_contacts'
    })


# ============================================
# MEDIA LIBRARY MANAGEMENT
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_media(request):
    """Manage media files"""
    media = MediaFile.objects.all().order_by('-created_at')
    
    file_type = request.GET.get('type')
    if file_type:
        media = media.filter(file_type=file_type)
    
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
    }
    return render(request, 'dashboard/admin_media.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_media_delete(request, media_id):
    """Delete media file"""
    media = get_object_or_404(MediaFile, id=media_id)
    
    if request.method == 'POST':
        title = media.title
        media.delete()
        messages.success(request, f'Media "{title}" deleted!')
        return redirect('dashboard:admin_media')
    
    return render(request, 'dashboard/admin_confirm_delete.html', {
        'object': media,
        'type': 'Media File',
        'back_url': 'dashboard:admin_media'
    })


# ============================================
# SUBSCRIBER MANAGEMENT
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_subscribers(request):
    """Manage subscribers"""
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
    }
    return render(request, 'dashboard/admin_subscribers.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_subscriber_delete(request, subscriber_id):
    """Delete subscriber"""
    subscriber = get_object_or_404(Subscriber, id=subscriber_id)
    
    if request.method == 'POST':
        email = subscriber.email
        subscriber.delete()
        messages.success(request, f'Subscriber "{email}" removed!')
        return redirect('dashboard:admin_subscribers')
    
    return render(request, 'dashboard/admin_confirm_delete.html', {
        'object': subscriber,
        'type': 'Subscriber',
        'back_url': 'dashboard:admin_subscribers'
    })


# ============================================
# NEWSLETTER MANAGEMENT
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_newsletters(request):
    """Manage newsletters"""
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
    }
    return render(request, 'dashboard/admin_newsletters.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_newsletter_create(request):
    """Create newsletter"""
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.created_by = request.user
            newsletter.save()
            form.save_m2m()
            messages.success(request, f'Newsletter "{newsletter.subject}" created!')
            return redirect('dashboard:admin_newsletters')
    else:
        form = NewsletterForm()
    
    return render(request, 'dashboard/admin_newsletter_form.html', {'form': form, 'action': 'Create'})


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_newsletter_edit(request, newsletter_id):
    """Edit newsletter"""
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    
    if request.method == 'POST':
        form = NewsletterForm(request.POST, instance=newsletter)
        if form.is_valid():
            form.save()
            messages.success(request, f'Newsletter "{newsletter.subject}" updated!')
            return redirect('dashboard:admin_newsletters')
    else:
        form = NewsletterForm(instance=newsletter)
    
    return render(request, 'dashboard/admin_newsletter_form.html', {'form': form, 'action': 'Edit', 'newsletter': newsletter})


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_newsletter_send(request, newsletter_id):
    """Send newsletter"""
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    
    if request.method == 'POST':
        newsletter.send()
        messages.success(request, f'Newsletter "{newsletter.subject}" sent!')
        return redirect('dashboard:admin_newsletters')
    
    return render(request, 'dashboard/admin_newsletter_send.html', {'newsletter': newsletter})


@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_newsletter_delete(request, newsletter_id):
    """Delete newsletter"""
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    
    if request.method == 'POST':
        subject = newsletter.subject
        newsletter.delete()
        messages.success(request, f'Newsletter "{subject}" deleted!')
        return redirect('dashboard:admin_newsletters')
    
    return render(request, 'dashboard/admin_confirm_delete.html', {
        'object': newsletter,
        'type': 'Newsletter',
        'back_url': 'dashboard:admin_newsletters'
    })


# ============================================
# SETTINGS MANAGEMENT
# ============================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'])
def admin_settings(request):
    """Site settings"""
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
                return redirect('dashboard:admin_settings?category=general')
        
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
                return redirect('dashboard:admin_settings?category=email')
        
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
                return redirect('dashboard:admin_settings?category=seo')
    
    # Get current settings
    settings = {
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
        'settings': settings,
        'categories': SiteSetting.SETTING_TYPES,
    }
    return render(request, 'dashboard/admin_settings.html', context)


def update_setting(category, key, value):
    """Update or create a setting"""
    setting, created = SiteSetting.objects.get_or_create(category=category, key=key)
    setting.value = value
    setting.save()


def get_setting_value(category, key, default=''):
    """Get a setting value"""
    try:
        setting = SiteSetting.objects.get(category=category, key=key)
        return setting.value
    except SiteSetting.DoesNotExist:
        return default