# apps/articles/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count, Sum, Avg, Prefetch
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
import json
from .models import Article, ArticleVersion, ArticleStatistics, RelatedArticle
from .forms import ArticleForm, ArticleFilterForm
from apps.categories.models import Category
from apps.tags.models import Tag
from apps.comments.models import Comment
from apps.accounts.models import UserActivityLog
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

# ============================================================
# PUBLIC VIEWS
# ============================================================

def home(request):
    """Homepage - The Egerton Avenue"""
    # Get featured articles
    featured_articles = Article.objects.filter(
        status='published',
        is_featured=True,
        published_at__lte=timezone.now()
    ).select_related('author', 'category').prefetch_related('tags')[:5]
    
    # Get breaking news
    breaking_news = Article.objects.filter(
        status='published',
        is_breaking=True,
        published_at__lte=timezone.now()
    ).select_related('author', 'category').order_by('-published_at')[:5]
    
    # Get latest articles
    latest_articles = Article.objects.filter(
        status='published',
        published_at__lte=timezone.now()
    ).select_related('author', 'category').prefetch_related('tags').order_by('-published_at')[:10]
    
    # Get articles by category (for The Egerton Avenue sections)
    environment_articles = Article.objects.filter(
        status='published',
        category__slug='environment',
        published_at__lte=timezone.now()
    ).select_related('author')[:5]
    
    society_articles = Article.objects.filter(
        status='published',
        category__slug='society',
        published_at__lte=timezone.now()
    ).select_related('author')[:5]
    
    politics_articles = Article.objects.filter(
        status='published',
        category__slug='politics',
        published_at__lte=timezone.now()
    ).select_related('author')[:5]
    
    business_articles = Article.objects.filter(
        status='published',
        category__slug='business',
        published_at__lte=timezone.now()
    ).select_related('author')[:5]
    
    # Get editor's pick
    editor_pick = Article.objects.filter(
        status='published',
        is_editor_pick=True,
        published_at__lte=timezone.now()
    ).select_related('author', 'category').first()
    
    # Get popular articles
    popular_articles = Article.objects.filter(
        status='published',
        published_at__lte=timezone.now()
    ).select_related('author').order_by('-views_count')[:5]
    
    context = {
        'page_title': 'The Egerton Avenue - Environment & Society',
        'featured_articles': featured_articles,
        'breaking_news': breaking_news,
        'latest_articles': latest_articles,
        'environment_articles': environment_articles,
        'society_articles': society_articles,
        'politics_articles': politics_articles,
        'business_articles': business_articles,
        'editor_pick': editor_pick,
        'popular_articles': popular_articles,
        'section': 'home',
    }
    
    return render(request, 'articles/home.html', context)


def category_view(request, slug):
    """Display articles by category slug - For navigation links"""
    from apps.categories.models import Category
    from django.core.paginator import Paginator
    
    # Get the category
    category = get_object_or_404(Category, slug=slug, is_active=True)
    
    # Get published articles in this category
    articles = Article.objects.filter(
        category=category,
        status='published',
        published_at__lte=timezone.now()
    ).select_related('author', 'category').prefetch_related('tags').order_by('-published_at', '-created_at')
    
    # Get featured article in this category
    featured_article = articles.filter(is_featured=True).first()
    
    # Pagination
    paginator = Paginator(articles, 12)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    # Get subcategories
    subcategories = category.children.filter(is_active=True)
    
    # Get article count for display
    article_count = Article.objects.filter(
        category=category,
        status='published',
        published_at__lte=timezone.now()
    ).count()
    
    context = {
        'category': category,
        'articles': articles,
        'featured_article': featured_article,
        'subcategories': subcategories,
        'article_count': article_count,
        'page_title': f'{category.name} - The Egerton Avenue',
        'section': slug,
    }
    
    # Use the categories app's template
    return render(request, 'categories/category_detail.html', context)


def photos(request):
    """Photos page - Gallery view"""
    from .models import Article
    
    # Get articles with featured images (photos)
    articles = Article.objects.filter(
        status='published',
        featured_image__isnull=False
    ).exclude(featured_image='').select_related('author', 'category').order_by('-published_at', '-created_at')
    
    # Get featured photos
    featured_articles = articles.filter(is_featured=True)[:6]
    
    # Paginate
    paginator = Paginator(articles, 12)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    # Get categories for filtering
    categories = Category.objects.filter(
        articles__isnull=False
    ).distinct()[:10]
    
    context = {
        'page_title': 'Photos - The Egerton Avenue',
        'featured_articles': featured_articles,
        'articles': articles,
        'categories': categories,
        'section': 'photos',
        'article_count': Article.objects.filter(status='published', featured_image__isnull=False).count(),
    }
    return render(request, 'articles/photos.html', context)


