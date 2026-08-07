from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from .models import Subscriber, Newsletter, NewsletterTracking
from .forms import SubscriberForm, NewsletterForm, NewsletterFilterForm
from apps.accounts.models import UserActivityLog


# ============================================
# PUBLIC SUBSCRIBE VIEWS
# ============================================

# apps/newsletter/views.py

def subscribe(request):
    """Subscribe to newsletter"""
    from apps.categories.models import Category
    from django.contrib import messages
    
    categories = Category.objects.filter(is_active=True)
    
    if request.method == 'POST':
        email = request.POST.get('email')
        name = request.POST.get('name')
        selected_categories = request.POST.getlist('categories')
        
        # Validate email
        if not email:
            messages.error(request, '⚠️ Email address is required.')
            return render(request, 'newsletter/subscribe.html', {
                'categories': categories,
                'email': email,
                'name': name,
            })
        
        # Check if already exists
        existing = Subscriber.objects.filter(email=email).first()
        if existing:
            if existing.status == 'unsubscribed':
                existing.status = 'active'
                if name:
                    existing.name = name
                existing.save()
                messages.success(request, '✅ You have been resubscribed successfully!')
            else:
                messages.info(request, 'ℹ️ You are already subscribed.')
            return redirect('home')
        
        # Create new subscriber
        subscriber = Subscriber.objects.create(
            email=email,
            name=name or '',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            referer=request.META.get('HTTP_REFERER', ''),
            status='active'
        )
        
        # Save categories
        if selected_categories:
            category_ids = []
            for cat in selected_categories:
                try:
                    category_ids.append(int(cat))
                except (ValueError, TypeError):
                    continue
            if category_ids:
                categories_to_add = Category.objects.filter(id__in=category_ids)
                subscriber.categories.add(*categories_to_add)
        
        # ✅ Only log if user is authenticated
        if request.user.is_authenticated:
            UserActivityLog.objects.create(
                user=request.user,
                action='subscribe',
                model_name='Subscriber',
                object_id=subscriber.id,
                description=f'New subscriber: {subscriber.email}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
        
        messages.success(request, '✅ Thank you for subscribing! You will receive our latest news.')
        return redirect('home')
    
    return render(request, 'newsletter/subscribe.html', {'categories': categories})


def unsubscribe(request, email=None):
    """Unsubscribe from newsletter"""
    if request.method == 'POST':
        email = request.POST.get('email')
    
    if email:
        subscriber = Subscriber.objects.filter(email=email).first()
        if subscriber:
            subscriber.unsubscribe()
            
            # Record unsubscribe
            NewsletterTracking.objects.create(
                newsletter=None,
                subscriber=subscriber,
                action='unsubscribe',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                referer=request.META.get('HTTP_REFERER', '')
            )
            
            messages.success(request, 'You have been unsubscribed successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Subscriber not found.')
    
    return render(request, 'newsletter/unsubscribe.html')


# ============================================
# TRACKING VIEWS
# ============================================

@require_http_methods(["GET"])
def track_open(request, newsletter_id, subscriber_id):
    """Track email opens via a tracking pixel"""
    try:
        newsletter = Newsletter.objects.get(id=newsletter_id)
        subscriber = Subscriber.objects.get(id=subscriber_id)
        
        # Record open
        NewsletterTracking.objects.create(
            newsletter=newsletter,
            subscriber=subscriber,
            action='open',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            referer=request.META.get('HTTP_REFERER', '')
        )
        
        # Update subscriber stats
        subscriber.record_open()
        
        # Update newsletter stats
        newsletter.opens_count += 1
        newsletter.save(update_fields=['opens_count'])
        
        # Return a 1x1 transparent pixel
        response = HttpResponse(content_type='image/gif')
        response.write(b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b')
        return response
    except Exception as e:
        print(f"Error tracking open: {e}")
        return HttpResponse(status=404)


@require_http_methods(["GET"])
def track_click(request, newsletter_id, subscriber_id):
    """Track email clicks"""
    try:
        newsletter = Newsletter.objects.get(id=newsletter_id)
        subscriber = Subscriber.objects.get(id=subscriber_id)
        link = request.GET.get('link', '')
        
        # Record click
        NewsletterTracking.objects.create(
            newsletter=newsletter,
            subscriber=subscriber,
            action='click',
            link=link,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            referer=request.META.get('HTTP_REFERER', '')
        )
        
        # Update subscriber stats
        subscriber.record_click()
        
        # Update newsletter stats
        newsletter.clicks_count += 1
        newsletter.save(update_fields=['clicks_count'])
        
        # Redirect to the link
        return redirect(link)
    except Exception as e:
        print(f"Error tracking click: {e}")
        return redirect('home')


# ============================================
# ADMIN - SUBSCRIBER MANAGEMENT
# ============================================

@login_required
@user_passes_test(lambda u: u.can_manage_users)
def subscriber_list(request):
    """List all subscribers"""
    subscribers = Subscriber.objects.all().order_by('-created_at')
    
    # Filtering
    status = request.GET.get('status')
    if status:
        subscribers = subscribers.filter(status=status)
    
    search = request.GET.get('search')
    if search:
        subscribers = subscribers.filter(
            Q(email__icontains=search) |
            Q(name__icontains=search)
        )
    
    paginator = Paginator(subscribers, 50)
    page = request.GET.get('page')
    try:
        subscribers = paginator.page(page)
    except PageNotAnInteger:
        subscribers = paginator.page(1)
    except EmptyPage:
        subscribers = paginator.page(paginator.num_pages)
    
    # Statistics
    stats = {
        'total': Subscriber.objects.count(),
        'active': Subscriber.objects.filter(status='active').count(),
        'inactive': Subscriber.objects.filter(status='inactive').count(),
        'unsubscribed': Subscriber.objects.filter(status='unsubscribed').count(),
    }
    
    context = {
        'subscribers': subscribers,
        'stats': stats,
        'status_filter': status,
        'search': search,
    }
    return render(request, 'newsletter/subscriber_list.html', context)


@login_required
@user_passes_test(lambda u: u.can_manage_users)
def subscriber_detail(request, subscriber_id):
    """View subscriber details"""
    subscriber = get_object_or_404(Subscriber, id=subscriber_id)
    
    # Get tracking data
    tracking = NewsletterTracking.objects.filter(subscriber=subscriber).order_by('-created_at')
    
    context = {
        'subscriber': subscriber,
        'tracking': tracking,
    }
    return render(request, 'newsletter/subscriber_detail.html', context)


# ============================================
# ADMIN - NEWSLETTER MANAGEMENT
# ============================================

@login_required
@user_passes_test(lambda u: u.can_manage_users)
def newsletter_list(request):
    """List all newsletters"""
    newsletters = Newsletter.objects.all().order_by('-created_at')
    
    # Filtering
    form = NewsletterFilterForm(request.GET)
    if form.is_valid():
        if form.cleaned_data.get('status'):
            newsletters = newsletters.filter(status=form.cleaned_data['status'])
        if form.cleaned_data.get('date_from'):
            newsletters = newsletters.filter(created_at__gte=form.cleaned_data['date_from'])
        if form.cleaned_data.get('date_to'):
            newsletters = newsletters.filter(created_at__lte=form.cleaned_data['date_to'])
    
    paginator = Paginator(newsletters, 20)
    page = request.GET.get('page')
    try:
        newsletters = paginator.page(page)
    except PageNotAnInteger:
        newsletters = paginator.page(1)
    except EmptyPage:
        newsletters = paginator.page(paginator.num_pages)
    
    context = {
        'newsletters': newsletters,
        'form': form,
    }
    return render(request, 'newsletter/newsletter_list.html', context)


@login_required
@user_passes_test(lambda u: u.can_manage_users)
def newsletter_create(request):
    """Create a new newsletter"""
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.created_by = request.user
            newsletter.save()
            form.save_m2m()  # Save many-to-many relationships
            
            UserActivityLog.objects.create(
                user=request.user,
                action='create',
                model_name='Newsletter',
                object_id=newsletter.id,
                description=f'Created newsletter: {newsletter.subject}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'Newsletter "{newsletter.subject}" created successfully!')
            return redirect('newsletter:edit', newsletter_id=newsletter.id)
    else:
        form = NewsletterForm()
    
    return render(request, 'newsletter/newsletter_create.html', {'form': form})


@login_required
@user_passes_test(lambda u: u.can_manage_users)
def newsletter_edit(request, newsletter_id):
    """Edit an existing newsletter"""
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    
    if newsletter.status in ['sent', 'sending']:
        messages.error(request, 'Cannot edit a newsletter that has been sent.')
        return redirect('newsletter:list')
    
    if request.method == 'POST':
        form = NewsletterForm(request.POST, instance=newsletter)
        if form.is_valid():
            newsletter = form.save()
            
            UserActivityLog.objects.create(
                user=request.user,
                action='update',
                model_name='Newsletter',
                object_id=newsletter.id,
                description=f'Updated newsletter: {newsletter.subject}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'Newsletter "{newsletter.subject}" updated successfully!')
            return redirect('newsletter:list')
    else:
        form = NewsletterForm(instance=newsletter)
    
    context = {
        'form': form,
        'newsletter': newsletter,
    }
    return render(request, 'newsletter/newsletter_edit.html', context)


@login_required
@user_passes_test(lambda u: u.can_manage_users)
def newsletter_send(request, newsletter_id):
    """Send a newsletter"""
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    
    if request.method == 'POST':
        test = request.POST.get('test', False)
        
        if newsletter.send(test=test):
            UserActivityLog.objects.create(
                user=request.user,
                action='send',
                model_name='Newsletter',
                object_id=newsletter.id,
                description=f'Sent newsletter: {newsletter.subject}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, f'Newsletter "{newsletter.subject}" sent successfully!')
        else:
            messages.error(request, f'Failed to send newsletter "{newsletter.subject}".')
        
        return redirect('newsletter:list')
    
    context = {
        'newsletter': newsletter,
        'subscriber_count': newsletter.subscribers_count,
    }
    return render(request, 'newsletter/newsletter_send.html', context)


@login_required
@user_passes_test(lambda u: u.can_manage_users)
def newsletter_history(request, newsletter_id):
    """View newsletter history and statistics"""
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    
    tracking = NewsletterTracking.objects.filter(newsletter=newsletter).order_by('-created_at')
    
    # Statistics
    opens = tracking.filter(action='open').count()
    clicks = tracking.filter(action='click').count()
    unsubscribes = tracking.filter(action='unsubscribe').count()
    bounces = tracking.filter(action='bounce').count()
    spam = tracking.filter(action='spam').count()
    
    # Open rate
    open_rate = (opens / newsletter.subscribers_count * 100) if newsletter.subscribers_count > 0 else 0
    
    context = {
        'newsletter': newsletter,
        'tracking': tracking[:100],
        'opens': opens,
        'clicks': clicks,
        'unsubscribes': unsubscribes,
        'bounces': bounces,
        'spam': spam,
        'open_rate': round(open_rate, 2),
    }
    return render(request, 'newsletter/newsletter_history.html', context)