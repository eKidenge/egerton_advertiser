from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import GenericSitemap
from django.views.decorators.cache import cache_page

from apps.articles.views import home
from apps.accounts.views import user_login, user_logout, user_register
from apps.articles.models import Article
from apps.categories.models import Category

# Sitemap configuration
sitemaps = {
    'articles': GenericSitemap({
        'queryset': Article.objects.filter(status='published'),
        'date_field': 'published_at',
    }, priority=0.6),
    'categories': GenericSitemap({
        'queryset': Category.objects.filter(is_active=True),
        'date_field': 'updated_at',
    }, priority=0.4),
}

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Home
    path('', home, name='home'),
    
    # Static Pages
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('privacy-policy/', TemplateView.as_view(template_name='privacy_policy.html'), name='privacy_policy'),
    path('terms-of-service/', TemplateView.as_view(template_name='terms_of_service.html'), name='terms_of_service'),
    path('cookie-policy/', TemplateView.as_view(template_name='cookie_policy.html'), name='cookie_policy'),
    path('sitemap-page/', TemplateView.as_view(template_name='sitemap.html'), name='sitemap'),
    
    # Authentication
    path('accounts/login/', user_login, name='login'),
    path('accounts/logout/', user_logout, name='logout'),
    path('accounts/register/', user_register, name='register'),
    
    # App URLs
    path('accounts/', include('apps.accounts.urls')),
    path('articles/', include('apps.articles.urls')),
    path('categories/', include('apps.categories.urls')),
    path('tags/', include('apps.tags.urls')),
    path('comments/', include('apps.comments.urls')),
    path('advertisements/', include('apps.advertisements.urls')),
    path('media-library/', include('apps.media_library.urls')),
    path('newsletter/', include('apps.newsletter.urls')),
    path('contacts/', include('apps.contacts.urls')),
    path('analytics/', include('apps.analytics.urls')),
    path('search/', include('apps.search.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('settings/', include('apps.settings_manager.urls')),
    
    # Third-party integrations
    path('ckeditor/', include('ckeditor_uploader.urls')),
    
    # Sitemap
    path('sitemap.xml', cache_page(86400)(sitemap), {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    
    # Robots.txt
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    
    # Error pages
    path('403/', TemplateView.as_view(template_name='403.html'), name='403'),
    path('404/', TemplateView.as_view(template_name='404.html'), name='404'),
    path('500/', TemplateView.as_view(template_name='500.html'), name='500'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Custom error handlers
handler403 = 'apps.accounts.views.handler403'
handler404 = 'apps.accounts.views.handler404'
handler500 = 'apps.accounts.views.handler500'