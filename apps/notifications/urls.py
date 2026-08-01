from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('<int:notification_id>/', views.notification_detail, name='detail'),
    path('<int:notification_id>/mark-read/', views.mark_read, name='mark_read'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('<int:notification_id>/delete/', views.delete_notification, name='delete'),
    path('delete-all/', views.delete_all_notifications, name='delete_all'),
    path('preferences/', views.notification_preferences, name='preferences'),
    
    # API endpoints
    path('api/unread-count/', views.get_unread_count, name='unread_count'),
    path('api/recent/', views.get_notifications_ajax, name='recent'),
]