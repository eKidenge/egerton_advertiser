from django.urls import path
from . import views

app_name = 'tags'

urlpatterns = [
    path('', views.tag_list, name='list'),
    path('<slug:slug>/', views.tag_detail, name='detail'),
    path('create/', views.tag_create, name='create'),
    path('<int:tag_id>/edit/', views.tag_edit, name='edit'),
    path('<int:tag_id>/delete/', views.tag_delete, name='delete'),
]