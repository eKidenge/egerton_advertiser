from django.contrib import admin
from django.utils.html import format_html
from .models import Subscriber, Newsletter, NewsletterTracking

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'status', 'frequency', 'opens', 'clicks', 'created_at')
    list_filter = ('status', 'frequency', 'created_at')
    search_fields = ('email', 'name')
    readonly_fields = ('opens', 'clicks', 'unsubscribes', 'confirmed_at', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('email', 'name')
        }),
        ('Status', {
            'fields': ('status', 'confirmed_at', 'confirmed_ip')
        }),
        ('Preferences', {
            'fields': ('categories', 'tags', 'frequency')
        }),
        ('Tracking', {
            'fields': ('opens', 'clicks', 'unsubscribes', 'last_sent', 'last_opened')
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent', 'referer', 'source', 'source_url')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['activate_subscribers', 'unsubscribe_subscribers']
    
    def activate_subscribers(self, request, queryset):
        queryset.update(status='active')
        self.message_user(request, f'{queryset.count()} subscribers activated.')
    activate_subscribers.short_description = 'Activate selected subscribers'
    
    def unsubscribe_subscribers(self, request, queryset):
        queryset.update(status='unsubscribed')
        self.message_user(request, f'{queryset.count()} subscribers unsubscribed.')
    unsubscribe_subscribers.short_description = 'Unsubscribe selected subscribers'

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('subject_preview', 'status', 'template', 'subscribers_count', 
                   'opens_count', 'clicks_count', 'created_at')
    list_filter = ('status', 'template', 'created_at')
    search_fields = ('subject', 'content')
    readonly_fields = ('subscribers_count', 'opens_count', 'clicks_count', 
                      'unsubscribe_count', 'bounce_count', 'spam_reports',
                      'sent_at', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('subject', 'preview_text')
        }),
        ('Content', {
            'fields': ('content', 'plain_text')
        }),
        ('Template', {
            'fields': ('template', 'template_custom')
        }),
        ('Articles', {
            'fields': ('articles',)
        }),
        ('Scheduling', {
            'fields': ('status', 'scheduled_for', 'sent_at')
        }),
        ('Audience', {
            'fields': ('target_categories',)
        }),
        ('Sender', {
            'fields': ('from_email', 'from_name', 'reply_to')
        }),
        ('Tracking', {
            'fields': ('subscribers_count', 'opens_count', 'clicks_count', 
                      'unsubscribe_count', 'bounce_count', 'spam_reports')
        }),
        ('Metadata', {
            'fields': ('created_by', 'sent_by', 'created_at', 'updated_at')
        }),
    )
    
    def subject_preview(self, obj):
        return obj.subject[:50] + ('...' if len(obj.subject) > 50 else '')
    subject_preview.short_description = 'Subject'

@admin.register(NewsletterTracking)
class NewsletterTrackingAdmin(admin.ModelAdmin):
    list_display = ('newsletter', 'subscriber', 'action', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('newsletter__subject', 'subscriber__email')
    readonly_fields = ('newsletter', 'subscriber', 'action', 'ip_address', 
                      'user_agent', 'referer', 'link', 'created_at')
    ordering = ('-created_at',)