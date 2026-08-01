from django.urls import path
from . import views

app_name = 'categories'

urlpatterns = [
    path('', views.category_list, name='list'),
    path('<slug:slug>/', views.category_detail, name='detail'),
    path('create/', views.category_create, name='create'),
    path('<int:category_id>/edit/', views.category_edit, name='edit'),
    path('<int:category_id>/delete/', views.category_delete, name='delete'),
]