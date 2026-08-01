from django.contrib import admin
from .models import DashboardWidget, DashboardPreference, DashboardMetric, QuickAction, DashboardActivityFeed

@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'widget_type', 'column', 'position', 'is_active')
    list_filter = ('widget_type', 'is_active', 'column')
    search_fields = ('title', 'user__username')
    ordering = ('user', 'column', 'position')

@admin.register(DashboardPreference)
class DashboardPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'default_view', 'refresh_interval', 'updated_at')
    list_filter = ('theme', 'default_view')
    search_fields = ('user__username',)

@admin.register(DashboardMetric)
class DashboardMetricAdmin(admin.ModelAdmin):
    list_display = ('user', 'metric_type', 'value', 'change_percentage', 'date')
    list_filter = ('metric_type', 'date')
    search_fields = ('user__username',)

@admin.register(QuickAction)
class QuickActionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'user__username')
    ordering = ('user', 'order')

@admin.register(DashboardActivityFeed)
class DashboardActivityFeedAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'message', 'is_read', 'created_at')
    list_filter = ('activity_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'message')
    ordering = ('-created_at',)