from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from .models import SiteSetting, ThemeSetting
from .forms import SiteSettingForm, ThemeSettingForm, GeneralSettingsForm, EmailSettingsForm, SEOSettingsForm

@login_required
@user_passes_test(lambda u: u.can_manage_settings)
def site_settings(request):
    category = request.GET.get('category', 'general')
    
    settings = SiteSetting.objects.filter(category=category).order_by('key')
    
    context = {
        'settings': settings,
        'category': category,
        'categories': SiteSetting.SETTING_TYPES,
    }
    return render(request, 'settings_manager/site_settings.html', context)

@login_required
@user_passes_test(lambda u: u.can_manage_settings)
def general_settings(request):
    if request.method == 'POST':
        form = GeneralSettingsForm(request.POST, request.FILES)
        if form.is_valid():
            # Save site name
            update_or_create_setting('general', 'site_name', form.cleaned_data['site_name'])
            update_or_create_setting('general', 'site_tagline', form.cleaned_data['site_tagline'])
            update_or_create_setting('general', 'site_description', form.cleaned_data['site_description'])
            
            # Save site logo if provided
            if form.cleaned_data['site_logo']:
                update_or_create_setting('general', 'site_logo', form.cleaned_data['site_logo'])
            
            if form.cleaned_data['site_favicon']:
                update_or_create_setting('general', 'site_favicon', form.cleaned_data['site_favicon'])
            
            update_or_create_setting('general', 'site_timezone', form.cleaned_data['site_timezone'])
            update_or_create_setting('general', 'site_language', form.cleaned_data['site_language'])
            
            messages.success(request, 'General settings updated successfully!')
            return redirect('settings:general')
    else:
        initial = {
            'site_name': get_setting_value('general', 'site_name', 'The Egerton Advertiser'),
            'site_tagline': get_setting_value('general', 'site_tagline', 'Your Local News Source'),
            'site_description': get_setting_value('general', 'site_description', ''),
            'site_timezone': get_setting_value('general', 'site_timezone', 'UTC'),
            'site_language': get_setting_value('general', 'site_language', 'en'),
        }
        form = GeneralSettingsForm(initial=initial)
    
    context = {
        'form': form,
        'active_tab': 'general',
    }
    return render(request, 'settings_manager/general_settings.html', context)

@login_required
@user_passes_test(lambda u: u.can_manage_settings)
def appearance_settings(request):
    user = request.user
    theme, created = ThemeSetting.objects.get_or_create(
        user=user,
        defaults={'is_global': False}
    )
    
    if request.method == 'POST':
        form = ThemeSettingForm(request.POST, instance=theme)
        if form.is_valid():
            form.save()
            messages.success(request, 'Appearance settings updated successfully!')
            return redirect('settings:appearance')
    else:
        form = ThemeSettingForm(instance=theme)
    
    # Get site logo and favicon
    site_logo = get_setting_value('general', 'site_logo', '')
    site_favicon = get_setting_value('general', 'site_favicon', '')
    
    context = {
        'form': form,
        'site_logo': site_logo,
        'site_favicon': site_favicon,
        'active_tab': 'appearance',
    }
    return render(request, 'settings_manager/appearance_settings.html', context)

@login_required
@user_passes_test(lambda u: u.can_manage_settings)
def email_settings(request):
    if request.method == 'POST':
        form = EmailSettingsForm(request.POST)
        if form.is_valid():
            update_or_create_setting('email', 'smtp_host', form.cleaned_data['smtp_host'])
            update_or_create_setting('email', 'smtp_port', str(form.cleaned_data['smtp_port']))
            update_or_create_setting('email', 'smtp_username', form.cleaned_data['smtp_username'])
            
            # Only save password if provided
            if form.cleaned_data['smtp_password']:
                update_or_create_setting('email', 'smtp_password', form.cleaned_data['smtp_password'])
            
            update_or_create_setting('email', 'use_tls', str(form.cleaned_data['use_tls']))
            update_or_create_setting('email', 'from_email', form.cleaned_data['from_email'])
            update_or_create_setting('email', 'from_name', form.cleaned_data['from_name'])
            
            messages.success(request, 'Email settings updated successfully!')
            return redirect('settings:email')
    else:
        initial = {
            'smtp_host': get_setting_value('email', 'smtp_host', ''),
            'smtp_port': int(get_setting_value('email', 'smtp_port', '587')),
            'smtp_username': get_setting_value('email', 'smtp_username', ''),
            'use_tls': get_setting_value('email', 'use_tls', 'True') == 'True',
            'from_email': get_setting_value('email', 'from_email', ''),
            'from_name': get_setting_value('email', 'from_name', 'The Egerton Advertiser'),
        }
        form = EmailSettingsForm(initial=initial)
    
    context = {
        'form': form,
        'active_tab': 'email',
    }
    return render(request, 'settings_manager/email_settings.html', context)

