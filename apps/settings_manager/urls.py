from django.urls import path
from . import views

app_name = 'settings'

urlpatterns = [
    path('', views.site_settings, name='site'),
    path('general/', views.general_settings, name='general'),
    path('appearance/', views.appearance_settings, name='appearance'),
    path('email/', views.email_settings, name='email'),
    path('seo/', views.seo_settings, name='seo'),
    path('social/', views.social_media_settings, name='social'),
    path('advertisement/', views.advertisement_settings, name='advertisement'),
    
    # API endpoints
    path('api/update/', views.update_setting_ajax, name='update_setting'),
    path('api/get/', views.get_setting_ajax, name='get_setting'),
]