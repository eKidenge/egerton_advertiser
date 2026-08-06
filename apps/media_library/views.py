from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
import json
import os
from PIL import Image
from .models import MediaFile, MediaTag, MediaCategory, MediaFileTag, MediaFileCategory, MediaUsage
from .forms import MediaFileForm, MediaTagForm, MediaCategoryForm, MediaFilterForm
from apps.accounts.models import UserActivityLog

# ============================================================
# USER'S PERSONAL MEDIA LIBRARY (Logged in users only)
# ============================================================

@login_required
def media_library(request):
    """User's personal media library - shows only their own uploads"""
    user = request.user
    
    # Only show media uploaded by the current user
    media_files = MediaFile.objects.filter(
        uploaded_by=user,
        status__in=['available', 'processing']
    ).order_by('-created_at')
    
    # Filtering
    form = MediaFilterForm(request.GET)
    if form.is_valid():
        if form.cleaned_data.get('file_type'):
            media_files = media_files.filter(file_type=form.cleaned_data['file_type'])
        if form.cleaned_data.get('search'):
            query = form.cleaned_data['search']
            media_files = media_files.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(alt_text__icontains=query)
            )
        if form.cleaned_data.get('date_from'):
            media_files = media_files.filter(created_at__gte=form.cleaned_data['date_from'])
        if form.cleaned_data.get('date_to'):
            media_files = media_files.filter(created_at__lte=form.cleaned_data['date_to'])
        if form.cleaned_data.get('tag'):
            media_files = media_files.filter(tags__tag__id=form.cleaned_data['tag'])
    
    # Store count BEFORE pagination
    total_count = media_files.count()
    image_count = media_files.filter(file_type='image').count()
    video_count = media_files.filter(file_type='video').count()
    
    # Pagination
    paginator = Paginator(media_files, 24)
    page = request.GET.get('page')
    try:
        media_files = paginator.page(page)
    except PageNotAnInteger:
        media_files = paginator.page(1)
    except EmptyPage:
        media_files = paginator.page(paginator.num_pages)
    
    # Get tags and categories for filter
    tags = MediaTag.objects.all().order_by('name')
    categories = MediaCategory.objects.all().order_by('name')
    
    context = {
        'media_files': media_files,
        'form': form,
        'tags': tags,
        'categories': categories,
        'total_count': total_count,
        'image_count': image_count,
        'video_count': video_count,
        'is_personal_library': True,
    }
    return render(request, 'media_library/media_library.html', context)


# ============================================================
# PUBLIC GALLERY VIEWS (No login required - shows ALL media)
# ============================================================

def public_photos(request):
    """Public photos gallery - displays ALL available photos from ALL users"""
    from django.core.files.storage import default_storage
    
    # Get base queryset
    base_media_files = MediaFile.objects.filter(
        file_type='image',
        status='available'
    ).order_by('-created_at')
    
    # Filter out files that don't have actual files on disk
    valid_ids = []
    for media in base_media_files:
        if media.file and default_storage.exists(media.file.name):
            valid_ids.append(media.id)
    
    if valid_ids:
        media_files = base_media_files.filter(id__in=valid_ids)
    else:
        media_files = base_media_files.none()
    
    # Store count BEFORE pagination
    total_count = media_files.count()
    image_count = media_files.filter(file_type='image').count()
    video_count = media_files.filter(file_type='video').count()
    
    # Pagination
    paginator = Paginator(media_files, 24)
    page = request.GET.get('page')
    try:
        media_files = paginator.page(page)
    except PageNotAnInteger:
        media_files = paginator.page(1)
    except EmptyPage:
        media_files = paginator.page(paginator.num_pages)
    
    # Get tags and categories for filter
    tags = MediaTag.objects.all().order_by('name')
    categories = MediaCategory.objects.all().order_by('name')
    
    context = {
        'media_files': media_files,
        'form': MediaFilterForm(request.GET),
        'tags': tags,
        'categories': categories,
        'total_count': total_count,
        'image_count': image_count,
        'video_count': video_count,
        'is_public': True,
        'section_title': 'Photos',
        'section_icon': 'fa-images',
    }
    return render(request, 'media_library/media_library.html', context)


