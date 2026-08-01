from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_dashboard, name='dashboard'),
    path('visitors/', views.visitor_statistics, name='visitors'),
    path('articles/', views.article_statistics, name='articles'),
    path('traffic/', views.traffic_sources, name='traffic'),
    path('realtime/', views.realtime_data, name='realtime'),
    
    # API endpoints
    path('api/track/', views.track_event, name='track_event'),
]