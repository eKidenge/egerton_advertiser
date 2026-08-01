from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Article, ArticleVersion, ArticleStatistics, RelatedArticle

class ArticleVersionInline(admin.TabularInline):
    model = ArticleVersion
    extra = 0
    readonly_fields = ('version_number', 'modified_at', 'modified_by')
    fields = ('version_number', 'title', 'modified_by', 'modified_at', 'change_notes')
    ordering = ('-version_number',)

class ArticleStatisticsInline(admin.StackedInline):
    model = ArticleStatistics
    extra = 0
    readonly_fields = ('views_today', 'views_week', 'views_month', 'views_year', 
                      'comments_count', 'last_updated')
    fieldsets = (
        ('Views', {'fields': ('views_today', 'views_week', 'views_month', 'views_year')}),
        ('Engagement', {'fields': ('comments_count', 'avg_reading_time', 'bounce_rate')}),
        ('Social', {'fields': ('twitter_shares', 'facebook_shares', 'linkedin_shares', 'whatsapp_shares')}),
        ('Performance', {'fields': ('click_through_rate', 'conversion_rate', 'engagement_score')}),
    )

class RelatedArticleInline(admin.TabularInline):
    model = RelatedArticle
    fk_name = 'source'
    extra = 0
    fields = ('target', 'order')
    ordering = ('order',)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title_preview', 'author', 'category', 'status', 
                   'is_featured', 'is_breaking', 'published_at', 'views_count')
    list_filter = ('status', 'category', 'is_featured', 'is_breaking', 
                  'is_editor_pick', 'is_exclusive', 'created_at')
    search_fields = ('title', 'content', 'excerpt', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'published_at', 'archived_at', 
                      'views_count', 'shares_count', 'likes_count', 'bookmarks_count')
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'excerpt', 'content', 'featured_image', 
                      'featured_image_alt', 'featured_image_caption')
        }),
        ('Organization', {
            'fields': ('author', 'category', 'tags')
        }),
        ('Status & Publishing', {
            'fields': ('status', 'publish_option', 'scheduled_for', 'published_at')
        }),
        ('Featured Settings', {
            'fields': ('is_featured', 'featured_order', 'is_breaking', 
                      'is_exclusive', 'is_editor_pick')
        }),
        ('SEO', {
            'fields': ('seo_title', 'seo_description', 'seo_keywords', 'canonical_url')
        }),
        ('Advanced', {
            'fields': ('custom_css', 'custom_js', 'extra_meta')
        }),
        ('Metadata', {
            'fields': ('views_count', 'shares_count', 'likes_count', 'bookmarks_count', 
                      'reading_time', 'created_at', 'updated_at', 'archived_at')
        }),
    )
    
    inlines = [ArticleVersionInline, ArticleStatisticsInline, RelatedArticleInline]
    
    actions = ['make_featured', 'make_breaking', 'publish_selected', 'draft_selected']
    
    def title_preview(self, obj):
        return format_html(
            '<a href="{}" target="_blank">{}</a>',
            obj.get_absolute_url(),
            obj.title[:50] + ('...' if len(obj.title) > 50 else '')
        )
    title_preview.short_description = 'Title'
    
    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f'{queryset.count()} articles marked as featured.')
    make_featured.short_description = 'Mark selected as featured'
    
    def make_breaking(self, request, queryset):
        queryset.update(is_breaking=True)
        self.message_user(request, f'{queryset.count()} articles marked as breaking news.')
    make_breaking.short_description = 'Mark selected as breaking news'
    
    def publish_selected(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='published', published_at=timezone.now())
        self.message_user(request, f'{queryset.count()} articles published.')
    publish_selected.short_description = 'Publish selected articles'
    
    def draft_selected(self, request, queryset):
        queryset.update(status='draft', published_at=None)
        self.message_user(request, f'{queryset.count()} articles moved to draft.')
    draft_selected.short_description = 'Move selected to draft'

@admin.register(ArticleVersion)
class ArticleVersionAdmin(admin.ModelAdmin):
    list_display = ('article', 'version_number', 'modified_by', 'modified_at')
    list_filter = ('modified_at',)
    search_fields = ('article__title', 'change_notes')
    readonly_fields = ('article', 'version_number', 'title', 'content', 'excerpt', 
                      'slug', 'modified_by', 'modified_at', 'change_notes')
    ordering = ('-modified_at',)