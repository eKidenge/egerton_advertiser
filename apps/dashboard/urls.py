from django.urls import path, reverse
from django.shortcuts import redirect
from . import views

app_name = 'dashboard'

urlpatterns = [
    # ============================================
    # MAIN DASHBOARD
    # ============================================
    path('', views.dashboard, name='home'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    
    # ============================================
    # ADMIN - ARTICLES
    # ============================================
    path('admin/articles/', views.admin_articles, name='article_list'),
    path('admin/articles/create/', views.admin_article_create, name='article_create'),
    path('admin/articles/<int:article_id>/edit/', views.admin_article_edit, name='article_edit'),
    path('admin/articles/<int:article_id>/delete/', views.admin_article_delete, name='article_delete'),
    path('admin/articles/<int:article_id>/publish/', views.admin_article_publish, name='article_publish'),
    path('admin/articles/<int:article_id>/feature/', views.admin_article_feature, name='article_feature'),
    path('admin/articles/<int:article_id>/breaking/', views.admin_article_breaking, name='article_breaking'),
    
    # ============================================
    # ADMIN - CATEGORIES
    # ============================================
    path('admin/categories/', views.admin_categories, name='category_list'),
    path('admin/categories/create/', views.admin_category_create, name='category_create'),
    path('admin/categories/<int:category_id>/edit/', views.admin_category_edit, name='category_edit'),
    path('admin/categories/<int:category_id>/delete/', views.admin_category_delete, name='category_delete'),
    
    # ============================================
    # ADMIN - TAGS
    # ============================================
    path('admin/tags/', views.admin_tags, name='tag_list'),
    path('admin/tags/create/', views.admin_tag_create, name='tag_create'),
    path('admin/tags/<int:tag_id>/edit/', views.admin_tag_edit, name='tag_edit'),
    path('admin/tags/<int:tag_id>/delete/', views.admin_tag_delete, name='tag_delete'),
    
    # ============================================
    # ADMIN - USERS
    # ============================================
    path('admin/users/', views.admin_users, name='user_list'),
    path('admin/users/create/', views.admin_user_create, name='user_create'),
    path('admin/users/<int:user_id>/edit/', views.admin_user_edit, name='user_edit'),
    path('admin/users/<int:user_id>/delete/', views.admin_user_delete, name='user_delete'),
    path('admin/users/<int:user_id>/toggle/', views.admin_user_toggle_active, name='user_toggle'),
    
    # ============================================
    # ADMIN - COMMENTS
    # ============================================
    path('admin/comments/', views.admin_comments, name='comment_list'),
    path('admin/comments/<int:comment_id>/moderate/', views.admin_comment_moderate, name='comment_moderate'),
    path('admin/comments/<int:comment_id>/delete/', views.admin_comment_delete, name='comment_delete'),
    
    # ============================================
    # ADMIN - ADVERTISEMENTS
    # ============================================
    path('admin/ads/', views.admin_ads, name='ad_list'),
    path('admin/ads/create/', views.admin_ad_create, name='ad_create'),
    path('admin/ads/<int:ad_id>/edit/', views.admin_ad_edit, name='ad_edit'),
    path('admin/ads/<int:ad_id>/delete/', views.admin_ad_delete, name='ad_delete'),
    path('admin/ads/<int:ad_id>/approve/', views.admin_ad_approve, name='ad_approve'),
    
    # ============================================
    # ADMIN - CONTACTS
    # ============================================
    path('admin/contacts/', views.admin_contacts, name='contact_list'),
    path('admin/contacts/<int:contact_id>/', views.admin_contact_detail, name='contact_detail'),
    path('admin/contacts/<int:contact_id>/delete/', views.admin_contact_delete, name='contact_delete'),
    
    # ============================================
    # ADMIN - MEDIA
    # ============================================
    path('admin/media/', views.admin_media, name='media_list'),
    path('admin/media/<int:media_id>/delete/', views.admin_media_delete, name='media_delete'),
    
    # ============================================
    # ADMIN - SUBSCRIBERS
    # ============================================
    path('admin/subscribers/', views.admin_subscribers, name='subscriber_list'),
    path('admin/subscribers/<int:subscriber_id>/delete/', views.admin_subscriber_delete, name='subscriber_delete'),
    
    # ============================================
    # ADMIN - NEWSLETTERS
    # ============================================
    path('admin/newsletters/', views.admin_newsletters, name='newsletter_list'),
    path('admin/newsletters/create/', views.admin_newsletter_create, name='newsletter_create'),
    path('admin/newsletters/<int:newsletter_id>/edit/', views.admin_newsletter_edit, name='newsletter_edit'),
    path('admin/newsletters/<int:newsletter_id>/send/', views.admin_newsletter_send, name='newsletter_send'),
    path('admin/newsletters/<int:newsletter_id>/delete/', views.admin_newsletter_delete, name='newsletter_delete'),
    
    # ============================================
    # ADMIN - SETTINGS
    # ============================================
    path('admin/settings/', views.admin_settings, name='settings'),
    
    # ============================================
    # USER DASHBOARD VIEWS
    # ============================================
    path('profile/', views.profile, name='profile'),
    path('activity-log/', views.activity_log, name='activity_log'),
    path('notifications/', views.notifications, name='notifications'),
    path('settings/', views.settings, name='settings'),
    
    # ============================================
    # WIDGET MANAGEMENT
    # ============================================
    path('widgets/add/', views.add_widget, name='add_widget'),
    path('widgets/<int:widget_id>/edit/', views.edit_widget, name='edit_widget'),
    path('widgets/<int:widget_id>/delete/', views.delete_widget, name='delete_widget'),
    path('widgets/reorder/', views.reorder_widgets, name='reorder_widgets'),
    
    # ============================================
    # NOTIFICATIONS
    # ============================================
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
]