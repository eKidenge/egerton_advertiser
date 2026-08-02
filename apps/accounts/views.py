from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q, Count, Avg, Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import random
import string
import logging

from .models import User, UserActivityLog, UserProfile
from .forms import (
    UserRegistrationForm, UserLoginForm, UserProfileForm, 
    UserEditForm, PasswordResetForm, UserCreateForm,
    UserActivityFilterForm
)
from apps.articles.models import Article
from apps.comments.models import Comment

# Set up logging
logger = logging.getLogger(__name__)


# ============================================
# HELPER FUNCTIONS
# ============================================

def generate_verification_code():
    """Generate a 6-digit verification code"""
    return ''.join(random.choices(string.digits, k=6))


def get_role_dashboard_url(user):
    """
    Get the appropriate dashboard URL name based on user role
    """
    # Map roles to dashboard URL names
    # dashboard:home is the main dashboard view
    # dashboard:admin_dashboard is the admin view
    role_dashboard_map = {
        'super_admin': 'dashboard:admin_dashboard',
        'admin': 'dashboard:admin_dashboard',
        'editor': 'dashboard:home',
        'journalist': 'dashboard:home',
        'subscriber': 'dashboard:home',
        'advertiser': 'dashboard:home',
    }
    
    # Return the dashboard URL name for this role, default to regular dashboard
    return role_dashboard_map.get(user.role, 'dashboard:home')


def redirect_to_role_dashboard(user):
    """
    Redirect user to their role-specific dashboard
    """
    dashboard_url = get_role_dashboard_url(user)
    return redirect(dashboard_url)


# ============================================
# AUTHENTICATION VIEWS
# ============================================

