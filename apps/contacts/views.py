from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import ContactMessage
from .forms import ContactForm, ContactReplyForm, ContactFilterForm
from apps.accounts.models import UserActivityLog

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            
            if request.user.is_authenticated:
                message.user = request.user
                message.name = request.user.get_full_name() or request.user.username
                message.email = request.user.email
            
            message.ip_address = request.META.get('REMOTE_ADDR')
            message.user_agent = request.META.get('HTTP_USER_AGENT', '')
            message.referer = request.META.get('HTTP_REFERER', '')
            message.save()
            
            # Send notification email to admin
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                send_mail(
                    f'New Contact Message: {message.subject}',
                    f"From: {message.name} ({message.email})\n\n{message.message}",
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL],
                    fail_silently=True
                )
            except Exception as e:
                print(f"Failed to send contact notification: {e}")
            
            messages.success(request, 'Your message has been sent successfully! We will get back to you soon.')
            return redirect('contact:success')
    else:
        if request.user.is_authenticated:
            initial = {
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
            }
            form = ContactForm(initial=initial)
        else:
            form = ContactForm()
    
    return render(request, 'contacts/contact.html', {'form': form})

def contact_success(request):
    return render(request, 'contacts/contact_success.html')

@login_required
@user_passes_test(lambda u: u.can_manage_users)
def contact_messages(request):
    messages_list = ContactMessage.objects.all().order_by('-created_at')
    
    # Filtering
    form = ContactFilterForm(request.GET)
    if form.is_valid():
        if form.cleaned_data.get('status'):
            messages_list = messages_list.filter(status=form.cleaned_data['status'])
        if form.cleaned_data.get('priority'):
            messages_list = messages_list.filter(priority=form.cleaned_data['priority'])
        if form.cleaned_data.get('search'):
            query = form.cleaned_data['search']
            messages_list = messages_list.filter(
                Q(name__icontains=query) |
                Q(email__icontains=query) |
                Q(subject__icontains=query) |
                Q(message__icontains=query)
            )
        if form.cleaned_data.get('date_from'):
            messages_list = messages_list.filter(created_at__gte=form.cleaned_data['date_from'])
        if form.cleaned_data.get('date_to'):
            messages_list = messages_list.filter(created_at__lte=form.cleaned_data['date_to'])
    
    paginator = Paginator(messages_list, 30)
    page = request.GET.get('page')
    try:
        messages_list = paginator.page(page)
    except PageNotAnInteger:
        messages_list = paginator.page(1)
    except EmptyPage:
        messages_list = paginator.page(paginator.num_pages)
    
    # Statistics
    stats = {
        'total': ContactMessage.objects.count(),
        'new': ContactMessage.objects.filter(status='new').count(),
        'read': ContactMessage.objects.filter(status='read').count(),
        'replied': ContactMessage.objects.filter(status='replied').count(),
        'archived': ContactMessage.objects.filter(status='archived').count(),
        'spam': ContactMessage.objects.filter(status='spam').count(),
    }
    
    context = {
        'messages': messages_list,
        'stats': stats,
        'form': form,
    }
    return render(request, 'contacts/contact_messages.html', context)

@login_required
@user_passes_test(lambda u: u.can_manage_users)
def contact_message_detail(request, message_id):
    message = get_object_or_404(ContactMessage, id=message_id)
    
    # Mark as read if it's new
    if message.status == 'new':
        message.mark_as_read()
    
    if request.method == 'POST':
        form = ContactReplyForm(request.POST)
        if form.is_valid():
            response = form.cleaned_data['response']
            message.reply(response, request.user)
            
            # Send email reply
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                send_mail(
                    f'Re: {message.subject}',
                    response,
                    settings.DEFAULT_FROM_EMAIL,
                    [message.email],
                    fail_silently=True
                )
            except Exception as e:
                print(f"Failed to send reply email: {e}")
            
            UserActivityLog.objects.create(
                user=request.user,
                action='reply',
                model_name='ContactMessage',
                object_id=message.id,
                description=f'Replied to contact message from {message.name}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'Reply sent successfully!')
            return redirect('contacts:message_detail', message_id=message.id)
    else:
        form = ContactReplyForm()
    
    context = {
        'message': message,
        'form': form,
    }
    return render(request, 'contacts/contact_message_detail.html', context)

@login_required
@user_passes_test(lambda u: u.can_manage_users)
@require_http_methods(["POST"])
def contact_message_reply(request, message_id):
    message = get_object_or_404(ContactMessage, id=message_id)
    response = request.POST.get('response')
    
    if response:
        message.reply(response, request.user)
        
        # Send email reply
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            send_mail(
                f'Re: {message.subject}',
                response,
                settings.DEFAULT_FROM_EMAIL,
                [message.email],
                fail_silently=True
            )
        except Exception as e:
            print(f"Failed to send reply email: {e}")
        
        messages.success(request, 'Reply sent successfully!')
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Response is required'})

@login_required
@user_passes_test(lambda u: u.can_manage_users)
@require_http_methods(["POST"])
def mark_as_read(request, message_id):
    message = get_object_or_404(ContactMessage, id=message_id)
    message.mark_as_read()
    return JsonResponse({'success': True})

@login_required
@user_passes_test(lambda u: u.can_manage_users)
@require_http_methods(["POST"])
def archive_message(request, message_id):
    message = get_object_or_404(ContactMessage, id=message_id)
    message.archive()
    messages.success(request, 'Message archived successfully.')
    return JsonResponse({'success': True})

@login_required
@user_passes_test(lambda u: u.can_manage_users)
@require_http_methods(["POST"])
def mark_as_spam(request, message_id):
    message = get_object_or_404(ContactMessage, id=message_id)
    message.mark_as_spam()
    messages.success(request, 'Message marked as spam.')
    return JsonResponse({'success': True})

@login_required
@user_passes_test(lambda u: u.can_manage_users)
def message_delete(request, message_id):
    message = get_object_or_404(ContactMessage, id=message_id)
    
    if request.method == 'POST':
        message.delete()
        messages.success(request, 'Message deleted successfully.')
        return redirect('contacts:messages')
    
    return render(request, 'contacts/contact_message_delete.html', {'message': message})