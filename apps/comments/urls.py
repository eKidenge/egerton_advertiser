from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    path('', views.comment_list, name='list'),
    path('<int:comment_id>/', views.comment_detail, name='detail'),
    path('pending/', views.pending_comments, name='pending'),
    path('approved/', views.approved_comments, name='approved'),
    path('spam/', views.spam_comments, name='spam'),
    path('<int:comment_id>/moderate/', views.comment_moderate, name='moderate'),
    path('<int:comment_id>/delete/', views.comment_delete, name='delete'),
    path('<int:comment_id>/vote/', views.vote_comment, name='vote'),
    path('add/<int:article_id>/', views.add_comment, name='add'),
    path('reply/<int:comment_id>/', views.add_reply, name='reply'),
]