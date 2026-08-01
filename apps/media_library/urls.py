from django.urls import path
from . import views

app_name = 'media_library'

urlpatterns = [
    # Media files
    path('', views.media_library, name='library'),
    path('upload/', views.media_upload, name='upload'),
    path('gallery/', views.media_gallery, name='gallery'),
    path('<int:media_id>/', views.media_detail, name='detail'),
    path('<int:media_id>/delete/', views.media_delete, name='delete'),
    path('bulk-upload/', views.bulk_upload_media, name='bulk_upload'),
    
    # Tags
    path('tags/', views.tag_list, name='tag_list'),
    path('tags/create/', views.tag_create, name='tag_create'),
    path('tags/<int:tag_id>/edit/', views.tag_edit, name='tag_edit'),
    path('tags/<int:tag_id>/delete/', views.tag_delete, name='tag_delete'),
    
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:category_id>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:category_id>/delete/', views.category_delete, name='category_delete'),
]