def video(request):
    """Video page - Video gallery view"""
    from .models import Article
    
    # Get articles with video content (you can add a video field to Article model)
    # For now, show articles with featured images as video placeholders
    articles = Article.objects.filter(
        status='published',
        published_at__lte=timezone.now()
    ).select_related('author', 'category').order_by('-published_at', '-created_at')
    
    # Get featured videos
    featured_articles = articles.filter(is_featured=True)[:3]
    
    # Paginate
    paginator = Paginator(articles, 9)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    # Get categories for filtering
    categories = Category.objects.filter(
        articles__isnull=False
    ).distinct()[:10]
    
    context = {
        'page_title': 'Video - The Egerton Avenue',
        'featured_articles': featured_articles,
        'articles': articles,
        'categories': categories,
        'section': 'video',
        'article_count': Article.objects.filter(status='published').count(),
    }
    return render(request, 'articles/video.html', context)


@cache_page(60 * 15)  # Cache for 15 minutes
@vary_on_headers('User-Agent')
def article_detail(request, slug):
    article = get_object_or_404(
        Article.objects.select_related('author', 'category')
        .prefetch_related('tags', 'related_articles'),
        slug=slug,
        status='published'
    )
    
    # Increment view count
    article.increment_view()
    
    # Log activity
    if request.user.is_authenticated:
        UserActivityLog.objects.create(
            user=request.user,
            action='view',
            model_name='Article',
            object_id=article.id,
            description=f'Viewed article: {article.title}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
    
    # Get related articles
    related_articles = Article.objects.filter(
        status='published',
        category=article.category
    ).exclude(id=article.id).select_related('author')[:5]
    
    # Get comments
    comments = Comment.objects.filter(
        article=article,
        status='approved'
    ).select_related('user').order_by('created_at')
    
    # Get author's other articles
    author_articles = Article.objects.filter(
        status='published',
        author=article.author
    ).exclude(id=article.id).select_related('category')[:5]
    
    context = {
        'article': article,
        'related_articles': related_articles,
        'comments': comments,
        'author_articles': author_articles,
        'comment_count': comments.count(),
        'page_title': f'{article.title} - The Egerton Avenue',
    }
    
    return render(request, 'articles/article_detail.html', context)


def latest_news(request):
    articles = Article.objects.filter(
        status='published',
        published_at__lte=timezone.now()
    ).select_related('author', 'category').prefetch_related('tags').order_by('-published_at')
    
    # Apply filters
    category_slug = request.GET.get('category')
    if category_slug:
        articles = articles.filter(category__slug=category_slug)
    
    tag_slug = request.GET.get('tag')
    if tag_slug:
        articles = articles.filter(tags__slug=tag_slug)
    
    date_from = request.GET.get('date_from')
    if date_from:
        articles = articles.filter(published_at__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        articles = articles.filter(published_at__lte=date_to)
    
    # Pagination
    paginator = Paginator(articles, 20)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    # Get categories and tags for filter
    categories = Category.objects.filter(is_active=True)
    tags = Tag.objects.all()
    
    context = {
        'articles': articles,
        'categories': categories,
        'tags': tags,
        'current_category': category_slug,
        'current_tag': tag_slug,
        'page_title': 'Latest News - The Egerton Avenue',
    }
    return render(request, 'articles/latest_news.html', context)


def breaking_news(request):
    articles = Article.objects.filter(
        status='published',
        is_breaking=True,
        published_at__lte=timezone.now()
    ).select_related('author', 'category').order_by('-published_at')
    
    paginator = Paginator(articles, 10)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    context = {
        'articles': articles,
        'page_title': 'Breaking News - The Egerton Avenue',
        'section': 'breaking',
    }
    return render(request, 'articles/breaking_news.html', context)


def author_articles(request, author_id):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    author = get_object_or_404(User, id=author_id)
    articles = Article.objects.filter(
        author=author,
        status='published',
        published_at__lte=timezone.now()
    ).select_related('category').order_by('-published_at')
    
    paginator = Paginator(articles, 20)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    context = {
        'articles': articles,
        'author': author,
        'article_count': Article.objects.filter(author=author, status='published').count(),
        'total_views': Article.objects.filter(author=author, status='published').aggregate(Sum('views_count'))['views_count__sum'] or 0,
        'page_title': f'Articles by {author.get_full_name()} - The Egerton Avenue',
    }
    return render(request, 'articles/author_articles.html', context)


# ============================================================
# DASHBOARD / AUTHOR VIEWS
# ============================================================

@login_required
def article_list(request):
    user = request.user
    
    if user.can_manage_users:
        articles = Article.objects.all().select_related('author', 'category')
    else:
        articles = Article.objects.filter(author=user).select_related('author', 'category')
    
    # Filtering
    form = ArticleFilterForm(request.GET)
    if form.is_valid():
        if form.cleaned_data.get('status'):
            articles = articles.filter(status=form.cleaned_data['status'])
        if form.cleaned_data.get('category'):
            articles = articles.filter(category=form.cleaned_data['category'])
        if form.cleaned_data.get('author'):
            articles = articles.filter(author=form.cleaned_data['author'])
        if form.cleaned_data.get('date_from'):
            articles = articles.filter(created_at__gte=form.cleaned_data['date_from'])
        if form.cleaned_data.get('date_to'):
            articles = articles.filter(created_at__lte=form.cleaned_data['date_to'])
        if form.cleaned_data.get('search'):
            query = form.cleaned_data['search']
            articles = articles.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query)
            )
    
    articles = articles.order_by('-created_at')
    
    paginator = Paginator(articles, 20)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    context = {
        'articles': articles,
        'form': form,
        'page_title': 'Manage Articles - The Egerton Avenue',
    }
    return render(request, 'articles/article_list.html', context)