def user_login(request):
    """User login view with role-based redirection"""
    if request.user.is_authenticated:
        return redirect_to_role_dashboard(request.user)
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        
        # Debug: Check form data
        print("=" * 60)
        print("LOGIN FORM DATA:")
        print(f"POST data: {request.POST}")
        
        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)
            
            print(f"Username/Email: '{username_or_email}'")
            print(f"Password length: {len(password)}")
            
            # Check if user exists
            user_obj = None
            try:
                user_obj = User.objects.get(username=username_or_email)
                print(f"✅ User found by username: {user_obj.username}")
            except User.DoesNotExist:
                print(f"❌ No user found with username: {username_or_email}")
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    print(f"✅ User found by email: {user_obj.username}")
                except User.DoesNotExist:
                    print(f"❌ No user found with email: {username_or_email}")
            
            # Try authentication
            user = authenticate(request, username=username_or_email, password=password)
            
            if user is None and user_obj is not None:
                print(f"Trying to authenticate with username: {user_obj.username}")
                user = authenticate(request, username=user_obj.username, password=password)
            
            if user is not None:
                print(f"✅ AUTHENTICATION SUCCESSFUL: {user.username}")
                
                if user.is_account_locked():
                    messages.error(request, 'Your account is temporarily locked. Please try again later.')
                    return render(request, 'accounts/login.html', {'form': form})
                
                try:
                    login(request, user)
                    print(f"✅ LOGIN SUCCESSFUL for {user.username}")
                except Exception as e:
                    print(f"Login error: {str(e)}")
                    messages.error(request, 'Login failed. Please try again.')
                    return render(request, 'accounts/login.html', {'form': form})
                
                # Log activity
                UserActivityLog.objects.create(
                    user=user,
                    action='login',
                    model_name='User',
                    object_id=user.id,
                    description=f'User {user.username} logged in',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    referer=request.META.get('HTTP_REFERER', '')
                )
                
                user.failed_login_attempts = 0
                user.save(update_fields=['failed_login_attempts'])
                
                if not remember_me:
                    request.session.set_expiry(0)
                else:
                    request.session.set_expiry(1209600)
                
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                
                return redirect_to_role_dashboard(user)
            else:
                # Check password manually
                if user_obj is not None:
                    from django.contrib.auth.hashers import check_password
                    is_correct = check_password(password, user_obj.password)
                    print(f"Password check result: {is_correct}")
                    
                    if is_correct:
                        print("✅ Password is correct but authentication failed!")
                    else:
                        print("❌ Password is incorrect")
                
                try:
                    if '@' in username_or_email:
                        user = User.objects.get(email=username_or_email)
                    else:
                        user = User.objects.get(username=username_or_email)
                    user.increment_failed_attempts()
                except User.DoesNotExist:
                    pass
                messages.error(request, 'Invalid username/email or password.')
        else:
            # Print form errors in detail
            print("❌ FORM IS INVALID")
            print(f"Form errors: {form.errors}")
            print(f"Form non-field errors: {form.non_field_errors()}")
            
            # Add form errors to messages
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        messages.error(request, f'{field}: {error}')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    """User logout view"""
    if request.user.is_authenticated:
        UserActivityLog.objects.create(
            user=request.user,
            action='logout',
            model_name='User',
            object_id=request.user.id,
            description=f'User {request.user.username} logged out',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        logout(request)
        messages.info(request, 'You have been logged out successfully.')
    return redirect('home')


def user_register(request):
    """User registration view with auto-login and role-based redirection"""
    if request.user.is_authenticated:
        return redirect_to_role_dashboard(request.user)
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        
        # DEBUG: Log form data
        logger.info("=" * 60)
        logger.info("REGISTRATION ATTEMPT")
        logger.info(f"POST data: {request.POST}")
        logger.info("=" * 60)
        
        # Check if form is valid
        if form.is_valid():
            logger.info("✅ FORM IS VALID - Creating user...")
            
            try:
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password1'])
                
                # Set default role if not specified
                if not user.role:
                    user.role = 'subscriber'
                
                user.save()
                
                # Create profile
                UserProfile.objects.create(
                    user=user,
                    newsletter_subscription=form.cleaned_data.get('newsletter_subscription', True)
                )
                
                # Log activity
                UserActivityLog.objects.create(
                    user=user,
                    action='create',
                    model_name='User',
                    object_id=user.id,
                    description=f'New user registered: {user.username}',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                # Send welcome email (with error handling)
                try:
                    subject = 'Welcome to The Egerton Advertiser'
                    html_message = render_to_string('accounts/emails/welcome.html', {
                        'user': user,
                        'site_name': 'The Egerton Advertiser',
                        'site_url': request.build_absolute_uri('/').rstrip('/')
                    })
                    plain_message = strip_tags(html_message)
                    send_mail(
                        subject,
                        plain_message,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        html_message=html_message,
                        fail_silently=True
                    )
                except Exception as e:
                    # Log but don't fail registration
                    logger.warning(f"Welcome email not sent: {str(e)}")
                
                # Auto-login after registration
                try:
                    login(request, user)
                except Exception as e:
                    logger.warning(f"Auto-login issue: {str(e)}")
                    # If auto-login fails, redirect to login page
                    messages.success(request, f'Registration successful! Please log in.')
                    return redirect('accounts:login')
                
                messages.success(request, f'Welcome to The Egerton Advertiser, {user.username}!')
                
                # Redirect to role-specific dashboard
                logger.info(f"✅ Registration successful! Redirecting to: {get_role_dashboard_url(user)}")
                return redirect_to_role_dashboard(user)
                
            except Exception as e:
                logger.error(f"❌ Error during registration: {str(e)}")
                messages.error(request, f'Registration failed. Please try again.')
                return render(request, 'accounts/register.html', {'form': form})
        else:
            # DEBUG: Log form errors
            logger.error("❌ FORM IS INVALID")
            logger.error(f"Form errors: {form.errors}")
            
            # Log each field error
            for field, errors in form.errors.items():
                logger.error(f"Field '{field}': {', '.join(errors)}")
            
            # Add error messages for user
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


# ============================================
# PROFILE VIEWS
# ============================================

@login_required
def profile_view(request, user_id=None):
    """View user profile"""
    if user_id:
        user = get_object_or_404(User, id=user_id)
        if user != request.user and not request.user.can_manage_users:
            messages.error(request, 'You do not have permission to view this profile.')
            return redirect('accounts:profile', user_id=request.user.id)
    else:
        user = request.user
    
    # Get user statistics
    articles = Article.objects.filter(author=user)
    published_count = articles.filter(status='published').count()
    draft_count = articles.filter(status='draft').count()
    total_views = articles.aggregate(Sum('views_count'))['views_count__sum'] or 0
    
    comments = Comment.objects.filter(user=user)
    comment_count = comments.count()
    
    recent_articles = articles.order_by('-created_at')[:5]
    recent_comments = comments.order_by('-created_at')[:5]
    
    # Get user activity
    recent_activities = UserActivityLog.objects.filter(user=user).order_by('-timestamp')[:10]
    
    context = {
        'profile_user': user,
        'published_count': published_count,
        'draft_count': draft_count,
        'total_views': total_views,
        'comment_count': comment_count,
        'recent_articles': recent_articles,
        'recent_comments': recent_comments,
        'recent_activities': recent_activities,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_edit(request):
    """Edit user profile"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            
            # Update profile fields
            profile = user.profile
            profile.date_of_birth = form.cleaned_data.get('date_of_birth')
            profile.gender = form.cleaned_data.get('gender')
            profile.country = form.cleaned_data.get('country')
            profile.city = form.cleaned_data.get('city')
            profile.organization = form.cleaned_data.get('organization')
            profile.save()
            
            UserActivityLog.objects.create(
                user=request.user,
                action='update',
                model_name='User',
                object_id=request.user.id,
                description=f'User {request.user.username} updated profile',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile', user_id=request.user.id)
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
def change_password(request):
    """Change user password"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            
            UserActivityLog.objects.create(
                user=request.user,
                action='update',
                model_name='User',
                object_id=request.user.id,
                description=f'User {request.user.username} changed password',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:profile', user_id=request.user.id)
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})


# ============================================
# PASSWORD RESET VIEWS
# ============================================

def forgot_password(request):
    """Forgot password view"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Generate reset token
            token = generate_verification_code()
            request.session['password_reset_token'] = token
            request.session['password_reset_user_id'] = user.id
            
            # Send reset email
            try:
                subject = 'Password Reset - The Egerton Advertiser'
                html_message = render_to_string('accounts/emails/password_reset.html', {
                    'user': user,
                    'token': token,
                    'site_name': 'The Egerton Advertiser',
                    'site_url': request.build_absolute_uri('/').rstrip('/')
                })
                plain_message = strip_tags(html_message)
                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=html_message,
                    fail_silently=True
                )
            except Exception as e:
                logger.error(f"Failed to send reset email: {e}")
            
            messages.success(request, 'Password reset instructions have been sent to your email.')
            return redirect('accounts:reset_password')
        except User.DoesNotExist:
            messages.error(request, 'No user found with this email address.')
    
    return render(request, 'accounts/forgot_password.html')


def reset_password(request):
    """Reset password view"""
    if request.method == 'POST':
        token = request.POST.get('token')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/reset_password.html')
        
        session_token = request.session.get('password_reset_token')
        user_id = request.session.get('password_reset_user_id')
        
        if token == session_token and user_id:
            try:
                user = User.objects.get(id=user_id)
                user.set_password(password)
                user.save()
                
                # Clear session
                del request.session['password_reset_token']
                del request.session['password_reset_user_id']
                
                UserActivityLog.objects.create(
                    user=user,
                    action='update',
                    model_name='User',
                    object_id=user.id,
                    description=f'User {user.username} reset password',
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                
                messages.success(request, 'Password has been reset successfully. Please log in.')
                return redirect('accounts:login')
            except User.DoesNotExist:
                messages.error(request, 'Invalid reset request.')
        else:
            messages.error(request, 'Invalid or expired token.')
    
    return render(request, 'accounts/reset_password.html')


# ============================================
# ADMIN USER MANAGEMENT VIEWS
# ============================================

@login_required
@user_passes_test(lambda u: u.can_manage_users)
def user_list(request):
    """List all users (admin only)"""
    query = request.GET.get('q', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    
    users = User.objects.all()
    
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
    
    if role_filter:
        users = users.filter(role=role_filter)
    
    if status_filter:
        if status_filter == 'active':
            users = users.filter(is_active=True)
        elif status_filter == 'inactive':
            users = users.filter(is_active=False)
        elif status_filter == 'verified':
            users = users.filter(is_verified=True)
        elif status_filter == 'unverified':
            users = users.filter(is_verified=False)
    
    # Pagination
    paginator = Paginator(users, 20)
    page = request.GET.get('page')
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    
    context = {
        'users': users,
        'query': query,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'role_choices': User.ROLE_CHOICES,
    }
    return render(request, 'accounts/user_list.html', context)


@login_required
@user_passes_test(lambda u: u.can_manage_users)
def user_detail(request, user_id):
    """View user details (admin only)"""
    user = get_object_or_404(User, id=user_id)
    
    # Statistics
    articles = Article.objects.filter(author=user)
    total_articles = articles.count()
    published_articles = articles.filter(status='published').count()
    draft_articles = articles.filter(status='draft').count()
    pending_articles = articles.filter(status='pending').count()
    total_views = articles.aggregate(Sum('views_count'))['views_count__sum'] or 0
    
    comments = Comment.objects.filter(user=user)
    total_comments = comments.count()
    
    recent_activities = UserActivityLog.objects.filter(user=user).order_by('-timestamp')[:20]
    
    context = {
        'user': user,
        'total_articles': total_articles,
        'published_articles': published_articles,
        'draft_articles': draft_articles,
        'pending_articles': pending_articles,
        'total_views': total_views,
        'total_comments': total_comments,
        'recent_activities': recent_activities,
    }
    return render(request, 'accounts/user_detail.html', context)


@login_required
@user_passes_test(lambda u: u.can_manage_users)
def user_create(request):
    """Create new user (admin only)"""
    if request.method == 'POST':
        form = UserCreateForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Create profile
            UserProfile.objects.create(user=user)
            
            # Send account creation email
            try:
                subject = 'Your Account at The Egerton Advertiser'
                html_message = render_to_string('accounts/emails/account_created.html', {
                    'user': user,
                    'password': form.cleaned_data['password'],
                    'site_name': 'The Egerton Advertiser',
                    'site_url': request.build_absolute_uri('/').rstrip('/')
                })
                plain_message = strip_tags(html_message)
                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=html_message,
                    fail_silently=True
                )
            except Exception as e:
                logger.error(f"Failed to send account creation email: {e}")
            
            UserActivityLog.objects.create(
                user=request.user,
                action='create',
                model_name='User',
                object_id=user.id,
                description=f'Admin {request.user.username} created user {user.username}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'User {user.username} created successfully!')
            return redirect('accounts:user_detail', user_id=user.id)
    else:
        form = UserCreateForm()
    
    return render(request, 'accounts/user_create.html', {'form': form})


@login_required
@user_passes_test(lambda u: u.can_manage_users)
def user_edit(request, user_id):
    """Edit user (admin only)"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            
            UserActivityLog.objects.create(
                user=request.user,
                action='update',
                model_name='User',
                object_id=user.id,
                description=f'Admin {request.user.username} updated user {user.username}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'User {user.username} updated successfully!')
            return redirect('accounts:user_detail', user_id=user.id)
    else:
        form = UserEditForm(instance=user)
    
    return render(request, 'accounts/user_edit.html', {'form': form, 'edit_user': user})


@login_required
@user_passes_test(lambda u: u.can_manage_users)
def user_delete(request, user_id):
    """Delete user (admin only)"""
    user = get_object_or_404(User, id=user_id)
    
    # Prevent self-deletion
    if request.user == user:
        messages.error(request, 'You cannot delete your own account!')
        return redirect('accounts:user_list')
    
    # Prevent deleting the last superuser
    if user.is_superuser and User.objects.filter(is_superuser=True).count() <= 1:
        messages.error(request, 'Cannot delete the last superuser!')
        return redirect('accounts:user_list')
    
    if request.method == 'POST':
        username = user.username
        
        # Archive user content
        Article.objects.filter(author=user).update(status='archived')
        
        # Delete user
        user.delete()
        
        UserActivityLog.objects.create(
            user=request.user,
            action='delete',
            model_name='User',
            object_id=user_id,
            description=f'Admin {request.user.username} deleted user {username}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, f'User {username} has been deleted.')
        return redirect('accounts:user_list')
    
    return render(request, 'accounts/user_delete.html', {'user': user})


# ============================================
# ROLE MANAGEMENT VIEWS
# ============================================

@login_required
@user_passes_test(lambda u: u.can_manage_users)
def role_list(request):
    """List all roles with statistics"""
    roles = User.ROLE_CHOICES
    role_stats = {}
    
    for role_code, role_name in roles:
        count = User.objects.filter(role=role_code).count()
        role_stats[role_code] = {
            'name': role_name,
            'count': count,
        }
    
    context = {'role_stats': role_stats}
    return render(request, 'accounts/role_list.html', context)


@login_required
@user_passes_test(lambda u: u.can_manage_users)
def role_create(request):
    """Create new role"""
    if request.method == 'POST':
        role_code = request.POST.get('role_code')
        role_name = request.POST.get('role_name')
        permissions = request.POST.getlist('permissions')
        
        # Create role (using group)
        from django.contrib.auth.models import Group, Permission
        
        group, created = Group.objects.get_or_create(name=role_name)
        
        # Add permissions
        for perm_code in permissions:
            try:
                perm = Permission.objects.get(codename=perm_code)
                group.permissions.add(perm)
            except Permission.DoesNotExist:
                pass
        
        messages.success(request, f'Role {role_name} created successfully!')
        return redirect('accounts:role_list')
    
    # Get all available permissions
    from django.contrib.auth.models import Permission
    all_permissions = Permission.objects.all().order_by('content_type__app_label', 'codename')
    
    context = {'all_permissions': all_permissions}
    return render(request, 'accounts/role_create.html', context)


@login_required
@user_passes_test(lambda u: u.can_manage_users)
def role_edit(request, role_id):
    """Edit role"""
    from django.contrib.auth.models import Group, Permission
    
    group = get_object_or_404(Group, id=role_id)
    
    if request.method == 'POST':
        group.name = request.POST.get('role_name')
        group.save()
        
        # Update permissions
        group.permissions.clear()
        permissions = request.POST.getlist('permissions')
        for perm_code in permissions:
            try:
                perm = Permission.objects.get(codename=perm_code)
                group.permissions.add(perm)
            except Permission.DoesNotExist:
                pass
        
        messages.success(request, f'Role {group.name} updated successfully!')
        return redirect('accounts:role_list')
    
    all_permissions = Permission.objects.all().order_by('content_type__app_label', 'codename')
    current_permissions = group.permissions.values_list('codename', flat=True)
    
    context = {
        'group': group,
        'all_permissions': all_permissions,
        'current_permissions': list(current_permissions),
    }
    return render(request, 'accounts/role_edit.html', context)


# ============================================
# ACTIVITY LOG VIEWS
# ============================================

@login_required
def activity_log(request):
    """View activity log"""
    if request.user.can_manage_users:
        activities = UserActivityLog.objects.all()
    else:
        activities = UserActivityLog.objects.filter(user=request.user)
    
    # Filtering
    form = UserActivityFilterForm(request.GET)
    if form.is_valid():
        if form.cleaned_data.get('user'):
            activities = activities.filter(user=form.cleaned_data['user'])
        if form.cleaned_data.get('action'):
            activities = activities.filter(action=form.cleaned_data['action'])
        if form.cleaned_data.get('start_date'):
            activities = activities.filter(timestamp__gte=form.cleaned_data['start_date'])
        if form.cleaned_data.get('end_date'):
            activities = activities.filter(timestamp__lte=form.cleaned_data['end_date'])
    
    activities = activities.order_by('-timestamp')
    
    paginator = Paginator(activities, 50)
    page = request.GET.get('page')
    try:
        activities = paginator.page(page)
    except PageNotAnInteger:
        activities = paginator.page(1)
    except EmptyPage:
        activities = paginator.page(paginator.num_pages)
    
    context = {
        'activities': activities,
        'form': form,
    }
    return render(request, 'dashboard/activity_log.html', context)


# ============================================
# ERROR HANDLERS
# ============================================

def handler403(request, exception=None):
    """403 Forbidden error handler"""
    return render(request, '403.html', status=403)


def handler404(request, exception=None):
    """404 Not Found error handler"""
    return render(request, '404.html', status=404)


def handler500(request):
    """500 Internal Server Error handler"""
    try:
        return render(request, '500.html', status=500)
    except Exception:
        return HttpResponseRedirect('/')


# ============================================
# RATE LIMIT EXCEEDED VIEW
# ============================================

def rate_limit_exceeded(request, exception=None):
    """Rate limit exceeded handler"""
    return render(request, '429.html', status=429)   #give full as you say, hope you know that i have role based