@login_required
@user_passes_test(lambda u: u.can_manage_settings)
def seo_settings(request):
    if request.method == 'POST':
        form = SEOSettingsForm(request.POST)
        if form.is_valid():
            update_or_create_setting('seo', 'meta_title', form.cleaned_data['meta_title'])
            update_or_create_setting('seo', 'meta_description', form.cleaned_data['meta_description'])
            update_or_create_setting('seo', 'meta_keywords', form.cleaned_data['meta_keywords'])
            update_or_create_setting('seo', 'google_analytics_id', form.cleaned_data['google_analytics_id'])
            update_or_create_setting('seo', 'google_verification', form.cleaned_data['google_verification'])
            update_or_create_setting('seo', 'bing_verification', form.cleaned_data['bing_verification'])
            update_or_create_setting('seo', 'robots_txt', form.cleaned_data['robots_txt'])
            update_or_create_setting('seo', 'enable_sitemap', str(form.cleaned_data['enable_sitemap']))
            
            messages.success(request, 'SEO settings updated successfully!')
            return redirect('settings:seo')
    else:
        initial = {
            'meta_title': get_setting_value('seo', 'meta_title', 'The Egerton Advertiser'),
            'meta_description': get_setting_value('seo', 'meta_description', ''),
            'meta_keywords': get_setting_value('seo', 'meta_keywords', ''),
            'google_analytics_id': get_setting_value('seo', 'google_analytics_id', ''),
            'google_verification': get_setting_value('seo', 'google_verification', ''),
            'bing_verification': get_setting_value('seo', 'bing_verification', ''),
            'robots_txt': get_setting_value('seo', 'robots_txt', 'User-agent: *\nAllow: /\n'),
            'enable_sitemap': get_setting_value('seo', 'enable_sitemap', 'True') == 'True',
        }
        form = SEOSettingsForm(initial=initial)
    
    context = {
        'form': form,
        'active_tab': 'seo',
    }
    return render(request, 'settings_manager/seo_settings.html', context)

@login_required
@user_passes_test(lambda u: u.can_manage_settings)
def social_media_settings(request):
    if request.method == 'POST':
        update_or_create_setting('social_media', 'facebook_url', request.POST.get('facebook_url', ''))
        update_or_create_setting('social_media', 'twitter_url', request.POST.get('twitter_url', ''))
        update_or_create_setting('social_media', 'instagram_url', request.POST.get('instagram_url', ''))
        update_or_create_setting('social_media', 'linkedin_url', request.POST.get('linkedin_url', ''))
        update_or_create_setting('social_media', 'youtube_url', request.POST.get('youtube_url', ''))
        update_or_create_setting('social_media', 'pinterest_url', request.POST.get('pinterest_url', ''))
        update_or_create_setting('social_media', 'whatsapp_number', request.POST.get('whatsapp_number', ''))
        update_or_create_setting('social_media', 'telegram_username', request.POST.get('telegram_username', ''))
        
        messages.success(request, 'Social media settings updated successfully!')
        return redirect('settings:social')
    
    context = {
        'facebook_url': get_setting_value('social_media', 'facebook_url', ''),
        'twitter_url': get_setting_value('social_media', 'twitter_url', ''),
        'instagram_url': get_setting_value('social_media', 'instagram_url', ''),
        'linkedin_url': get_setting_value('social_media', 'linkedin_url', ''),
        'youtube_url': get_setting_value('social_media', 'youtube_url', ''),
        'pinterest_url': get_setting_value('social_media', 'pinterest_url', ''),
        'whatsapp_number': get_setting_value('social_media', 'whatsapp_number', ''),
        'telegram_username': get_setting_value('social_media', 'telegram_username', ''),
        'active_tab': 'social_media',
    }
    return render(request, 'settings_manager/social_media_settings.html', context)

@login_required
@user_passes_test(lambda u: u.can_manage_settings)
def advertisement_settings(request):
    if request.method == 'POST':
        update_or_create_setting('advertisement', 'enable_ads', request.POST.get('enable_ads', 'True'))
        update_or_create_setting('advertisement', 'ad_unit_id', request.POST.get('ad_unit_id', ''))
        update_or_create_setting('advertisement', 'ad_blocker_message', request.POST.get('ad_blocker_message', ''))
        update_or_create_setting('advertisement', 'auto_ads', request.POST.get('auto_ads', 'False'))
        
        messages.success(request, 'Advertisement settings updated successfully!')
        return redirect('settings:advertisement')
    
    context = {
        'enable_ads': get_setting_value('advertisement', 'enable_ads', 'True') == 'True',
        'ad_unit_id': get_setting_value('advertisement', 'ad_unit_id', ''),
        'ad_blocker_message': get_setting_value('advertisement', 'ad_blocker_message', ''),
        'auto_ads': get_setting_value('advertisement', 'auto_ads', 'False') == 'True',
        'active_tab': 'advertisement',
    }
    return render(request, 'settings_manager/advertisement_settings.html', context)

# Helper functions
def update_or_create_setting(category, key, value):
    setting, created = SiteSetting.objects.get_or_create(
        category=category,
        key=key,
        defaults={'value': value}
    )
    if not created:
        setting.value = value
        setting.save()

def get_setting_value(category, key, default=''):
    try:
        setting = SiteSetting.objects.get(category=category, key=key)
        return setting.value
    except SiteSetting.DoesNotExist:
        return default

@require_http_methods(["POST"])
@login_required
@user_passes_test(lambda u: u.can_manage_settings)
def update_setting_ajax(request):
    try:
        data = json.loads(request.body)
        category = data.get('category')
        key = data.get('key')
        value = data.get('value')
        
        update_or_create_setting(category, key, value)
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@user_passes_test(lambda u: u.can_manage_settings)
def get_setting_ajax(request):
    try:
        category = request.GET.get('category')
        key = request.GET.get('key')
        
        value = get_setting_value(category, key, '')
        
        return JsonResponse({'success': True, 'value': value})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})