from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import User, UserProfile, UserActivityLog


class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'  # Required because UserProfile has multiple ForeignKey to User
    extra = 0
    max_num = 1
    
    fieldsets = (
        (None, {
            'fields': (
                'user',  # Read-only display
            )
        }),
        ('Personal Information', {
            'fields': (
                'date_of_birth', 'gender', 'nationality',
                'country', 'city', 'address', 'postal_code'
            ),
            'classes': ('wide',)
        }),
        ('Professional Information', {
            'fields': (
                'organization', 'job_title', 'expertise_areas'
            ),
            'classes': ('wide',)
        }),
        ('Preferences', {
            'fields': (
                'preferred_categories', 'notification_preferences'
            ),
            'classes': ('wide',)
        }),
        ('Verification Status', {
            'fields': (
                'is_verified', 'verification_date', 'verification_notes', 'verified_by'
            ),
            'classes': ('wide',)
        }),
        ('Additional Settings', {
            'fields': (
                'newsletter_subscription', 'marketing_consent',
                'terms_accepted', 'terms_accepted_date'
            ),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('wide',)
        }),
    )
    
    # Read-only fields
    readonly_fields = ('user', 'created_at', 'updated_at', 'verification_date', 'verified_by')
    
    def get_extra(self, request, obj=None, **kwargs):
        """Only show the inline if the user exists"""
        return 1 if obj else 0


