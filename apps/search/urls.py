from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('', views.search, name='search'),
    path('advanced/', views.advanced_search, name='advanced'),
    path('api/track-click/', views.track_click, name='track_click'),
    path('statistics/', views.search_statistics, name='statistics'),
]