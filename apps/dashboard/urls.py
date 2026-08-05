from django.urls import path, reverse
from django.shortcuts import redirect
from . import views
from apps.articles import views as article_views

app_name = 'dashboard'

urlpatterns = [
    # ============================================
    # MAIN DASHBOARD
    # ============================================
    path('', views.dashboard, name='home'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    
    # ============================================
    # ADMIN - ARTICLES (General)
    # ============================================
    path('admin/articles/', views.admin_articles, name='article_list'),
    path('admin/articles/create/', views.admin_article_create, name='article_create'),
    path('admin/articles/<int:article_id>/edit/', views.admin_article_edit, name='article_edit'),
    path('admin/articles/<int:article_id>/delete/', views.admin_article_delete, name='article_delete'),
    path('admin/articles/<int:article_id>/publish/', views.admin_article_publish, name='article_publish'),
    path('admin/articles/<int:article_id>/feature/', views.admin_article_feature, name='article_feature'),
    path('admin/articles/<int:article_id>/breaking/', views.admin_article_breaking, name='article_breaking'),
    
    # ============================================
    # ADMIN - ARTICLE MODERATION (Approve/Reject)
    # ============================================
    path('admin/articles/<int:article_id>/approve/', article_views.approve_article, name='article_approve'),
    path('admin/articles/<int:article_id>/reject/', article_views.reject_article, name='article_reject'),
    
    # ============================================
    # ADMIN - EDUCATION & RESEARCH
    # ============================================
    path('admin/education-research/', views.admin_education_research, name='education_research_list'),
    path('admin/education-research/<int:article_id>/edit/', views.admin_education_research_edit, name='education_research_edit'),
    path('admin/education-research/<int:article_id>/delete/', views.admin_education_research_delete, name='education_research_delete'),
    path('admin/education-research/<int:article_id>/publish/', views.admin_education_research_publish, name='education_research_publish'),
    path('admin/education-research/<int:article_id>/feature/', views.admin_education_research_feature, name='education_research_feature'),
    
    # ============================================
    # ADMIN - TECHNOLOGY
    # ============================================
    path('admin/technology/', views.admin_technology, name='technology_list'),
    path('admin/technology/<int:article_id>/edit/', views.admin_technology_edit, name='technology_edit'),
    path('admin/technology/<int:article_id>/delete/', views.admin_technology_delete, name='technology_delete'),
    path('admin/technology/<int:article_id>/publish/', views.admin_technology_publish, name='technology_publish'),
    path('admin/technology/<int:article_id>/feature/', views.admin_technology_feature, name='technology_feature'),
    
    # ============================================
    # ADMIN - BUSINESS & DIRECTORY
    # ============================================
    path('admin/business/', views.admin_business, name='business_list'),
    path('admin/business/<int:article_id>/edit/', views.admin_business_edit, name='business_edit'),
    path('admin/business/<int:article_id>/delete/', views.admin_business_delete, name='business_delete'),
    path('admin/business/<int:article_id>/publish/', views.admin_business_publish, name='business_publish'),
    path('admin/business/<int:article_id>/feature/', views.admin_business_feature, name='business_feature'),
    
    # ============================================
    # ADMIN - HEALTH
    # ============================================
    path('admin/health/', views.admin_health, name='health_list'),
    path('admin/health/<int:article_id>/edit/', views.admin_health_edit, name='health_edit'),
    path('admin/health/<int:article_id>/delete/', views.admin_health_delete, name='health_delete'),
    path('admin/health/<int:article_id>/publish/', views.admin_health_publish, name='health_publish'),
    path('admin/health/<int:article_id>/feature/', views.admin_health_feature, name='health_feature'),
    
    # ============================================
    # ADMIN - AGRICULTURE
    # ============================================
    path('admin/agriculture/', views.admin_agriculture, name='agriculture_list'),
    path('admin/agriculture/<int:article_id>/edit/', views.admin_agriculture_edit, name='agriculture_edit'),
    path('admin/agriculture/<int:article_id>/delete/', views.admin_agriculture_delete, name='agriculture_delete'),
    path('admin/agriculture/<int:article_id>/publish/', views.admin_agriculture_publish, name='agriculture_publish'),
    path('admin/agriculture/<int:article_id>/feature/', views.admin_agriculture_feature, name='agriculture_feature'),
    
    # ============================================
    # ADMIN - CAREERS
    # ============================================
    path('admin/careers/', views.admin_careers, name='careers_list'),
    path('admin/careers/<int:article_id>/edit/', views.admin_careers_edit, name='careers_edit'),
    path('admin/careers/<int:article_id>/delete/', views.admin_careers_delete, name='careers_delete'),
    path('admin/careers/<int:article_id>/publish/', views.admin_careers_publish, name='careers_publish'),
    path('admin/careers/<int:article_id>/feature/', views.admin_careers_feature, name='careers_feature'),
    
    # ============================================
    # ADMIN - OPINION
    # ============================================
    path('admin/opinion/', views.admin_opinion, name='opinion_list'),
    path('admin/opinion/<int:article_id>/edit/', views.admin_opinion_edit, name='opinion_edit'),
    path('admin/opinion/<int:article_id>/delete/', views.admin_opinion_delete, name='opinion_delete'),
    path('admin/opinion/<int:article_id>/publish/', views.admin_opinion_publish, name='opinion_publish'),
    
    # ============================================
    # ADMIN - ENVIRONMENT
    # ============================================
    path('admin/environment/', views.admin_environment, name='environment_list'),
    path('admin/environment/<int:article_id>/edit/', views.admin_environment_edit, name='environment_edit'),
    path('admin/environment/<int:article_id>/delete/', views.admin_environment_delete, name='environment_delete'),
    path('admin/environment/<int:article_id>/publish/', views.admin_environment_publish, name='environment_publish'),
    
    # ============================================
    # ADMIN - SOCIETY
    # ============================================
    path('admin/society/', views.admin_society, name='society_list'),
    path('admin/society/<int:article_id>/edit/', views.admin_society_edit, name='society_edit'),
    path('admin/society/<int:article_id>/delete/', views.admin_society_delete, name='society_delete'),
    path('admin/society/<int:article_id>/publish/', views.admin_society_publish, name='society_publish'),
    
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
    path('admin/users/<int:user_id>/role/', views.admin_user_change_role, name='user_change_role'),
    path('admin/users/<int:user_id>/reset-password/', views.admin_user_reset_password, name='user_reset_password'),
    path('admin/users/<int:user_id>/impersonate/', views.admin_user_impersonate, name='user_impersonate'),
    path('admin/users/bulk-action/', views.admin_user_bulk_action, name='user_bulk_action'),
    path('admin/users/export/', views.admin_user_export, name='user_export'),
    
    # ============================================
    # ADMIN - COMMENTS
    # ============================================
    path('admin/comments/', views.admin_comments, name='comment_list'),
    path('admin/comments/<int:comment_id>/moderate/', views.admin_comment_moderate, name='comment_moderate'),
    path('admin/comments/<int:comment_id>/delete/', views.admin_comment_delete, name='comment_delete'),
    path('admin/comments/bulk-action/', views.admin_comment_bulk_action, name='comment_bulk_action'),
    path('admin/comments/export/', views.admin_comment_export, name='comment_export'),
    
    # ============================================
    # ADMIN - ADVERTISEMENTS (ADSBOARD)
    # ============================================
    path('admin/ads/', views.admin_ads, name='ad_list'),
    path('admin/ads/create/', views.admin_ad_create, name='ad_create'),
    path('admin/ads/<int:ad_id>/edit/', views.admin_ad_edit, name='ad_edit'),
    path('admin/ads/<int:ad_id>/delete/', views.admin_ad_delete, name='ad_delete'),
    path('admin/ads/<int:ad_id>/approve/', views.admin_ad_approve, name='ad_approve'),
    path('admin/ads/<int:ad_id>/reject/', views.admin_ad_reject, name='ad_reject'),
    path('admin/ads/<int:ad_id>/pause/', views.admin_ad_pause, name='ad_pause'),
    path('admin/ads/<int:ad_id>/resume/', views.admin_ad_resume, name='ad_resume'),
    path('admin/ads/<int:ad_id>/duplicate/', views.admin_ad_duplicate, name='ad_duplicate'),
    path('admin/ads/<int:ad_id>/statistics/', views.admin_ad_statistics, name='ad_statistics'),
    path('admin/ads/bulk-action/', views.admin_ad_bulk_action, name='ad_bulk_action'),
    path('admin/ads/export/', views.admin_ad_export, name='ad_export'),
    path('admin/ads/positions/', views.admin_ad_positions, name='ad_positions'),
    path('admin/ads/performance/', views.admin_ad_performance, name='ad_performance'),
    path('admin/ads/revenue/', views.admin_ad_revenue, name='ad_revenue'),
    path('admin/ads/analytics/', views.admin_ad_analytics, name='ad_analytics'),
    path('admin/ads/placements/', views.admin_ad_placements, name='ad_placements'),
    path('admin/ads/schedule/', views.admin_ad_schedule, name='ad_schedule'),
    path('admin/ads/approvals/', views.admin_ad_approvals, name='ad_approvals'),
    path('admin/ads/reports/', views.admin_ad_reports, name='ad_reports'),
    
    # ============================================
    # ADMIN - PHOTOS
    # ============================================
    path('admin/photos/', views.admin_photos, name='photos_list'),
    path('admin/photos/<int:photo_id>/edit/', views.admin_photos_edit, name='photos_edit'),
    path('admin/photos/<int:photo_id>/delete/', views.admin_photos_delete, name='photos_delete'),
    path('admin/photos/<int:photo_id>/feature/', views.admin_photos_feature, name='photos_feature'),
    
    # ============================================
    # ADMIN - VIDEOS
    # ============================================
    path('admin/videos/', views.admin_videos, name='video_list'),
    path('admin/videos/<int:video_id>/edit/', views.admin_video_edit, name='video_edit'),
    path('admin/videos/<int:video_id>/delete/', views.admin_video_delete, name='video_delete'),
    path('admin/videos/<int:video_id>/feature/', views.admin_video_feature, name='video_feature'),
    
    # ============================================
    # ADMIN - CONTACTS
    # ============================================
    path('admin/contacts/', views.admin_contacts, name='contact_list'),
    path('admin/contacts/<int:contact_id>/', views.admin_contact_detail, name='contact_detail'),
    path('admin/contacts/<int:contact_id>/delete/', views.admin_contact_delete, name='contact_delete'),
    path('admin/contacts/<int:contact_id>/reply/', views.admin_contact_reply, name='contact_reply'),
    path('admin/contacts/<int:contact_id>/mark-read/', views.admin_contact_mark_read, name='contact_mark_read'),
    path('admin/contacts/bulk-action/', views.admin_contact_bulk_action, name='contact_bulk_action'),
    
    # ============================================
    # ADMIN - MEDIA
    # ============================================
    path('admin/media/', views.admin_media, name='media_list'),
    path('admin/media/<int:media_id>/delete/', views.admin_media_delete, name='media_delete'),
    path('admin/media/<int:media_id>/edit/', views.admin_media_edit, name='media_edit'),
    path('admin/media/bulk-upload/', views.admin_media_bulk_upload, name='media_bulk_upload'),
    path('admin/media/bulk-delete/', views.admin_media_bulk_delete, name='media_bulk_delete'),
    path('admin/media/gallery/', views.admin_media_gallery, name='media_gallery'),
    
    # ============================================
    # ADMIN - SUBSCRIBERS
    # ============================================
    path('admin/subscribers/', views.admin_subscribers, name='subscriber_list'),
    path('admin/subscribers/<int:subscriber_id>/delete/', views.admin_subscriber_delete, name='subscriber_delete'),
    path('admin/subscribers/<int:subscriber_id>/toggle/', views.admin_subscriber_toggle, name='subscriber_toggle'),
    path('admin/subscribers/export/', views.admin_subscriber_export, name='subscriber_export'),
    path('admin/subscribers/bulk-action/', views.admin_subscriber_bulk_action, name='subscriber_bulk_action'),
    
    # ============================================
    # ADMIN - NEWSLETTERS
    # ============================================
    path('admin/newsletters/', views.admin_newsletters, name='newsletter_list'),
    path('admin/newsletters/create/', views.admin_newsletter_create, name='newsletter_create'),
    path('admin/newsletters/<int:newsletter_id>/edit/', views.admin_newsletter_edit, name='newsletter_edit'),
    path('admin/newsletters/<int:newsletter_id>/send/', views.admin_newsletter_send, name='newsletter_send'),
    path('admin/newsletters/<int:newsletter_id>/delete/', views.admin_newsletter_delete, name='newsletter_delete'),
    path('admin/newsletters/<int:newsletter_id>/duplicate/', views.admin_newsletter_duplicate, name='newsletter_duplicate'),
    path('admin/newsletters/<int:newsletter_id>/preview/', views.admin_newsletter_preview, name='newsletter_preview'),
    path('admin/newsletters/bulk-action/', views.admin_newsletter_bulk_action, name='newsletter_bulk_action'),
    
    # ============================================
    # ADMIN - SETTINGS
    # ============================================
    path('admin/settings/', views.admin_settings, name='settings'),
    path('admin/settings/update/', views.admin_settings_update, name='settings_update'),
    path('admin/settings/ajax/', views.admin_settings_ajax, name='settings_ajax'),
    
    # ============================================
    # ADMIN - ANALYTICS & REPORTS
    # ============================================
    path('admin/analytics/', views.admin_analytics, name='analytics'),
    path('admin/analytics/content/', views.admin_analytics_content, name='analytics_content'),
    path('admin/analytics/audience/', views.admin_analytics_audience, name='analytics_audience'),
    path('admin/analytics/revenue/', views.admin_analytics_revenue, name='analytics_revenue'),
    path('admin/analytics/export/', views.admin_analytics_export, name='analytics_export'),
    path('admin/analytics/realtime/', views.admin_analytics_realtime, name='analytics_realtime'),
    
    # ============================================
    # USER DASHBOARD VIEWS
    # ============================================
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/activity/', views.profile_activity, name='profile_activity'),
    path('profile/preferences/', views.profile_preferences, name='profile_preferences'),
    path('activity-log/', views.activity_log, name='activity_log'),
    path('notifications/', views.notifications, name='notifications'),
    path('settings/', views.settings, name='settings'),
    path('settings/update/', views.settings_update, name='settings_update'),
    
    # ============================================
    # WIDGET MANAGEMENT
    # ============================================
    path('widgets/', views.widget_list, name='widget_list'),
    path('widgets/add/', views.add_widget, name='add_widget'),
    path('widgets/<int:widget_id>/edit/', views.edit_widget, name='edit_widget'),
    path('widgets/<int:widget_id>/delete/', views.delete_widget, name='delete_widget'),
    path('widgets/<int:widget_id>/toggle/', views.toggle_widget, name='toggle_widget'),
    path('widgets/reorder/', views.reorder_widgets, name='reorder_widgets'),
    path('widgets/reset/', views.reset_widgets, name='reset_widgets'),
    
    # ============================================
    # NOTIFICATIONS
    # ============================================
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/clear/', views.clear_notifications, name='clear_notifications'),
    
    # ============================================
    # API ENDPOINTS (AJAX)
    # ============================================
    path('api/stats/', views.api_stats, name='api_stats'),
    path('api/chart-data/', views.api_chart_data, name='api_chart_data'),
    path('api/recent-activity/', views.api_recent_activity, name='api_recent_activity'),
    path('api/dashboard-widgets/', views.api_dashboard_widgets, name='api_dashboard_widgets'),
    path('api/notifications/', views.api_notifications, name='api_notifications'),
    path('api/ad-stats/', views.api_ad_stats, name='api_ad_stats'),
    path('api/user-stats/', views.api_user_stats, name='api_user_stats'),
    path('api/content-stats/', views.api_content_stats, name='api_content_stats'),
    path('api/bulk-action/', views.api_bulk_action, name='api_bulk_action'),
    path('api/search/', views.api_search, name='api_search'),
    path('api/export/', views.api_export, name='api_export'),
]