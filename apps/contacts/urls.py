from django.urls import path
from . import views

app_name = 'contacts'

urlpatterns = [
    # Public
    path('', views.contact, name='contact'),
    path('success/', views.contact_success, name='success'),
    
    # Admin
    path('admin/messages/', views.contact_messages, name='messages'),
    path('admin/messages/<int:message_id>/', views.contact_message_detail, name='message_detail'),
    path('admin/messages/<int:message_id>/reply/', views.contact_message_reply, name='message_reply'),
    path('admin/messages/<int:message_id>/read/', views.mark_as_read, name='mark_read'),
    path('admin/messages/<int:message_id>/archive/', views.archive_message, name='archive'),
    path('admin/messages/<int:message_id>/spam/', views.mark_as_spam, name='spam'),
    path('admin/messages/<int:message_id>/delete/', views.message_delete, name='delete'),
]