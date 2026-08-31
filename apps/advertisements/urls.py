# apps/advertisements/urls.py

from django.urls import path
from . import views

app_name = 'advertisements'

urlpatterns = [
    # List all advertisements
    path('', views.advertisement_list, name='list'),
    
    # Create advertisement
    path('create/', views.advertisement_create, name='create'),
    
    # Detail view
    path('<int:ad_id>/', views.advertisement_detail, name='detail'),
    
    # Edit view
    path('<int:ad_id>/edit/', views.advertisement_edit, name='edit'),
    
    # Delete view
    path('<int:ad_id>/delete/', views.advertisement_delete, name='delete'),
    
    # Toggle (Pause/Resume) view - ADD THIS
    path('<int:ad_id>/toggle/', views.advertisement_toggle, name='toggle'),
    
    # Positions view
    path('positions/', views.advertisement_positions, name='positions'),
    
    # Statistics view
    path('statistics/', views.advertisement_statistics, name='statistics'),
    
    # Moderation URLs
    path('<int:ad_id>/approve/', views.admin_ad_approve, name='approve'),
    path('<int:ad_id>/reject/', views.admin_ad_reject, name='reject'),
    
    # API endpoints
    path('api/get/<str:position>/', views.get_ad_by_position, name='get_by_position'),
]