class CustomUserAdmin(UserAdmin):
    """Custom admin for User model with role-based views"""
    
    # List display fields
    list_display = (
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'role_colored', 
        'is_active', 
        'is_verified', 
        'date_joined'
    )
    
    # List filters
    list_filter = (
        'role', 
        'is_active', 
        'is_verified', 
        'is_staff', 
        'is_superuser', 
        'department',
        'date_joined'
    )
    
    # Search fields
    search_fields = (
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'phone_number',
        'employee_id'
    )
    
    # Default ordering
    ordering = ('-date_joined',)
    
    # Actions
    actions = ['activate_users', 'deactivate_users', 'verify_users', 'unverify_users']
    
    # Fieldsets for viewing/editing user
    fieldsets = (
        (None, {
            'fields': ('username', 'password'),
            'classes': ('wide',)
        }),
        (_('Personal Information'), {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'bio', 'profile_picture'),
            'classes': ('wide',)
        }),
        (_('Professional Information'), {
            'fields': ('role', 'department', 'employee_id', 'hire_date', 'job_title'),
            'classes': ('wide',)
        }),
        (_('Social & Web'), {
            'fields': ('website', 'social_links'),
            'classes': ('wide',)
        }),
        (_('Preferences'), {
            'fields': ('email_notifications', 'push_notifications', 'language', 'timezone'),
            'classes': ('wide',)
        }),
        (_('Security'), {
            'fields': ('failed_login_attempts', 'locked_until', 'two_factor_enabled'),
            'classes': ('wide',)
        }),
        (_('Meta Information'), {
            'fields': ('articles_written', 'total_views', 'reputation_score'),
            'classes': ('wide',)
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('wide',)
        }),
        (_('Important Dates'), {
            'fields': ('last_login', 'date_joined', 'updated_at'),
            'classes': ('wide',)
        }),
    )
    
    # Fieldsets for adding new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )
    
    # Inlines
    inlines = [UserProfileInline]
    
    # Read-only fields
    readonly_fields = (
        'last_login', 
        'date_joined', 
        'updated_at', 
        'failed_login_attempts', 
        'locked_until'
    )
    
    def get_inline_instances(self, request, obj=None):
        """Only show the inline if the user exists"""
        if not obj:
            return []
        return super().get_inline_instances(request, obj)
    
    def role_colored(self, obj):
        """Display role with color coding"""
        colors = {
            'super_admin': '#dc3545',  # Red
            'admin': '#007bff',        # Blue
            'editor': '#28a745',       # Green
            'journalist': '#17a2b8',   # Teal
            'subscriber': '#6c757d',   # Gray
            'advertiser': '#ffc107',   # Yellow
        }
        color = colors.get(obj.role, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_role_display()
        )
    role_colored.short_description = 'Role'
    
    def activate_users(self, request, queryset):
        """Activate selected users"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} user(s) activated successfully.')
    activate_users.short_description = 'Activate selected users'
    
    def deactivate_users(self, request, queryset):
        """Deactivate selected users"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} user(s) deactivated successfully.')
    deactivate_users.short_description = 'Deactivate selected users'
    
    def verify_users(self, request, queryset):
        """Verify selected users"""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} user(s) verified successfully.')
    verify_users.short_description = 'Verify selected users'
    
    def unverify_users(self, request, queryset):
        """Unverify selected users"""
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} user(s) unverified successfully.')
    unverify_users.short_description = 'Unverify selected users'
    
    def get_queryset(self, request):
        """Optimize queries with select_related"""
        return super().get_queryset(request).select_related('profile')
    
    def save_model(self, request, obj, form, change):
        """Log user creation/update in admin"""
        if not change:
            # New user created
            UserActivityLog.objects.create(
                user=request.user,
                action='create',
                model_name='User',
                object_id=obj.id,
                description=f'Admin {request.user.username} created user {obj.username}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
        else:
            # User updated
            UserActivityLog.objects.create(
                user=request.user,
                action='update',
                model_name='User',
                object_id=obj.id,
                description=f'Admin {request.user.username} updated user {obj.username}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
        super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj):
        """Log user deletion in admin"""
        UserActivityLog.objects.create(
            user=request.user,
            action='delete',
            model_name='User',
            object_id=obj.id,
            description=f'Admin {request.user.username} deleted user {obj.username}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        super().delete_model(request, obj)


class UserActivityLogAdmin(admin.ModelAdmin):
    """Admin for UserActivityLog model"""
    
    list_display = (
        'user', 
        'action_colored', 
        'model_name', 
        'object_id', 
        'ip_address', 
        'timestamp'
    )
    
    list_filter = (
        'action', 
        'model_name', 
        'timestamp',
        'user'
    )
    
    search_fields = (
        'user__username', 
        'user__email', 
        'description',
        'ip_address',
        'model_name'
    )
    
    readonly_fields = (
        'user', 
        'action', 
        'model_name', 
        'object_id', 
        'description',
        'ip_address', 
        'user_agent', 
        'referer', 
        'timestamp'
    )
    
    ordering = ('-timestamp',)
    
    # Disable add/delete/edit permissions
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def action_colored(self, obj):
        """Display action with color coding"""
        colors = {
            'login': '#28a745',      # Green
            'logout': '#dc3545',      # Red
            'create': '#007bff',      # Blue
            'update': '#ffc107',      # Yellow
            'delete': '#dc3545',      # Red
            'publish': '#17a2b8',     # Teal
            'view': '#6c757d',        # Gray
            'comment': '#fd7e14',     # Orange
        }
        color = colors.get(obj.action, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_action_display()
        )
    action_colored.short_description = 'Action'


class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile model"""
    
    list_display = (
        'user', 
        'gender', 
        'country', 
        'organization', 
        'is_verified', 
        'newsletter_subscription'
    )
    
    list_filter = (
        'gender', 
        'country', 
        'is_verified', 
        'newsletter_subscription',
        'marketing_consent'
    )
    
    search_fields = (
        'user__username', 
        'user__email', 
        'country', 
        'city',
        'organization',
        'job_title'
    )
    
    readonly_fields = ('created_at', 'updated_at', 'verification_date')
    
    fieldsets = (
        (None, {
            'fields': ('user',)
        }),
        ('Personal Information', {
            'fields': ('date_of_birth', 'gender', 'nationality', 'country', 'city', 'address', 'postal_code')
        }),
        ('Professional', {
            'fields': ('organization', 'job_title', 'expertise_areas')
        }),
        ('Preferences', {
            'fields': ('preferred_categories', 'notification_preferences')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verification_date', 'verification_notes', 'verified_by')
        }),
        ('Additional', {
            'fields': ('newsletter_subscription', 'marketing_consent', 'terms_accepted', 'terms_accepted_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def has_add_permission(self, request):
        """Prevent adding profiles directly in admin"""
        return False


# Register models with the admin site
admin.site.register(User, CustomUserAdmin)
admin.site.register(UserActivityLog, UserActivityLogAdmin)
admin.site.register(UserProfile, UserProfileAdmin)