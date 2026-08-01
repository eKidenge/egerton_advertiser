from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from .models import Category
from .forms import CategoryForm
from apps.articles.models import Article
from apps.accounts.models import UserActivityLog

def category_list(request):
    categories = Category.objects.filter(
        is_active=True,
        parent__isnull=True
    ).prefetch_related('children').order_by('order')
    
    # Update article counts
    for category in categories:
        category.update_article_count()
    
    context = {
        'categories': categories,
    }
    return render(request, 'categories/category_list.html', context)

def category_detail(request, slug):
    category = get_object_or_404(
        Category.objects.prefetch_related('children'),
        slug=slug,
        is_active=True
    )
    
    # Get articles in this category and subcategories
    category_ids = [category.id]
    for child in category.children.filter(is_active=True):
        category_ids.append(child.id)
    
    articles = Article.objects.filter(
        category__id__in=category_ids,
        status='published',
        published_at__lte=timezone.now()
    ).select_related('author').order_by('-published_at')
    
    # Pagination
    paginator = Paginator(articles, 20)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    # Get subcategories
    subcategories = category.children.filter(is_active=True)
    
    context = {
        'category': category,
        'articles': articles,
        'subcategories': subcategories,
        'article_count': articles.count(),
    }
    return render(request, 'categories/category_detail.html', context)

@login_required
@user_passes_test(lambda u: u.can_manage_users)
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            
            UserActivityLog.objects.create(
                user=request.user,
                action='create',
                model_name='Category',
                object_id=category.id,
                description=f'Created category: {category.name}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'Category "{category.name}" created successfully!')
            return redirect('categories:detail', slug=category.slug)
    else:
        form = CategoryForm()
    
    return render(request, 'categories/category_create.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.can_manage_users)
def category_edit(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            category = form.save()
            
            UserActivityLog.objects.create(
                user=request.user,
                action='update',
                model_name='Category',
                object_id=category.id,
                description=f'Updated category: {category.name}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'Category "{category.name}" updated successfully!')
            return redirect('categories:detail', slug=category.slug)
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'categories/category_edit.html', {'form': form, 'category': category})

@login_required
@user_passes_test(lambda u: u.can_manage_users)
def category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        name = category.name
        
        # Move articles to a default category or unset
        # This needs to be handled carefully
        category.delete()
        
        UserActivityLog.objects.create(
            user=request.user,
            action='delete',
            model_name='Category',
            object_id=category_id,
            description=f'Deleted category: {name}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, f'Category "{name}" deleted successfully!')
        return redirect('categories:list')
    
    return render(request, 'categories/category_delete.html', {'category': category})