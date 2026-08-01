from django.contrib import admin
from .models import SearchQuery, SearchResultClick

@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ('query', 'user', 'results_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('query', 'user__username')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

@admin.register(SearchResultClick)
class SearchResultClickAdmin(admin.ModelAdmin):
    list_display = ('search_query', 'result_type', 'result_title', 'clicked_at')
    list_filter = ('result_type', 'clicked_at')
    search_fields = ('result_title', 'search_query__query')
    readonly_fields = ('clicked_at',)
    ordering = ('-clicked_at',)