from django.contrib import admin
from .models import AnalyticsEvent, AnalyticsPageView, AnalyticsTrafficSource, AnalyticsRealTime

@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'event_name', 'path', 'user', 'device_type', 'created_at')
    list_filter = ('event_type', 'device_type', 'created_at')
    search_fields = ('path', 'url', 'user__username')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

@admin.register(AnalyticsPageView)
class AnalyticsPageViewAdmin(admin.ModelAdmin):
    list_display = ('path', 'views', 'unique_views', 'avg_time_on_page', 'date')
    list_filter = ('date',)
    search_fields = ('path', 'title')
    ordering = ('-date', '-views')

@admin.register(AnalyticsTrafficSource)
class AnalyticsTrafficSourceAdmin(admin.ModelAdmin):
    list_display = ('source_type', 'source_name', 'visits', 'unique_visits', 'conversions', 'date')
    list_filter = ('source_type', 'date')
    search_fields = ('source_name',)
    ordering = ('-date', '-visits')

@admin.register(AnalyticsRealTime)
class AnalyticsRealTimeAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'current_path', 'device_type', 'country', 'last_activity')
    list_filter = ('device_type', 'country')
    search_fields = ('session_id', 'current_path')
    readonly_fields = ('started_at', 'last_activity')