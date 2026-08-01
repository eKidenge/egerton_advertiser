from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    # Public URLs
    path('', views.home, name='home'),
    path('latest/', views.latest_news, name='latest'),
    path('breaking-news/', views.breaking_news, name='breaking_news'),
    path('author/<int:author_id>/', views.author_articles, name='author_articles'),
    path('<slug:slug>/', views.article_detail, name='detail'),
    
    # AJAX endpoints
    path('api/breaking-news/', views.get_breaking_news_ajax, name='breaking_news_ajax'),
    
    # User URLs (require login)
    path('my/articles/', views.article_list, name='article_list'),
    path('create/', views.article_create, name='article_create'),
    path('<int:article_id>/edit/', views.article_edit, name='article_edit'),
    path('<int:article_id>/delete/', views.article_delete, name='article_delete'),
    path('<int:article_id>/publish/', views.publish_article, name='publish'),
    path('<int:article_id>/unpublish/', views.unpublish_article, name='unpublish'),
    path('<int:article_id>/statistics/', views.article_statistics, name='statistics'),
    
    # Status-specific lists
    path('status/drafts/', views.draft_articles, name='drafts'),
    path('status/published/', views.published_articles, name='published'),
    path('status/pending/', views.pending_articles, name='pending'),
    path('status/scheduled/', views.scheduled_articles, name='scheduled'),
    path('status/archived/', views.archived_articles, name='archived'),
    path('featured/', views.featured_articles, name='featured'),
]