def public_videos(request):
    """Public videos gallery - displays ALL available videos from ALL users"""
    from django.core.files.storage import default_storage
    
    # Get base queryset
    base_media_files = MediaFile.objects.filter(
        file_type='video',
        status='available'
    ).order_by('-created_at')
    
    # Filter out files that don't have actual files on disk
    valid_ids = []
    for media in base_media_files:
        if media.file and default_storage.exists(media.file.name):
            valid_ids.append(media.id)
    
    if valid_ids:
        media_files = base_media_files.filter(id__in=valid_ids)
    else:
        media_files = base_media_files.none()
    
    # Store count BEFORE pagination
    total_count = media_files.count()
    image_count = media_files.filter(file_type='image').count()
    video_count = media_files.filter(file_type='video').count()
    
    # Pagination
    paginator = Paginator(media_files, 24)
    page = request.GET.get('page')
    try:
        media_files = paginator.page(page)
    except PageNotAnInteger:
        media_files = paginator.page(1)
    except EmptyPage:
        media_files = paginator.page(paginator.num_pages)
    
    # Get tags and categories for filter
    tags = MediaTag.objects.all().order_by('name')
    categories = MediaCategory.objects.all().order_by('name')
    
    context = {
        'media_files': media_files,
        'form': MediaFilterForm(request.GET),
        'tags': tags,
        'categories': categories,
        'total_count': total_count,
        'image_count': image_count,
        'video_count': video_count,
        'is_public': True,
        'section_title': 'Videos',
        'section_icon': 'fa-video',
    }
    return render(request, 'media_library/media_library.html', context)


# ============================================================
# ADMIN VIEW - Shows ALL media (For admin dashboard)
# ============================================================

@login_required
@user_passes_test(lambda u: u.role in ['super_admin', 'admin'] or u.is_staff)
def admin_media_library(request):
    """Admin view - shows ALL media from ALL users"""
    from django.core.files.storage import default_storage
    
    base_media_files = MediaFile.objects.filter(
        status__in=['available', 'processing']
    ).order_by('-created_at')
    
    # Filter out files that don't have actual files on disk
    valid_ids = []
    for media in base_media_files:
        if media.file and default_storage.exists(media.file.name):
            valid_ids.append(media.id)
    
    if valid_ids:
        media_files = base_media_files.filter(id__in=valid_ids)
    else:
        media_files = base_media_files.none()
    
    # Filtering
    form = MediaFilterForm(request.GET)
    if form.is_valid():
        if form.cleaned_data.get('file_type'):
            media_files = media_files.filter(file_type=form.cleaned_data['file_type'])
        if form.cleaned_data.get('search'):
            query = form.cleaned_data['search']
            media_files = media_files.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(alt_text__icontains=query)
            )
        if form.cleaned_data.get('date_from'):
            media_files = media_files.filter(created_at__gte=form.cleaned_data['date_from'])
        if form.cleaned_data.get('date_to'):
            media_files = media_files.filter(created_at__lte=form.cleaned_data['date_to'])
        if form.cleaned_data.get('tag'):
            media_files = media_files.filter(tags__tag__id=form.cleaned_data['tag'])
    
    # Store count BEFORE pagination
    total_count = media_files.count()
    image_count = media_files.filter(file_type='image').count()
    video_count = media_files.filter(file_type='video').count()
    
    paginator = Paginator(media_files, 24)
    page = request.GET.get('page')
    try:
        media_files = paginator.page(page)
    except PageNotAnInteger:
        media_files = paginator.page(1)
    except EmptyPage:
        media_files = paginator.page(paginator.num_pages)
    
    tags = MediaTag.objects.all().order_by('name')
    categories = MediaCategory.objects.all().order_by('name')
    
    context = {
        'media_files': media_files,
        'form': form,
        'tags': tags,
        'categories': categories,
        'total_count': total_count,
        'image_count': image_count,
        'video_count': video_count,
        'is_admin_view': True,
    }
    return render(request, 'media_library/media_library.html', context)


