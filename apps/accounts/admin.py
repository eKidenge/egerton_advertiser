from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserActivityLog, UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fieldsets = (
        (None, {'fields': ('date_of_birth', 'gender', 'nationality')}),
        ('Location', {'fields': ('country', 'city', 'address', 'postal_code')}),
        ('Professional', {'fields': ('organization', 'job_title', 'expertise_areas')}),
        ('Preferences', {'fields': ('preferred_categories', 'notification_preferences')}),
        ('Verification', {'fields': ('id_document', 'is_verified', 'verification_date', 'verification_notes')}),
        ('Consent', {'fields': ('newsletter_subscription', 'marketing_consent', 
                               'terms_accepted', 'terms_accepted_date')}),
    )

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'department', 
                   'is_active', 'is_verified', 'date_joined')
    list_filter = ('role', 'department', 'is_active', 'is_verified', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'bio')}),
        (_('Profile'), {'fields': ('profile_picture', 'role', 'department', 'job_title')}),
        (_('Social Media'), {'fields': ('social_links', 'website')}),
        (_('Professional'), {'fields': ('employee_id', 'hire_date')}),
        (_('Preferences'), {'fields': ('email_notifications', 'push_notifications', 'language', 'timezone')}),
        (_('Security'), {'fields': ('is_verified', 'two_factor_enabled', 'failed_login_attempts', 'locked_until')}),
        (_('Statistics'), {'fields': ('articles_written', 'total_views', 'reputation_score')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'updated_at')}),
    )
    
    inlines = [UserProfileInline]
    readonly_fields = ('date_joined', 'updated_at', 'last_login')

class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model_name', 'object_id', 'timestamp', 'ip_address')
    list_filter = ('action', 'model_name', 'timestamp')
    search_fields = ('user__username', 'user__email', 'description')
    readonly_fields = ('user', 'action', 'model_name', 'object_id', 'description', 
                      'ip_address', 'user_agent', 'referer', 'timestamp')
    ordering = ('-timestamp',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(UserActivityLog, UserActivityLogAdmin)