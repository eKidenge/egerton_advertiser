from django.contrib import admin
from django.utils.html import format_html
from .models import Advertisement, AdvertisementView, AdvertisementClick

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title_preview', 'advertiser', 'position', 'size', 
                   'status', 'start_date', 'end_date', 'views_count', 'clicks_count')
    list_filter = ('status', 'position', 'size', 'start_date', 'end_date')
    search_fields = ('title', 'company_name', 'advertiser__username', 'advertiser__email')
    readonly_fields = ('views_count', 'clicks_count', 'unique_views', 'unique_clicks', 
                      'conversion_count', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'advertiser', 'company_name', 
                      'contact_email', 'contact_phone')
        }),
        ('Ad Content', {
            'fields': ('image', 'image_alt', 'video_url', 'link_url', 'link_target')
        }),
        ('Placement', {
            'fields': ('position', 'size')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date', 'status')
        }),
        ('Budget & Pricing', {
            'fields': ('budget', 'cost_per_click', 'cost_per_impression')
        }),
        ('Targeting', {
            'fields': ('targeted_categories', 'targeted_articles', 
                      'target_countries', 'target_cities')
        }),
        ('Limits', {
            'fields': ('max_clicks', 'max_impressions', 'daily_limit', 'priority')
        }),
        ('Performance', {
            'fields': ('views_count', 'clicks_count', 'unique_views', 
                      'unique_clicks', 'conversion_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def title_preview(self, obj):
        return obj.title[:50] + ('...' if len(obj.title) > 50 else '')
    title_preview.short_description = 'Title'
    
    actions = ['activate_ads', 'pause_ads', 'expire_ads']
    
    def activate_ads(self, request, queryset):
        queryset.update(status='active')
        self.message_user(request, f'{queryset.count()} advertisements activated.')
    activate_ads.short_description = 'Activate selected ads'
    
    def pause_ads(self, request, queryset):
        queryset.update(status='paused')
        self.message_user(request, f'{queryset.count()} advertisements paused.')
    pause_ads.short_description = 'Pause selected ads'
    
    def expire_ads(self, request, queryset):
        queryset.update(status='expired')
        self.message_user(request, f'{queryset.count()} advertisements expired.')
    expire_ads.short_description = 'Expire selected ads'

@admin.register(AdvertisementView)
class AdvertisementViewAdmin(admin.ModelAdmin):
    list_display = ('ad', 'user', 'viewed_at', 'ip_address')
    list_filter = ('viewed_at',)
    search_fields = ('ad__title', 'user__username', 'ip_address')
    readonly_fields = ('ad', 'user', 'viewed_at', 'ip_address', 'user_agent', 'referer', 'session_id')
    ordering = ('-viewed_at',)

@admin.register(AdvertisementClick)
class AdvertisementClickAdmin(admin.ModelAdmin):
    list_display = ('ad', 'user', 'clicked_at', 'ip_address')
    list_filter = ('clicked_at',)
    search_fields = ('ad__title', 'user__username', 'ip_address')
    readonly_fields = ('ad', 'user', 'clicked_at', 'ip_address', 'user_agent', 'referer', 'session_id')
    ordering = ('-clicked_at',)