# ============================================================
# MEDIA UPLOAD
# ============================================================
@login_required
def media_upload(request):
    """Upload media files - supports both GET and POST"""
    
    categories = MediaCategory.objects.all().order_by('name')
    tags = MediaTag.objects.all().order_by('name')
    
    if request.method == 'POST':
        form = MediaFileForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                media_file = form.save(commit=False)
                media_file.uploaded_by = request.user
                media_file.status = 'processing'
                media_file.save()
                
                # Process image thumbnails
                if media_file.file_type == 'image':
                    try:
                        process_image_thumbnails(media_file)
                    except Exception as e:
                        print(f"Thumbnail error: {e}")
                
                media_file.status = 'available'
                media_file.save()
                
                # ✅ FIX: Handle tags properly with both name and slug
                from django.utils.text import slugify
                tag_names = form.cleaned_data.get('tag_names')
                if tag_names:
                    if isinstance(tag_names, list):
                        tag_names = ', '.join(tag_names)
                    for tag_name in tag_names.split(','):
                        tag_name = tag_name.strip()
                        if tag_name:
                            # Check if tag exists by name first
                            tag, created = MediaTag.objects.get_or_create(
                                name=tag_name,
                                defaults={'slug': slugify(tag_name)}
                            )
                            # If tag exists but slug is different, update slug
                            if not created and tag.slug != slugify(tag_name):
                                tag.slug = slugify(tag_name)
                                tag.save()
                            
                            MediaFileTag.objects.get_or_create(
                                media_file=media_file,
                                tag=tag
                            )
                
                # Save category
                category_id = request.POST.get('category')
                if category_id and category_id.isdigit():
                    try:
                        category = MediaCategory.objects.get(id=category_id)
                        MediaFileCategory.objects.get_or_create(
                            media_file=media_file,
                            category=category
                        )
                    except MediaCategory.DoesNotExist:
                        pass
                
                messages.success(request, f'✅ Media file "{media_file.title}" uploaded successfully!')
                return redirect('media_library:library')
                
            except Exception as e:
                messages.error(request, f'❌ Error: {str(e)}')
                # Return to form with error
                return render(request, 'media_library/media_upload.html', {
                    'form': form,
                    'tags': tags,
                    'categories': categories,
                })
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = MediaFileForm()
    
    context = {
        'form': form,
        'tags': tags,
        'categories': categories,
    }
    return render(request, 'media_library/media_upload.html', context)


# ============================================================
# THUMBNAIL PROCESSING
# ============================================================

def process_image_thumbnails(media_file):
    """Generate thumbnails for uploaded images"""
    from django.core.files import File
    from io import BytesIO
    
    image_path = media_file.file.path
    img = Image.open(image_path)
    
    # Get image dimensions
    media_file.width, media_file.height = img.size
    
    # Generate thumbnails
    sizes = {
        'small': (150, 150),
        'medium': (300, 200),
        'large': (600, 400),
    }
    
    for size_name, dimensions in sizes.items():
        thumb_img = img.copy()
        thumb_img.thumbnail(dimensions, Image.LANCZOS)
        
        thumb_io = BytesIO()
        thumb_img.save(thumb_io, format='JPEG' if img.mode == 'RGB' else 'PNG', quality=85)
        
        # Save to appropriate field
        field_name = f'thumbnail_{size_name}'
        if hasattr(media_file, field_name):
            thumb_file = File(thumb_io, name=f"{size_name}_{os.path.basename(media_file.file.name)}")
            getattr(media_file, field_name).save(thumb_file.name, thumb_file, save=False)
    
    media_file.save()


# ============================================================
# MEDIA GALLERY (User's personal gallery)
# ============================================================

@login_required
def media_gallery(request):
    """User's personal gallery - shows only their own media"""
    user = request.user
    media_files = MediaFile.objects.filter(
        uploaded_by=user,
        status='available'
    ).order_by('-created_at')
    
    # Filter by file type
    file_type = request.GET.get('type')
    if file_type:
        media_files = media_files.filter(file_type=file_type)
    
    return render(request, 'media_library/media_gallery.html', {
        'media_files': media_files,
        'file_type_filter': file_type,
    })


# ============================================================
# MEDIA DETAIL
# ============================================================

@login_required
def media_detail(request, media_id):
    media_file = get_object_or_404(MediaFile, id=media_id)
    
    if media_file.uploaded_by != request.user and not request.user.can_manage_users:
        messages.error(request, 'You do not have permission to view this media file.')
        return redirect('media_library:library')
    
    # Get usage information
    usages = MediaUsage.objects.filter(media_file=media_file).order_by('-used_at')
    
    # Get tags and categories
    tags = media_file.tags.all()
    categories = media_file.categories.all()
    
    context = {
        'media_file': media_file,
        'usages': usages,
        'tags': tags,
        'categories': categories,
    }
    return render(request, 'media_library/media_detail.html', context)


# ============================================================
# MEDIA DELETE
# ============================================================

