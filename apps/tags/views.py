from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from .models import Tag
from .forms import TagForm
from apps.articles.models import Article
from apps.accounts.models import UserActivityLog

def tag_list(request):
    tags = Tag.objects.filter(is_active=True).order_by('-article_count')
    
    # Update article counts
    for tag in tags:
        tag.update_article_count()
    
    paginator = Paginator(tags, 50)
    page = request.GET.get('page')
    try:
        tags = paginator.page(page)
    except PageNotAnInteger:
        tags = paginator.page(1)
    except EmptyPage:
        tags = paginator.page(paginator.num_pages)
    
    return render(request, 'tags/tag_list.html', {'tags': tags})

def tag_detail(request, slug):
    tag = get_object_or_404(Tag, slug=slug, is_active=True)
    
    articles = Article.objects.filter(
        tags=tag,
        status='published',
        published_at__lte=timezone.now()
    ).select_related('author', 'category').order_by('-published_at')
    
    paginator = Paginator(articles, 20)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    context = {
        'tag': tag,
        'articles': articles,
        'article_count': articles.count(),
    }
    return render(request, 'tags/tag_detail.html', context)

@login_required
@user_passes_test(lambda u: u.can_manage_users)
def tag_create(request):
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            tag = form.save()
            
            UserActivityLog.objects.create(
                user=request.user,
                action='create',
                model_name='Tag',
                object_id=tag.id,
                description=f'Created tag: {tag.name}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'Tag "{tag.name}" created successfully!')
            return redirect('tags:list')
    else:
        form = TagForm()
    
    return render(request, 'tags/tag_create.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.can_manage_users)
def tag_edit(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    
    if request.method == 'POST':
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            tag = form.save()
            
            UserActivityLog.objects.create(
                user=request.user,
                action='update',
                model_name='Tag',
                object_id=tag.id,
                description=f'Updated tag: {tag.name}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'Tag "{tag.name}" updated successfully!')
            return redirect('tags:list')
    else:
        form = TagForm(instance=tag)
    
    return render(request, 'tags/tag_edit.html', {'form': form, 'tag': tag})

@login_required
@user_passes_test(lambda u: u.can_manage_users)
def tag_delete(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    
    if request.method == 'POST':
        name = tag.name
        tag.delete()
        
        UserActivityLog.objects.create(
            user=request.user,
            action='delete',
            model_name='Tag',
            object_id=tag_id,
            description=f'Deleted tag: {name}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, f'Tag "{name}" deleted successfully!')
        return redirect('tags:list')
    
    return render(request, 'tags/tag_delete.html', {'tag': tag})