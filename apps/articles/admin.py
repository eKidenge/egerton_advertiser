from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Article, ArticleVersion, ArticleStatistics, RelatedArticle

class ArticleVersionInline(admin.TabularInline):
    model = ArticleVersion
    extra = 0
    readonly_fields = ('version_number', 'modified_at', 'modified_by')
    fields = ('version_number', 'title', 'modified_by', 'modified_at', 'change_notes')
    ordering = ('-version_number',)
    can_delete = False
    max_num = 0

    def has_add_permission(self, request, obj=None):
        return False


class ArticleStatisticsInline(admin.StackedInline):
    model = ArticleStatistics
    extra = 0
    readonly_fields = ('views_today', 'views_week', 'views_month', 'views_year', 
                      'comments_count', 'last_updated', 'engagement_score')
    fieldsets = (
        ('Views', {'fields': ('views_today', 'views_week', 'views_month', 'views_year')}),
        ('Engagement', {'fields': ('comments_count', 'avg_reading_time', 'bounce_rate')}),
        ('Social Media Shares', {'fields': ('twitter_shares', 'facebook_shares', 'linkedin_shares', 'whatsapp_shares')}),
        ('Performance', {'fields': ('click_through_rate', 'conversion_rate', 'engagement_score')}),
    )
    can_delete = False
    max_num = 1

    def has_add_permission(self, request, obj=None):
        return False


class RelatedArticleInline(admin.TabularInline):
    model = RelatedArticle
    fk_name = 'source'
    extra = 1
    fields = ('target', 'order')
    ordering = ('order',)
    autocomplete_fields = ('target',)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "target":
            # Exclude the source article itself from being selected as target
            if request._obj_ is not None:
                kwargs["queryset"] = Article.objects.exclude(id=request._obj_.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title_preview', 'author', 'category', 'status_display', 
                   'featured_badges', 'published_at', 'views_count', 'action_links')
    list_filter = ('status', 'category', 'is_featured', 'is_breaking', 
                  'is_editor_pick', 'is_exclusive', 'author', 'created_at')
    search_fields = ('title', 'content', 'excerpt', 'slug', 'author__username', 'author__email')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'published_at', 'archived_at', 
                      'views_count', 'shares_count', 'likes_count', 'bookmarks_count', 
                      'reading_time')
    autocomplete_fields = ('author', 'category', 'tags', 'related_articles')
    date_hierarchy = 'published_at'
    list_per_page = 25
    ordering = ('-created_at',)
    
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
            'fields': ('seo_title', 'seo_description', 'seo_keywords', 'canonical_url'),
            'classes': ('collapse',)
        }),
        ('Advanced', {
            'fields': ('custom_css', 'custom_js', 'extra_meta'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('views_count', 'shares_count', 'likes_count', 'bookmarks_count', 
                      'reading_time', 'created_at', 'updated_at', 'archived_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ArticleVersionInline, ArticleStatisticsInline, RelatedArticleInline]
    
    actions = ['make_featured', 'make_breaking', 'make_editor_pick', 
               'publish_selected', 'draft_selected', 'archive_selected', 'delete_selected']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'category')
    
    def title_preview(self, obj):
        return format_html(
            '<a href="{}" target="_blank" style="font-weight:600;color:#1a5c3a;">{}</a>',
            obj.get_absolute_url(),
            obj.title[:60] + ('...' if len(obj.title) > 60 else '')
        )
    title_preview.short_description = 'Title'
    title_preview.admin_order_field = 'title'
    
    def status_display(self, obj):
        status_colors = {
            'draft': '#6c757d',
            'pending': '#ffc107',
            'published': '#28a745',
            'scheduled': '#17a2b8',
            'archived': '#6c757d',
            'trash': '#dc3545',
        }
        color = status_colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'
    
    def featured_badges(self, obj):
        badges = []
        if obj.is_featured:
            badges.append('<span style="background:#c9a84c;color:#0a1628;padding:2px 10px;border-radius:12px;font-size:10px;font-weight:700;margin:2px;">★ Featured</span>')
        if obj.is_breaking:
            badges.append('<span style="background:#dc3545;color:#fff;padding:2px 10px;border-radius:12px;font-size:10px;font-weight:700;margin:2px;">⚡ Breaking</span>')
        if obj.is_editor_pick:
            badges.append('<span style="background:#4a2c6a;color:#fff;padding:2px 10px;border-radius:12px;font-size:10px;font-weight:700;margin:2px;">📌 Editor\'s Pick</span>')
        if obj.is_exclusive:
            badges.append('<span style="background:#1a5c3a;color:#fff;padding:2px 10px;border-radius:12px;font-size:10px;font-weight:700;margin:2px;">🔒 Exclusive</span>')
        return format_html(' '.join(badges))
    featured_badges.short_description = 'Badges'
    
    def action_links(self, obj):
        links = []
        if obj.status != 'published':
            links.append('<a href="#" onclick="return false;" style="color:#28a745;margin-right:8px;">Publish</a>')
        else:
            links.append('<a href="#" onclick="return false;" style="color:#ffc107;margin-right:8px;">Unpublish</a>')
        links.append('<a href="{}" target="_blank" style="color:#1a5c3a;margin-right:8px;">View</a>'.format(obj.get_absolute_url()))
        links.append('<a href="{}" style="color:#007bff;">Edit</a>'.format(reverse('admin:articles_article_change', args=[obj.id])))
        return format_html(' '.join(links))
    action_links.short_description = 'Actions'
    
    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} article(s) marked as featured.')
    make_featured.short_description = 'Mark selected as featured'
    
    def make_breaking(self, request, queryset):
        updated = queryset.update(is_breaking=True)
        self.message_user(request, f'{updated} article(s) marked as breaking news.')
    make_breaking.short_description = 'Mark selected as breaking news'
    
    def make_editor_pick(self, request, queryset):
        updated = queryset.update(is_editor_pick=True)
        self.message_user(request, f'{updated} article(s) marked as editor\'s pick.')
    make_editor_pick.short_description = 'Mark selected as editor\'s pick'
    
    def publish_selected(self, request, queryset):
        updated = queryset.update(status='published', published_at=timezone.now())
        self.message_user(request, f'{updated} article(s) published.')
    publish_selected.short_description = 'Publish selected articles'
    
    def draft_selected(self, request, queryset):
        updated = queryset.update(status='draft', published_at=None)
        self.message_user(request, f'{updated} article(s) moved to draft.')
    draft_selected.short_description = 'Move selected to draft'
    
    def archive_selected(self, request, queryset):
        updated = queryset.update(status='archived', archived_at=timezone.now())
        self.message_user(request, f'{updated} article(s) archived.')
    archive_selected.short_description = 'Archive selected articles'
    
    def delete_selected(self, request, queryset):
        # Soft delete - move to trash instead of hard delete
        updated = queryset.update(status='trash')
        self.message_user(request, f'{updated} article(s) moved to trash.')
    delete_selected.short_description = 'Move selected to trash'
    
    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(ArticleVersion)
class ArticleVersionAdmin(admin.ModelAdmin):
    list_display = ('article_link', 'version_number', 'title_preview', 'modified_by', 'modified_at')
    list_filter = ('modified_at', 'modified_by')
    search_fields = ('article__title', 'change_notes', 'title')
    readonly_fields = ('article', 'version_number', 'title', 'content', 'excerpt', 
                      'slug', 'modified_by', 'modified_at', 'change_notes')
    ordering = ('-modified_at',)
    list_per_page = 20
    
    def article_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:articles_article_change', args=[obj.article.id]),
            obj.article.title[:40] + ('...' if len(obj.article.title) > 40 else '')
        )
    article_link.short_description = 'Article'
    
    def title_preview(self, obj):
        return obj.title[:50] + ('...' if len(obj.title) > 50 else '')
    title_preview.short_description = 'Version Title'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ArticleStatistics)
