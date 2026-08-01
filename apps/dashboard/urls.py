from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Main Dashboard
    path('', views.dashboard, name='home'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    
    # Articles
    path('admin/articles/', views.admin_articles, name='admin_articles'),
    path('admin/articles/create/', views.admin_article_create, name='admin_article_create'),
    path('admin/articles/<int:article_id>/edit/', views.admin_article_edit, name='admin_article_edit'),
    path('admin/articles/<int:article_id>/delete/', views.admin_article_delete, name='admin_article_delete'),
    path('admin/articles/<int:article_id>/publish/', views.admin_article_publish, name='admin_article_publish'),
    path('admin/articles/<int:article_id>/feature/', views.admin_article_feature, name='admin_article_feature'),
    path('admin/articles/<int:article_id>/breaking/', views.admin_article_breaking, name='admin_article_breaking'),
    
    # Categories
    path('admin/categories/', views.admin_categories, name='admin_categories'),
    path('admin/categories/create/', views.admin_category_create, name='admin_category_create'),
    path('admin/categories/<int:category_id>/edit/', views.admin_category_edit, name='admin_category_edit'),
    path('admin/categories/<int:category_id>/delete/', views.admin_category_delete, name='admin_category_delete'),
    
    # Tags
    path('admin/tags/', views.admin_tags, name='admin_tags'),
    path('admin/tags/create/', views.admin_tag_create, name='admin_tag_create'),
    path('admin/tags/<int:tag_id>/edit/', views.admin_tag_edit, name='admin_tag_edit'),
    path('admin/tags/<int:tag_id>/delete/', views.admin_tag_delete, name='admin_tag_delete'),
    
    # Users
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/create/', views.admin_user_create, name='admin_user_create'),
    path('admin/users/<int:user_id>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('admin/users/<int:user_id>/delete/', views.admin_user_delete, name='admin_user_delete'),
    path('admin/users/<int:user_id>/toggle/', views.admin_user_toggle_active, name='admin_user_toggle'),
    
    # Comments
    path('admin/comments/', views.admin_comments, name='admin_comments'),
    path('admin/comments/<int:comment_id>/moderate/', views.admin_comment_moderate, name='admin_comment_moderate'),
    path('admin/comments/<int:comment_id>/delete/', views.admin_comment_delete, name='admin_comment_delete'),
    
    # Ads
    path('admin/ads/', views.admin_ads, name='admin_ads'),
    path('admin/ads/create/', views.admin_ad_create, name='admin_ad_create'),
    path('admin/ads/<int:ad_id>/edit/', views.admin_ad_edit, name='admin_ad_edit'),
    path('admin/ads/<int:ad_id>/delete/', views.admin_ad_delete, name='admin_ad_delete'),
    path('admin/ads/<int:ad_id>/approve/', views.admin_ad_approve, name='admin_ad_approve'),
    
    # Contacts
    path('admin/contacts/', views.admin_contacts, name='admin_contacts'),
    path('admin/contacts/<int:contact_id>/', views.admin_contact_detail, name='admin_contact_detail'),
    path('admin/contacts/<int:contact_id>/delete/', views.admin_contact_delete, name='admin_contact_delete'),
    
    # Media
    path('admin/media/', views.admin_media, name='admin_media'),
    path('admin/media/<int:media_id>/delete/', views.admin_media_delete, name='admin_media_delete'),
    
    # Subscribers
    path('admin/subscribers/', views.admin_subscribers, name='admin_subscribers'),
    path('admin/subscribers/<int:subscriber_id>/delete/', views.admin_subscriber_delete, name='admin_subscriber_delete'),
    
    # Newsletters
    path('admin/newsletters/', views.admin_newsletters, name='admin_newsletters'),
    path('admin/newsletters/create/', views.admin_newsletter_create, name='admin_newsletter_create'),
    path('admin/newsletters/<int:newsletter_id>/edit/', views.admin_newsletter_edit, name='admin_newsletter_edit'),
    path('admin/newsletters/<int:newsletter_id>/send/', views.admin_newsletter_send, name='admin_newsletter_send'),
    path('admin/newsletters/<int:newsletter_id>/delete/', views.admin_newsletter_delete, name='admin_newsletter_delete'),
    
    # Settings
    path('admin/settings/', views.admin_settings, name='admin_settings'),
    
    # Original dashboard views
    path('profile/', views.profile, name='profile'),
    path('activity-log/', views.activity_log, name='activity_log'),
    path('notifications/', views.notifications, name='notifications'),
    path('settings/', views.settings, name='settings'),
    path('widgets/add/', views.add_widget, name='add_widget'),
    path('widgets/<int:widget_id>/edit/', views.edit_widget, name='edit_widget'),
    path('widgets/<int:widget_id>/delete/', views.delete_widget, name='delete_widget'),
    path('widgets/reorder/', views.reorder_widgets, name='reorder_widgets'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),

    # Add these to your existing dashboard urls.py

urlpatterns += [
    # Admin Dashboard Main
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    
    # Admin Articles
    path('admin/articles/', views.admin_articles, name='admin_articles'),
    path('admin/articles/create/', views.admin_article_create, name='admin_article_create'),
    path('admin/articles/<int:article_id>/edit/', views.admin_article_edit, name='admin_article_edit'),
    path('admin/articles/<int:article_id>/delete/', views.admin_article_delete, name='admin_article_delete'),
    path('admin/articles/<int:article_id>/publish/', views.admin_article_publish, name='admin_article_publish'),
    path('admin/articles/<int:article_id>/feature/', views.admin_article_feature, name='admin_article_feature'),
    path('admin/articles/<int:article_id>/breaking/', views.admin_article_breaking, name='admin_article_breaking'),
    
    # Admin Categories
    path('admin/categories/', views.admin_categories, name='admin_categories'),
    path('admin/categories/create/', views.admin_category_create, name='admin_category_create'),
    path('admin/categories/<int:category_id>/edit/', views.admin_category_edit, name='admin_category_edit'),
    path('admin/categories/<int:category_id>/delete/', views.admin_category_delete, name='admin_category_delete'),
    
    # Admin Tags
    path('admin/tags/', views.admin_tags, name='admin_tags'),
    path('admin/tags/create/', views.admin_tag_create, name='admin_tag_create'),
    path('admin/tags/<int:tag_id>/edit/', views.admin_tag_edit, name='admin_tag_edit'),
    path('admin/tags/<int:tag_id>/delete/', views.admin_tag_delete, name='admin_tag_delete'),
    
    # Admin Users
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/create/', views.admin_user_create, name='admin_user_create'),
    path('admin/users/<int:user_id>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('admin/users/<int:user_id>/delete/', views.admin_user_delete, name='admin_user_delete'),
    path('admin/users/<int:user_id>/toggle/', views.admin_user_toggle_active, name='admin_user_toggle'),
    
    # Admin Comments
    path('admin/comments/', views.admin_comments, name='admin_comments'),
    path('admin/comments/<int:comment_id>/moderate/', views.admin_comment_moderate, name='admin_comment_moderate'),
    path('admin/comments/<int:comment_id>/delete/', views.admin_comment_delete, name='admin_comment_delete'),
    
    # Admin Ads
    path('admin/ads/', views.admin_ads, name='admin_ads'),
    path('admin/ads/create/', views.admin_ad_create, name='admin_ad_create'),
    path('admin/ads/<int:ad_id>/edit/', views.admin_ad_edit, name='admin_ad_edit'),
    path('admin/ads/<int:ad_id>/delete/', views.admin_ad_delete, name='admin_ad_delete'),
    path('admin/ads/<int:ad_id>/approve/', views.admin_ad_approve, name='admin_ad_approve'),
    
    # Admin Contacts
    path('admin/contacts/', views.admin_contacts, name='admin_contacts'),
    path('admin/contacts/<int:contact_id>/', views.admin_contact_detail, name='admin_contact_detail'),
    path('admin/contacts/<int:contact_id>/delete/', views.admin_contact_delete, name='admin_contact_delete'),
    
    # Admin Media
    path('admin/media/', views.admin_media, name='admin_media'),
    path('admin/media/<int:media_id>/delete/', views.admin_media_delete, name='admin_media_delete'),
    
    # Admin Subscribers
    path('admin/subscribers/', views.admin_subscribers, name='admin_subscribers'),
    path('admin/subscribers/<int:subscriber_id>/delete/', views.admin_subscriber_delete, name='admin_subscriber_delete'),
    
    # Admin Newsletters
    path('admin/newsletters/', views.admin_newsletters, name='admin_newsletters'),
    path('admin/newsletters/create/', views.admin_newsletter_create, name='admin_newsletter_create'),
    path('admin/newsletters/<int:newsletter_id>/edit/', views.admin_newsletter_edit, name='admin_newsletter_edit'),
    path('admin/newsletters/<int:newsletter_id>/send/', views.admin_newsletter_send, name='admin_newsletter_send'),
    path('admin/newsletters/<int:newsletter_id>/delete/', views.admin_newsletter_delete, name='admin_newsletter_delete'),
    
    # Admin Settings
    path('admin/settings/', views.admin_settings, name='admin_settings'),
]