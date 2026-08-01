from django.contrib import admin
from django.utils.html import format_html
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('subject_preview', 'name', 'email', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at', 'updated_at', 'ip_address', 'user_agent', 'referer')
    
    fieldsets = (
        ('Sender Information', {
            'fields': ('name', 'email', 'phone', 'user')
        }),
        ('Message', {
            'fields': ('subject', 'message')
        }),
        ('Status', {
            'fields': ('status', 'priority')
        }),
        ('Response', {
            'fields': ('response', 'responded_by', 'responded_at')
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent', 'referer')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def subject_preview(self, obj):
        return obj.subject[:50] + ('...' if len(obj.subject) > 50 else '')
    subject_preview.short_description = 'Subject'
    
    actions = ['mark_as_read', 'archive_messages', 'mark_as_spam']
    
    def mark_as_read(self, request, queryset):
        queryset.update(status='read')
        self.message_user(request, f'{queryset.count()} messages marked as read.')
    mark_as_read.short_description = 'Mark selected as read'
    
    def archive_messages(self, request, queryset):
        queryset.update(status='archived')
        self.message_user(request, f'{queryset.count()} messages archived.')
    archive_messages.short_description = 'Archive selected messages'
    
    def mark_as_spam(self, request, queryset):
        queryset.update(status='spam')
        self.message_user(request, f'{queryset.count()} messages marked as spam.')
    mark_as_spam.short_description = 'Mark selected as spam'