class ArticleStatisticsAdmin(admin.ModelAdmin):
    list_display = ('article_link', 'views_today', 'views_week', 'views_month', 
                   'comments_count', 'engagement_score', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('article__title',)
    readonly_fields = ('article', 'views_today', 'views_week', 'views_month', 'views_year',
                      'comments_count', 'avg_reading_time', 'bounce_rate',
                      'twitter_shares', 'facebook_shares', 'linkedin_shares', 'whatsapp_shares',
                      'click_through_rate', 'conversion_rate', 'engagement_score', 'last_updated')
    ordering = ('-last_updated',)
    list_per_page = 20
    
    fieldsets = (
        ('Views', {'fields': ('views_today', 'views_week', 'views_month', 'views_year')}),
        ('Engagement', {'fields': ('comments_count', 'avg_reading_time', 'bounce_rate')}),
        ('Social Media Shares', {'fields': ('twitter_shares', 'facebook_shares', 'linkedin_shares', 'whatsapp_shares')}),
        ('Performance', {'fields': ('click_through_rate', 'conversion_rate', 'engagement_score')}),
    )
    
    def article_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:articles_article_change', args=[obj.article.id]),
            obj.article.title[:40] + ('...' if len(obj.article.title) > 40 else '')
        )
    article_link.short_description = 'Article'
    
    def has_add_permission(self, request):
        return False


@admin.register(RelatedArticle)
class RelatedArticleAdmin(admin.ModelAdmin):
    list_display = ('source_link', 'target_link', 'order', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('source__title', 'target__title')
    ordering = ('-created_at',)
    list_per_page = 20
    
    def source_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:articles_article_change', args=[obj.source.id]),
            obj.source.title[:30] + ('...' if len(obj.source.title) > 30 else '')
        )
    source_link.short_description = 'Source Article'
    
    def target_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:articles_article_change', args=[obj.target.id]),
            obj.target.title[:30] + ('...' if len(obj.target.title) > 30 else '')
        )
    target_link.short_description = 'Related Article'