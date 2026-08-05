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
    
    # ============================================================
    # MAIN NAVIGATION SECTION VIEWS (All in one place)
    # ============================================================
    
    # EDUCATION & RESEARCH
    path('education-research/', views.education_research, name='education_research'),
    
    # TECHNOLOGY
    path('technology/', views.technology, name='technology'),
    
    # BUSINESS & DIRECTORY
    path('business-directory/', views.business_directory, name='business_directory'),
    
    # HEALTH
    path('health/', views.health, name='health'),
    
    # AGRICULTURE
    path('agriculture/', views.agriculture, name='agriculture'),
    
    # ENVIRONMENT
    path('environment/', views.environment, name='environment'),
    
    # CAREERS
    path('careers/', views.careers, name='careers'),
    
    # OPINION
    path('opinion/', views.opinion, name='opinion'),
    
    # SOCIETY
    path('society/', views.society, name='society'),
    
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
    
    # NEW: Section-specific create URLs for Journalists
    path('create/opinion/', views.create_opinion_article, name='create_opinion'),
    path('create/environment/', views.create_environment_article, name='create_environment'),
    path('create/society/', views.create_society_article, name='create_society'),
    path('create/photos/', views.create_photos_article, name='create_photos'),
    path('create/video/', views.create_video_article, name='create_video'),
    
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
    # ADMIN / MODERATION VIEWS (Admin & Editor only)
    # ============================================================
    
    # Approve pending article
    path('admin/<int:article_id>/approve/', views.approve_article, name='approve'),
    
    # Reject pending article
    path('admin/<int:article_id>/reject/', views.reject_article, name='reject'),
    
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
    # ARTS & CULTURE
    path('arts-culture/', views.arts_culture, name='arts_culture'),
]