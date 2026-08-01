from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
import json
from .models import Advertisement, AdvertisementView, AdvertisementClick
from .forms import AdvertisementForm, AdvertisementFilterForm
from apps.accounts.models import UserActivityLog

@login_required
def advertisement_list(request):
    user = request.user
    
    if user.can_manage_users:
        ads = Advertisement.objects.all().select_related('advertiser')
    else:
        ads = Advertisement.objects.filter(advertiser=user).select_related('advertiser')
    
    # Filtering
    form = AdvertisementFilterForm(request.GET)
    if form.is_valid():
        if form.cleaned_data.get('status'):
            ads = ads.filter(status=form.cleaned_data['status'])
        if form.cleaned_data.get('position'):
            ads = ads.filter(position=form.cleaned_data['position'])
        if form.cleaned_data.get('advertiser') and user.can_manage_users:
            ads = ads.filter(advertiser=form.cleaned_data['advertiser'])
        if form.cleaned_data.get('date_from'):
            ads = ads.filter(created_at__gte=form.cleaned_data['date_from'])
        if form.cleaned_data.get('date_to'):
            ads = ads.filter(created_at__lte=form.cleaned_data['date_to'])
    
    ads = ads.order_by('-created_at')
    
    paginator = Paginator(ads, 20)
    page = request.GET.get('page')
    try:
        ads = paginator.page(page)
    except PageNotAnInteger:
        ads = paginator.page(1)
    except EmptyPage:
        ads = paginator.page(paginator.num_pages)
    
    context = {
        'ads': ads,
        'form': form,
    }
    return render(request, 'advertisements/advertisement_list.html', context)

