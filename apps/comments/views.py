from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Comment, CommentVote
from .forms import CommentForm, CommentModerationForm
from apps.articles.models import Article
from apps.accounts.models import UserActivityLog

@login_required
@require_http_methods(["POST"])
def add_comment(request, article_id):
    article = get_object_or_404(Article, id=article_id, status='published')
    
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.article = article
        comment.user = request.user
        comment.ip_address = request.META.get('REMOTE_ADDR')
        comment.user_agent = request.META.get('HTTP_USER_AGENT', '')
        comment.referer = request.META.get('HTTP_REFERER', '')
        comment.save()
        
        UserActivityLog.objects.create(
            user=request.user,
            action='comment',
            model_name='Comment',
            object_id=comment.id,
            description=f'Added comment on article: {article.title}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, 'Your comment has been submitted and is awaiting moderation.')
    else:
        messages.error(request, 'Please correct the errors below.')
    
    return redirect('articles:detail', slug=article.slug)

@login_required
@require_http_methods(["POST"])
def add_reply(request, comment_id):
    parent_comment = get_object_or_404(Comment, id=comment_id, status='approved')
    article = parent_comment.article
    
    form = CommentForm(request.POST)
    if form.is_valid():
        reply = form.save(commit=False)
        reply.article = article
        reply.user = request.user
        reply.parent = parent_comment
        reply.ip_address = request.META.get('REMOTE_ADDR')
        reply.user_agent = request.META.get('HTTP_USER_AGENT', '')
        reply.referer = request.META.get('HTTP_REFERER', '')
        reply.save()
        
        UserActivityLog.objects.create(
            user=request.user,
            action='comment',
            model_name='Comment',
            object_id=reply.id,
            description=f'Replied to comment on article: {article.title}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, 'Your reply has been submitted.')
    else:
        messages.error(request, 'Please correct the errors below.')
    
    return redirect('articles:detail', slug=article.slug)

@login_required
@user_passes_test(lambda u: u.can_moderate_comments)
def comment_list(request):
    comments = Comment.objects.all().select_related('user', 'article', 'parent').order_by('-created_at')
    
    # Filtering
    status = request.GET.get('status')
    if status:
        comments = comments.filter(status=status)
    
    article_id = request.GET.get('article')
    if article_id:
        comments = comments.filter(article_id=article_id)
    
    paginator = Paginator(comments, 50)
    page = request.GET.get('page')
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)
    
    context = {
        'comments': comments,
        'status_filter': status,
        'status_choices': Comment.STATUS_CHOICES,
    }
    return render(request, 'comments/comment_list.html', context)

def comment_detail(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    if comment.status != 'approved' and not request.user.can_moderate_comments:
        messages.error(request, 'You do not have permission to view this comment.')
        return redirect('articles:detail', slug=comment.article.slug)
    
    replies = comment.get_replies()
    
    context = {
        'comment': comment,
        'replies': replies,
    }
    return render(request, 'comments/comment_detail.html', context)

@login_required
@user_passes_test(lambda u: u.can_moderate_comments)
def pending_comments(request):
    comments = Comment.objects.filter(status='pending').select_related('user', 'article').order_by('-created_at')
    
    paginator = Paginator(comments, 30)
    page = request.GET.get('page')
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)
    
    return render(request, 'comments/pending_comments.html', {'comments': comments})

@login_required
@user_passes_test(lambda u: u.can_moderate_comments)
def approved_comments(request):
    comments = Comment.objects.filter(status='approved').select_related('user', 'article').order_by('-created_at')
    
    paginator = Paginator(comments, 30)
    page = request.GET.get('page')
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)
    
    return render(request, 'comments/approved_comments.html', {'comments': comments})

@login_required
@user_passes_test(lambda u: u.can_moderate_comments)
def spam_comments(request):
    comments = Comment.objects.filter(status='spam').select_related('user', 'article').order_by('-created_at')
    
    paginator = Paginator(comments, 30)
    page = request.GET.get('page')
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)
    
    return render(request, 'comments/spam_comments.html', {'comments': comments})

@login_required
@user_passes_test(lambda u: u.can_moderate_comments)
def comment_moderate(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.method == 'POST':
        form = CommentModerationForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            notes = form.cleaned_data.get('notes', '')
            
            if action == 'approve':
                comment.approve(request.user)
                messages.success(request, 'Comment approved successfully.')
            elif action == 'reject':
                comment.reject(request.user, notes)
                messages.success(request, 'Comment rejected.')
            elif action == 'spam':
                comment.mark_as_spam(request.user)
                messages.success(request, 'Comment marked as spam.')
            
            UserActivityLog.objects.create(
                user=request.user,
                action='update',
                model_name='Comment',
                object_id=comment.id,
                description=f'Moderated comment by {comment.user.username}: {action}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            return redirect('comments:pending')
    else:
        form = CommentModerationForm()
    
    return render(request, 'comments/comment_moderate.html', {'comment': comment, 'form': form})

@login_required
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    if not request.user.can_moderate_comments and comment.user != request.user:
        messages.error(request, 'You do not have permission to delete this comment.')
        return redirect('articles:detail', slug=comment.article.slug)
    
    if request.method == 'POST':
        article_slug = comment.article.slug
        comment.delete()
        
        messages.success(request, 'Comment deleted successfully.')
        return redirect('articles:detail', slug=article_slug)
    
    return render(request, 'comments/comment_delete.html', {'comment': comment})

@login_required
@require_http_methods(["POST"])
def vote_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    vote_type = request.POST.get('vote_type')
    
    if vote_type not in ['like', 'dislike']:
        return JsonResponse({'error': 'Invalid vote type'}, status=400)
    
    # Check if user already voted
    existing_vote = CommentVote.objects.filter(comment=comment, user=request.user).first()
    
    if existing_vote:
        if existing_vote.vote_type == vote_type:
            # Remove vote (toggle off)
            existing_vote.delete()
            if vote_type == 'like':
                comment.likes -= 1
            else:
                comment.dislikes -= 1
            comment.save()
            return JsonResponse({
                'success': True,
                'action': 'removed',
                'likes': comment.likes,
                'dislikes': comment.dislikes
            })
        else:
            # Change vote
            existing_vote.vote_type = vote_type
            existing_vote.save()
            if vote_type == 'like':
                comment.likes += 1
                comment.dislikes -= 1
            else:
                comment.likes -= 1
                comment.dislikes += 1
            comment.save()
            return JsonResponse({
                'success': True,
                'action': 'changed',
                'likes': comment.likes,
                'dislikes': comment.dislikes
            })
    else:
        # New vote
        CommentVote.objects.create(
            comment=comment,
            user=request.user,
            vote_type=vote_type
        )
        if vote_type == 'like':
            comment.likes += 1
        else:
            comment.dislikes += 1
        comment.save()
        
        return JsonResponse({
            'success': True,
            'action': 'added',
            'likes': comment.likes,
            'dislikes': comment.dislikes
        })