@login_required
@require_http_methods(["POST"])
def media_delete(request, media_id):
    media_file = get_object_or_404(MediaFile, id=media_id)
    
    if media_file.uploaded_by != request.user and not request.user.can_manage_users:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Delete file from storage
    if media_file.file:
        media_file.file.delete(save=False)
    
    # Delete thumbnails
    for size in ['small', 'medium', 'large']:
        field_name = f'thumbnail_{size}'
        if hasattr(media_file, field_name):
            thumbnail = getattr(media_file, field_name)
            if thumbnail:
                thumbnail.delete(save=False)
    
    media_file.status = 'deleted'
    media_file.save()
    
    UserActivityLog.objects.create(
        user=request.user,
        action='delete',
        model_name='MediaFile',
        object_id=media_file.id,
        description=f'Deleted media file: {media_file.title}',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    messages.success(request, f'Media file "{media_file.title}" deleted successfully.')
    return redirect('media_library:library')


# ============================================================
# BULK UPLOAD
# ============================================================

@login_required
@require_http_methods(["POST"])
def bulk_upload_media(request):
    """Handle multiple file uploads"""
    uploaded_files = []
    errors = []
    
    for file in request.FILES.getlist('files'):
        try:
            media_file = MediaFile.objects.create(
                title=file.name,
                file=file,
                uploaded_by=request.user,
                status='processing'
            )
            
            # Process image thumbnails
            if media_file.file_type == 'image':
                try:
                    process_image_thumbnails(media_file)
                except Exception as e:
                    print(f"Error processing thumbnails for {file.name}: {e}")
            
            media_file.status = 'available'
            media_file.save()
            
            uploaded_files.append({
                'id': media_file.id,
                'name': media_file.title,
                'url': media_file.get_file_url()
            })
        except Exception as e:
            errors.append({'file': file.name, 'error': str(e)})
    
    return JsonResponse({
        'success': True,
        'uploaded': uploaded_files,
        'errors': errors
    })


# ============================================================
# TAG MANAGEMENT
# ============================================================

@login_required
def tag_list(request):
    tags = MediaTag.objects.annotate(
        file_count=Count('media_files')
    ).order_by('name')
    
    return render(request, 'media_library/tag_list.html', {'tags': tags})


@login_required
def tag_create(request):
    if request.method == 'POST':
        form = MediaTagForm(request.POST)
        if form.is_valid():
            tag = form.save()
            messages.success(request, f'Tag "{tag.name}" created successfully!')
            return redirect('media_library:tag_list')
    else:
        form = MediaTagForm()
    
    return render(request, 'media_library/tag_create.html', {'form': form})


@login_required
def tag_edit(request, tag_id):
    tag = get_object_or_404(MediaTag, id=tag_id)
    
    if request.method == 'POST':
        form = MediaTagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tag "{tag.name}" updated successfully!')
            return redirect('media_library:tag_list')
    else:
        form = MediaTagForm(instance=tag)
    
    return render(request, 'media_library/tag_edit.html', {'form': form, 'tag': tag})


@login_required
def tag_delete(request, tag_id):
    tag = get_object_or_404(MediaTag, id=tag_id)
    
    if request.method == 'POST':
        name = tag.name
        tag.delete()
        messages.success(request, f'Tag "{name}" deleted successfully!')
        return redirect('media_library:tag_list')
    
    return render(request, 'media_library/tag_delete.html', {'tag': tag})


# ============================================================
# CATEGORY MANAGEMENT
# ============================================================

@login_required
def category_list(request):
    categories = MediaCategory.objects.annotate(
        file_count=Count('media_files')
    ).order_by('name')
    
    return render(request, 'media_library/category_list.html', {'categories': categories})


@login_required
def category_create(request):
    if request.method == 'POST':
        form = MediaCategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" created successfully!')
            return redirect('media_library:category_list')
    else:
        form = MediaCategoryForm()
    
    return render(request, 'media_library/category_create.html', {'form': form})


@login_required
def category_edit(request, category_id):
    category = get_object_or_404(MediaCategory, id=category_id)
    
    if request.method == 'POST':
        form = MediaCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{category.name}" updated successfully!')
            return redirect('media_library:category_list')
    else:
        form = MediaCategoryForm(instance=category)
    
    return render(request, 'media_library/category_edit.html', {'form': form, 'category': category})


@login_required
def category_delete(request, category_id):
    category = get_object_or_404(MediaCategory, id=category_id)
    
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Category "{name}" deleted successfully!')
        return redirect('media_library:category_list')
    
    return render(request, 'media_library/category_delete.html', {'category': category})