@login_required
def advertisement_detail(request, ad_id):
    ad = get_object_or_404(Advertisement, id=ad_id)
    
    if not request.user.can_manage_users and ad.advertiser != request.user:
        messages.error(request, 'You do not have permission to view this ad.')
        return redirect('advertisements:list')
    
    # Get statistics
    total_views = ad.views_count
    total_clicks = ad.clicks_count
    ctr = (total_clicks / total_views * 100) if total_views > 0 else 0
    
    # Daily views for chart
    daily_views = AdvertisementView.objects.filter(
        ad=ad,
        viewed_at__gte=timezone.now() - timezone.timedelta(days=30)
    ).extra(
        {'day': "date(viewed_at)"}
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    # Daily clicks for chart
    daily_clicks = AdvertisementClick.objects.filter(
        ad=ad,
        clicked_at__gte=timezone.now() - timezone.timedelta(days=30)
    ).extra(
        {'day': "date(clicked_at)"}
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    context = {
        'ad': ad,
        'total_views': total_views,
        'total_clicks': total_clicks,
        'ctr': ctr,
        'daily_views': daily_views,
        'daily_clicks': daily_clicks,
    }
    return render(request, 'advertisements/advertisement_detail.html', context)

@login_required
def advertisement_create(request):
    if request.method == 'POST':
        form = AdvertisementForm(request.POST, request.FILES)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.advertiser = request.user
            ad.save()
            form.save_m2m()
            
            UserActivityLog.objects.create(
                user=request.user,
                action='create',
                model_name='Advertisement',
                object_id=ad.id,
                description=f'Created advertisement: {ad.title}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'Advertisement "{ad.title}" created successfully!')
            return redirect('advertisements:detail', ad_id=ad.id)
    else:
        form = AdvertisementForm()
    
    return render(request, 'advertisements/advertisement_create.html', {'form': form})

@login_required
def advertisement_edit(request, ad_id):
    ad = get_object_or_404(Advertisement, id=ad_id)
    
    if not request.user.can_manage_users and ad.advertiser != request.user:
        messages.error(request, 'You do not have permission to edit this ad.')
        return redirect('advertisements:list')
    
    if request.method == 'POST':
        form = AdvertisementForm(request.POST, request.FILES, instance=ad)
        if form.is_valid():
            ad = form.save()
            
            UserActivityLog.objects.create(
                user=request.user,
                action='update',
                model_name='Advertisement',
                object_id=ad.id,
                description=f'Updated advertisement: {ad.title}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'Advertisement "{ad.title}" updated successfully!')
            return redirect('advertisements:detail', ad_id=ad.id)
    else:
        form = AdvertisementForm(instance=ad)
    
    return render(request, 'advertisements/advertisement_edit.html', {'form': form, 'ad': ad})

@login_required
def advertisement_delete(request, ad_id):
    ad = get_object_or_404(Advertisement, id=ad_id)
    
    if not request.user.can_manage_users and ad.advertiser != request.user:
        messages.error(request, 'You do not have permission to delete this ad.')
        return redirect('advertisements:list')
    
    if request.method == 'POST':
        title = ad.title
        ad.delete()
        
        UserActivityLog.objects.create(
            user=request.user,
            action='delete',
            model_name='Advertisement',
            object_id=ad_id,
            description=f'Deleted advertisement: {title}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, f'Advertisement "{title}" deleted successfully!')
        return redirect('advertisements:list')
    
    return render(request, 'advertisements/advertisement_delete.html', {'ad': ad})

@login_required
@user_passes_test(lambda u: u.can_manage_users)
def advertisement_positions(request):
    positions = []
    for pos_code, pos_name in Advertisement.POSITION_CHOICES:
        ad_count = Advertisement.objects.filter(position=pos_code).count()
        active_count = Advertisement.objects.filter(position=pos_code, status='active').count()
        positions.append({
            'code': pos_code,
            'name': pos_name,
            'ad_count': ad_count,
            'active_count': active_count,
        })
    
    return render(request, 'advertisements/advertisement_positions.html', {'positions': positions})

@login_required
def advertisement_statistics(request):
    user = request.user
    
    if user.can_manage_users:
        ads = Advertisement.objects.all()
    else:
        ads = Advertisement.objects.filter(advertiser=user)
    
    # Overall statistics
    total_ads = ads.count()
    active_ads = ads.filter(status='active').count()
    total_views = ads.aggregate(Sum('views_count'))['views_count__sum'] or 0
    total_clicks = ads.aggregate(Sum('clicks_count'))['clicks_count__sum'] or 0
    ctr = (total_clicks / total_views * 100) if total_views > 0 else 0
    
    # By position
    position_stats = []
    for pos_code, pos_name in Advertisement.POSITION_CHOICES:
        pos_ads = ads.filter(position=pos_code)
        count = pos_ads.count()
        if count > 0:
            position_stats.append({
                'position': pos_name,
                'count': count,
                'views': pos_ads.aggregate(Sum('views_count'))['views_count__sum'] or 0,
                'clicks': pos_ads.aggregate(Sum('clicks_count'))['clicks_count__sum'] or 0,
            })
    
    context = {
        'total_ads': total_ads,
        'active_ads': active_ads,
        'total_views': total_views,
        'total_clicks': total_clicks,
        'ctr': ctr,
        'position_stats': position_stats,
    }
    return render(request, 'advertisements/advertisement_statistics.html', context)

@require_http_methods(["GET"])
def get_ad_by_position(request, position):
    """API endpoint to get an ad for a specific position"""
    ads = Advertisement.objects.filter(
        position=position,
        status='active',
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    ).order_by('-priority')
    
    # Check daily and total limits
    for ad in ads:
        if ad.can_show():
            # Increment view
            ad.increment_view(user=request.user if request.user.is_authenticated else None, request=request)
            
            return JsonResponse({
                'id': ad.id,
                'title': ad.title,
                'image_url': ad.image.url if ad.image else '',
                'link_url': ad.link_url,
                'link_target': ad.link_target,
                'alt_text': ad.image_alt,
            })
    
    return JsonResponse({'ad': None})