@login_required
def article_create(request):
    if not request.user.can_publish:
        messages.error(request, 'You do not have permission to create articles.')
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            
            # Handle publish option
            publish_option = form.cleaned_data.get('publish_option')
            if publish_option == Article.PUBLISH_NOW:
                article.status = 'published'
                article.published_at = timezone.now()
            elif publish_option == Article.SCHEDULE:
                article.status = 'scheduled'
                article.scheduled_for = form.cleaned_data.get('scheduled_for')
            
            article.save()
            
            # Save many-to-many fields
            form.save_m2m()
            
            # Log activity
            UserActivityLog.objects.create(
                user=request.user,
                action='create',
                model_name='Article',
                object_id=article.id,
                description=f'Created article: {article.title}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'Article "{article.title}" created successfully!')
            
            if article.status == 'draft':
                return redirect('articles:article_edit', article_id=article.id)
            else:
                return redirect('articles:detail', slug=article.slug)
    else:
        form = ArticleForm()
    
    # Get categories and tags for the form
    categories = Category.objects.filter(is_active=True)
    tags = Tag.objects.all()
    
    context = {
        'form': form,
        'categories': categories,
        'tags': tags,
        'action': 'create',
        'page_title': 'Create Article - The Egerton Avenue',
    }
    return render(request, 'articles/article_create.html', context)


@login_required
def article_edit(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    
    # Check permissions
    if not request.user.can_manage_users and article.author != request.user:
        messages.error(request, 'You do not have permission to edit this article.')
        return redirect('articles:article_list')
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            # Save version before update
            ArticleVersion.objects.create(
                article=article,
                version_number=article.versions.count() + 1,
                title=article.title,
                content=article.content,
                excerpt=article.excerpt,
                slug=article.slug,
                modified_by=request.user,
                change_notes=request.POST.get('change_notes', '')
            )
            
            article = form.save(commit=False)
            
            # Handle publish option
            publish_option = form.cleaned_data.get('publish_option')
            if publish_option == Article.PUBLISH_NOW and article.status != 'published':
                article.status = 'published'
                article.published_at = timezone.now()
            elif publish_option == Article.SCHEDULE:
                article.status = 'scheduled'
                article.scheduled_for = form.cleaned_data.get('scheduled_for')
            
            article.updated_at = timezone.now()
            article.save()
            form.save_m2m()
            
            # Log activity
            UserActivityLog.objects.create(
                user=request.user,
                action='update',
                model_name='Article',
                object_id=article.id,
                description=f'Updated article: {article.title}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'Article "{article.title}" updated successfully!')
            return redirect('articles:detail', slug=article.slug)
    else:
        form = ArticleForm(instance=article)
    
    categories = Category.objects.filter(is_active=True)
    tags = Tag.objects.all()
    versions = article.versions.all()
    
    context = {
        'form': form,
        'article': article,
        'categories': categories,
        'tags': tags,
        'versions': versions,
        'action': 'edit',
        'page_title': f'Edit {article.title} - The Egerton Avenue',
    }
    return render(request, 'articles/article_edit.html', context)


@login_required
def article_delete(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    
    # Check permissions
    if not request.user.can_manage_users and article.author != request.user:
        messages.error(request, 'You do not have permission to delete this article.')
        return redirect('articles:article_list')
    
    if request.method == 'POST':
        title = article.title
        
        # Log activity
        UserActivityLog.objects.create(
            user=request.user,
            action='delete',
            model_name='Article',
            object_id=article.id,
            description=f'Deleted article: {title}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        article.delete()
        messages.success(request, f'Article "{title}" deleted successfully!')
        return redirect('articles:article_list')
    
    context = {
        'article': article,
        'page_title': f'Delete {article.title} - The Egerton Avenue',
    }
    return render(request, 'articles/article_delete.html', context)


@login_required
def draft_articles(request):
    user = request.user
    if user.can_manage_users:
        articles = Article.objects.filter(status='draft').select_related('author', 'category')
    else:
        articles = Article.objects.filter(author=user, status='draft').select_related('author', 'category')
    
    articles = articles.order_by('-created_at')
    
    paginator = Paginator(articles, 20)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    context = {
        'articles': articles,
        'page_title': 'Draft Articles - The Egerton Avenue',
    }
    return render(request, 'articles/draft_articles.html', context)


@login_required
def published_articles(request):
    user = request.user
    if user.can_manage_users:
        articles = Article.objects.filter(status='published').select_related('author', 'category')
    else:
        articles = Article.objects.filter(author=user, status='published').select_related('author', 'category')
    
    articles = articles.order_by('-published_at')
    
    paginator = Paginator(articles, 20)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    context = {
        'articles': articles,
        'page_title': 'Published Articles - The Egerton Avenue',
    }
    return render(request, 'articles/published_articles.html', context)


@login_required
@user_passes_test(lambda u: u.can_manage_users)
def pending_articles(request):
    articles = Article.objects.filter(status='pending').select_related('author', 'category').order_by('-created_at')
    
    paginator = Paginator(articles, 20)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    context = {
        'articles': articles,
        'page_title': 'Pending Articles - The Egerton Avenue',
    }
    return render(request, 'articles/pending_articles.html', context)


@login_required
def scheduled_articles(request):
    user = request.user
    if user.can_manage_users:
        articles = Article.objects.filter(status='scheduled').select_related('author', 'category')
    else:
        articles = Article.objects.filter(author=user, status='scheduled').select_related('author', 'category')
    
    articles = articles.order_by('scheduled_for')
    
    paginator = Paginator(articles, 20)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    context = {
        'articles': articles,
        'page_title': 'Scheduled Articles - The Egerton Avenue',
    }
    return render(request, 'articles/scheduled_articles.html', context)


@login_required
@user_passes_test(lambda u: u.can_manage_users)
def archived_articles(request):
    articles = Article.objects.filter(status='archived').select_related('author', 'category').order_by('-archived_at')
    
    paginator = Paginator(articles, 20)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    context = {
        'articles': articles,
        'page_title': 'Archived Articles - The Egerton Avenue',
    }
    return render(request, 'articles/archived_articles.html', context)


@login_required
@user_passes_test(lambda u: u.can_manage_users)
def featured_articles(request):
    articles = Article.objects.filter(is_featured=True).select_related('author', 'category').order_by('featured_order', '-published_at')
    
    paginator = Paginator(articles, 20)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    context = {
        'articles': articles,
        'page_title': 'Featured Articles - The Egerton Avenue',
    }
    return render(request, 'articles/featured_articles.html', context)


# ============================================================
# API / AJAX VIEWS
# ============================================================

@login_required
@require_http_methods(["POST"])
def publish_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    
    if not request.user.can_publish and article.author != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.user.is_editor or request.user.can_publish:
        article.status = 'published'
        article.published_at = timezone.now()
        article.save()
        
        # Send notification to subscribers
        try:
            # This would be implemented with a newsletter system
            pass
        except Exception as e:
            print(f"Failed to send notification: {e}")
        
        UserActivityLog.objects.create(
            user=request.user,
            action='publish',
            model_name='Article',
            object_id=article.id,
            description=f'Published article: {article.title}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, f'Article "{article.title}" published successfully!')
        return redirect('articles:detail', slug=article.slug)
    
    messages.error(request, 'You do not have permission to publish articles.')
    return redirect('articles:article_list')


@login_required
@require_http_methods(["POST"])
def unpublish_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    
    if not request.user.can_publish and article.author != request.user:
        messages.error(request, 'Permission denied.')
        return redirect('articles:article_list')
    
    article.status = 'draft'
    article.published_at = None
    article.save()
    
    UserActivityLog.objects.create(
        user=request.user,
        action='update',
        model_name='Article',
        object_id=article.id,
        description=f'Unpublished article: {article.title}',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    messages.success(request, f'Article "{article.title}" unpublished successfully!')
    return redirect('articles:article_list')


def get_breaking_news_ajax(request):
    articles = Article.objects.filter(
        status='published',
        is_breaking=True,
        published_at__lte=timezone.now()
    ).order_by('-published_at')[:10]
    
    data = [{
        'title': article.title,
        'url': article.get_absolute_url(),
        'published_at': article.published_at.strftime('%H:%M'),
    } for article in articles]
    
    return JsonResponse({'articles': data})


@login_required
def article_statistics(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    
    if not request.user.can_manage_users and article.author != request.user:
        messages.error(request, 'Permission denied.')
        return redirect('articles:article_list')
    
    # Get statistics
    stats = ArticleStatistics.objects.get_or_create(article=article)[0]
    
    # Get daily views for chart
    from django.db.models import Count
    
    daily_views = UserActivityLog.objects.filter(
        model_name='Article',
        object_id=article.id,
        action='view',
        timestamp__gte=timezone.now() - timezone.timedelta(days=30)
    ).extra(
        {'day': "date(timestamp)"}
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    context = {
        'article': article,
        'stats': stats,
        'daily_views': daily_views,
        'page_title': f'Statistics for {article.title} - The Egerton Avenue',
    }
    
    return render(request, 'analytics/article_statistics.html', context)


# ============================================================
# DEDICATED SECTION VIEWS (Using categories template)
# ============================================================

def opinion_view(request):
    """Opinion section - The Egerton Avenue"""
    from apps.categories.models import Category
    from django.core.paginator import Paginator
    
    # Get the category
    category = get_object_or_404(Category, slug='opinion', is_active=True)
    
    # Get published articles in this category
    articles = Article.objects.filter(
        category=category,
        status='published',
        published_at__lte=timezone.now()
    ).select_related('author', 'category').prefetch_related('tags').order_by('-published_at', '-created_at')
    
    # Get featured article in this category
    featured_article = articles.filter(is_featured=True).first()
    
    # Pagination
    paginator = Paginator(articles, 12)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    # Get subcategories
    subcategories = category.children.filter(is_active=True)
    
    context = {
        'category': category,
        'articles': articles,
        'featured_article': featured_article,
        'subcategories': subcategories,
        'article_count': Article.objects.filter(category=category, status='published').count(),
        'page_title': 'Opinion - The Egerton Avenue',
        'section': 'opinion',
    }
    
    return render(request, 'categories/category_detail.html', context)


def environment_view(request):
    """Environment section - The Egerton Avenue"""
    from apps.categories.models import Category
    from django.core.paginator import Paginator
    
    # Get the category
    category = get_object_or_404(Category, slug='environment', is_active=True)
    
    # Get published articles in this category
    articles = Article.objects.filter(
        category=category,
        status='published',
        published_at__lte=timezone.now()
    ).select_related('author', 'category').prefetch_related('tags').order_by('-published_at', '-created_at')
    
    # Get featured article in this category
    featured_article = articles.filter(is_featured=True).first()
    
    # Pagination
    paginator = Paginator(articles, 12)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    # Get subcategories
    subcategories = category.children.filter(is_active=True)
    
    context = {
        'category': category,
        'articles': articles,
        'featured_article': featured_article,
        'subcategories': subcategories,
        'article_count': Article.objects.filter(category=category, status='published').count(),
        'page_title': 'Environment - The Egerton Avenue',
        'section': 'environment',
    }
    
    return render(request, 'categories/category_detail.html', context)


def society_view(request):
    """Society section - The Egerton Avenue"""
    from apps.categories.models import Category
    from django.core.paginator import Paginator
    
    # Get the category
    category = get_object_or_404(Category, slug='society', is_active=True)
    
    # Get published articles in this category
    articles = Article.objects.filter(
        category=category,
        status='published',
        published_at__lte=timezone.now()
    ).select_related('author', 'category').prefetch_related('tags').order_by('-published_at', '-created_at')
    
    # Get featured article in this category
    featured_article = articles.filter(is_featured=True).first()
    
    # Pagination
    paginator = Paginator(articles, 12)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    # Get subcategories
    subcategories = category.children.filter(is_active=True)
    
    context = {
        'category': category,
        'articles': articles,
        'featured_article': featured_article,
        'subcategories': subcategories,
        'article_count': Article.objects.filter(category=category, status='published').count(),
        'page_title': 'Society - The Egerton Avenue',
        'section': 'society',
    }
    
    return render(request, 'categories/category_detail.html', context)