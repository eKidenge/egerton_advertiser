from django.urls import path
from . import views

app_name = 'newsletter'

urlpatterns = [
    # Public URLs
    path('subscribe/', views.subscribe, name='subscribe'),
    path('unsubscribe/', views.unsubscribe, name='unsubscribe'),
    path('unsubscribe/<str:email>/', views.unsubscribe, name='unsubscribe_email'),
    
    # Tracking URLs
    path('track/open/<int:newsletter_id>/<int:subscriber_id>/', views.track_open, name='track_open'),
    path('track/click/<int:newsletter_id>/<int:subscriber_id>/', views.track_click, name='track_click'),
    
    # Admin URLs
    path('admin/subscribers/', views.subscriber_list, name='subscriber_list'),
    path('admin/subscribers/<int:subscriber_id>/', views.subscriber_detail, name='subscriber_detail'),
    path('admin/newsletters/', views.newsletter_list, name='newsletter_list'),
    path('admin/newsletters/create/', views.newsletter_create, name='create'),
    path('admin/newsletters/<int:newsletter_id>/edit/', views.newsletter_edit, name='edit'),
    path('admin/newsletters/<int:newsletter_id>/send/', views.newsletter_send, name='send'),
    path('admin/newsletters/<int:newsletter_id>/history/', views.newsletter_history, name='history'),
]