from django.urls import path, re_path
from . import views

app_name = 'articles'

urlpatterns = [
    # ============================================================
    # PUBLIC VIEWS
    # ============================================================
    
    # Homepage
    path('', views.home, name='home'),
    
    # Latest news
    path('latest/', views.latest_news, name='latest'),
    
    # Breaking news
    path('breaking-news/', views.breaking_news, name='breaking_news'),
    
    # Author articles
    path('author/<int:author_id>/', views.author_articles, name='author_articles'),
    
    # ============================================================
    # CATEGORY VIEWS - For navigation links
    # ============================================================
    
    # Category view - MUST come before detail view to avoid conflict
    path('category/<slug:slug>/', views.category_view, name='category'),
    
    # Dedicated section views (using categories template)
    path('opinion/', views.opinion_view, name='opinion'),
    path('environment/', views.environment_view, name='environment'),
    path('society/', views.society_view, name='society'),
    
    # ============================================================
    # PHOTOS & VIDEO
    # ============================================================
    
    # Photo gallery
    path('photos/', views.photos, name='photos'),
    
    # Video gallery
    path('video/', views.video, name='video'),
    
    # ============================================================
    # ARTICLE DETAIL - MUST come LAST to catch all slugs
    # ============================================================
    
    # Article detail view - catches all remaining slugs
    # Using re_path to allow colons, hyphens, underscores, letters and numbers
    re_path(r'^(?P<slug>[-\w:]+)/$', views.article_detail, name='detail'),
    
    # ============================================================
    # AJAX ENDPOINTS
    # ============================================================
    
    # Breaking news API
    path('api/breaking-news/', views.get_breaking_news_ajax, name='breaking_news_ajax'),
    
    # ============================================================
    # USER / AUTHOR VIEWS (require login)
    # ============================================================
    
    # Article management
    path('my/articles/', views.article_list, name='article_list'),
    
    # Create article
    path('create/', views.article_create, name='article_create'),
    
    # Edit article
    path('<int:article_id>/edit/', views.article_edit, name='article_edit'),
    
    # Delete article
    path('<int:article_id>/delete/', views.article_delete, name='article_delete'),
    
    # Publish article
    path('<int:article_id>/publish/', views.publish_article, name='publish'),
    
    # Unpublish article
    path('<int:article_id>/unpublish/', views.unpublish_article, name='unpublish'),
    
    # Article statistics
    path('<int:article_id>/statistics/', views.article_statistics, name='statistics'),
    
    # ============================================================
    # STATUS-SPECIFIC LISTS
    # ============================================================
    
    # Draft articles
    path('status/drafts/', views.draft_articles, name='drafts'),
    
    # Published articles
    path('status/published/', views.published_articles, name='published'),
    
    # Pending articles
    path('status/pending/', views.pending_articles, name='pending'),
    
    # Scheduled articles
    path('status/scheduled/', views.scheduled_articles, name='scheduled'),
    
    # Archived articles
    path('status/archived/', views.archived_articles, name='archived'),
    
    # Featured articles
    path('featured/', views.featured_articles, name='featured'),
]