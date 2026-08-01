from django.contrib import admin
from django.utils.html import format_html
from .models import Comment, CommentVote

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('content_preview', 'user', 'article', 'status', 
                   'created_at', 'likes', 'dislikes')
    list_filter = ('status', 'created_at', 'article')
    search_fields = ('content', 'user__username', 'user__email', 'article__title')
    readonly_fields = ('created_at', 'updated_at', 'ip_address', 'user_agent', 'referer')
    
    fieldsets = (
        ('Content', {
            'fields': ('article', 'user', 'parent', 'content')
        }),
        ('Status', {
            'fields': ('status', 'moderator', 'moderation_notes', 'moderated_at')
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent', 'referer')
        }),
        ('Engagement', {
            'fields': ('likes', 'dislikes', 'reports')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def content_preview(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_preview.short_description = 'Content'
    
    actions = ['approve_comments', 'reject_comments', 'mark_as_spam']
    
    def approve_comments(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='approved', moderator=request.user, moderated_at=timezone.now())
        self.message_user(request, f'{queryset.count()} comments approved.')
    approve_comments.short_description = 'Approve selected comments'
    
    def reject_comments(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='rejected', moderator=request.user, moderated_at=timezone.now())
        self.message_user(request, f'{queryset.count()} comments rejected.')
    reject_comments.short_description = 'Reject selected comments'
    
    def mark_as_spam(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='spam', moderator=request.user, moderated_at=timezone.now())
        self.message_user(request, f'{queryset.count()} comments marked as spam.')
    mark_as_spam.short_description = 'Mark selected as spam'