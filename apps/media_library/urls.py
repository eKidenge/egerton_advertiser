from django.urls import path
from . import views

app_name = 'media_library'

urlpatterns = [
    # ============================================================
    # USER'S PERSONAL MEDIA LIBRARY (Logged in users only)
    # ============================================================
    path('', views.media_library, name='library'),
    path('upload/', views.media_upload, name='upload'),
    path('gallery/', views.media_gallery, name='gallery'),
    path('<int:media_id>/', views.media_detail, name='detail'),
    path('<int:media_id>/delete/', views.media_delete, name='delete'),
    path('bulk-upload/', views.bulk_upload_media, name='bulk_upload'),
    
    # ============================================================
    # PUBLIC GALLERY VIEWS (No login required - shows ALL media)
    # ============================================================
    path('photos/', views.public_photos, name='public_photos'),
    path('videos/', views.public_videos, name='public_videos'),
    
    # ============================================================
    # ADMIN VIEWS (Shows ALL media from ALL users)
    # ============================================================
    path('admin/', views.admin_media_library, name='admin_library'),
    path('admin/all/', views.admin_media_library, name='admin_all'),
    
    # ============================================================
    # TAG MANAGEMENT
    # ============================================================
    path('tags/', views.tag_list, name='tag_list'),
    path('tags/create/', views.tag_create, name='tag_create'),
    path('tags/<int:tag_id>/edit/', views.tag_edit, name='tag_edit'),
    path('tags/<int:tag_id>/delete/', views.tag_delete, name='tag_delete'),
    
    # ============================================================
    # CATEGORY MANAGEMENT
    # ============================================================
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:category_id>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:category_id>/delete/', views.category_delete, name='category_delete'),
]