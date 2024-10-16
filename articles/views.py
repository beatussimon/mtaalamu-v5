from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Article, Category, Subcategory, Comment, Subscription
from .forms import ArticleForm, CommentForm, SubscriptionForm
import logging
from django.http import JsonResponse
from django.core.paginator import Paginator,EmptyPage
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.http import require_POST
from django.db.models import Q 
from django.db import IntegrityError
from django.template.loader import render_to_string



logger = logging.getLogger(__name__)

def article_list(request):
    recently_added_threshold = timezone.now() - timedelta(days=7)
    all_articles = Article.objects.order_by('-created_at')

    # Get the 4 most recent articles added in the last 7 days
    recently_added_articles = all_articles.filter(created_at__gte=recently_added_threshold)[:4]

    # Exclude these 4 articles from the "Explore More" section
    other_articles = all_articles.exclude(id__in=recently_added_articles.values_list('id', flat=True))

    # Pagination for "Explore More" articles
    paginator = Paginator(other_articles, 8)  # 8 articles per page initially
    page_number = request.GET.get('page', 1)  # Default to page 1
    explore_more_articles = paginator.get_page(page_number)

    # Handle AJAX request for infinite scroll
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('articles/partials/article_list_partial.html', {
            'explore_more_articles': explore_more_articles,
        })
        return JsonResponse({
            'html': html,
            'has_next': explore_more_articles.has_next(),
        })

    return render(request, 'articles/article_list.html', {
        'recently_added_articles': recently_added_articles,
        'explore_more_articles': explore_more_articles,
        'paginator': paginator,
    })
    
def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    related_articles = Article.objects.filter(category=article.category).exclude(pk=pk)[:5]

    # Handle Comment Submission
    if request.method == 'POST' and 'comment_submit' in request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            parent_id = request.POST.get('parent_id')  # Get parent comment ID for replies
            parent = Comment.objects.get(id=parent_id) if parent_id else None
            comment = comment_form.save(commit=False)
            comment.article = article
            comment.author = request.user
            comment.parent = parent  # Set parent comment for replies
            comment.save()
            messages.success(request, 'Comment added successfully.')
            return redirect('articles:article_detail', pk=pk)
        else:
            messages.error(request, 'There was an error with your comment.')

    # Handle Comment Liking via AJAX
    if request.method == 'POST' and 'like_comment' in request.POST:
        comment_id = request.POST.get('comment_id')
        comment = Comment.objects.get(id=comment_id)
        if request.user in comment.likes.all():
            comment.likes.remove(request.user)  # Unlike the comment
        else:
            comment.likes.add(request.user)  # Like the comment
        return JsonResponse({'likes_count': comment.like_count()})  # Return updated like count

    comment_form = CommentForm()  # Empty form for new comment

    # Fetch articles
    recently_added_articles = Article.objects.order_by('-created_at')[:4]  # Latest 4 articles
    explore_more_articles = Article.objects.exclude(pk__in=recently_added_articles).order_by('-created_at')[:8]  # Next 8 articles
    other_articles = Article.objects.exclude(pk__in=recently_added_articles).exclude(pk__in=explore_more_articles).order_by('-created_at')

    # Pagination for comments
    comments_list = article.comments.filter(parent=None).order_by('-created_at')  # Only top-level comments
    paginator = Paginator(comments_list, 5)  # Show 5 comments per page
    page_number = request.GET.get('page')
    comments = paginator.get_page(page_number)

    context = {
        'article': article,
        'related_articles': related_articles,
        'comments': comments,
        'comment_form': comment_form,
        'recently_added_articles': recently_added_articles,
        'explore_more_articles': explore_more_articles,
        'other_articles': other_articles,  # This will be used for pagination
    }
    return render(request, 'articles/article_detail.html', context)


@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Ensure that only the author can edit their comment
    if request.user != comment.author:
        messages.error(request, "You are not allowed to edit this comment.")
        return redirect('articles:article_detail', pk=comment.article.pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Comment updated successfully.')
            return redirect('articles:article_detail', pk=comment.article.pk)
        else:
            messages.error(request, 'There was an error updating your comment.')

    else:
        form = CommentForm(instance=comment)

    return render(request, 'articles/edit_comment.html', {'form': form, 'comment': comment})

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user == comment.author or request.user.is_superuser:
        comment.delete()
        messages.success(request, 'Comment deleted successfully.')
    else:
        messages.error(request, "You are not allowed to delete this comment.")
    return redirect('articles:article_detail', pk=comment.article.id)

@login_required
def reply_comment(request, comment_id):
    parent_comment = get_object_or_404(Comment, pk=comment_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.parent = parent_comment  # Set the parent comment
            reply.author = request.user  # Set the author to the current user
            reply.article = parent_comment.article  # Ensure the reply is associated with the correct article
            reply.save()
            messages.success(request, 'Reply added successfully.')
            return redirect('articles:article_detail', pk=parent_comment.article.id)
        else:
            messages.error(request, 'There was an error with your reply.')

    return redirect('articles:article_detail', pk=parent_comment.article.id)

@login_required
def like_comment(request, comment_id):
    logger = logging.getLogger(__name__)

    try:
        if request.method == 'POST':
            comment = get_object_or_404(Comment, id=comment_id)

            # Toggle like status
            if request.user in comment.likes.all():
                comment.likes.remove(request.user)  # Unlike the comment
            else:
                comment.likes.add(request.user)  # Like the comment

            return JsonResponse({'new_like_count': comment.like_count()})
    except Exception as e:
        logger.error(f"Error liking comment {comment_id}: {e}")
        return JsonResponse({'error': 'An error occurred.'}, status=500)

@login_required
def like_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.user in article.likes.all():
        article.likes.remove(request.user)
        messages.success(request, 'You unliked the article.')
    else:
        article.likes.add(request.user)
        messages.success(request, 'You liked the article.')
    return redirect('articles:article_detail', pk=pk)

@login_required
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, 'Article created successfully.')
            return redirect('articles:article_list')
        else:
            messages.error(request, 'There was an error in the form. Please correct it.')
    else:
        form = ArticleForm()

    return render(request, 'articles/article_form.html', {
        'form': form,
        'categories': Category.objects.prefetch_related('subcategories'),
    })

@login_required
def article_edit(request, pk):
    article = get_object_or_404(Article, pk=pk)

    if request.user != article.author and not request.user.is_superuser:
        messages.error(request, "You don't have permission to edit this article.")
        return redirect('articles:article_list')

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, 'Article updated successfully.')
            return redirect('articles:article_detail', pk=article.pk)
        else:
            messages.error(request, 'There was an error in the form. Please correct it.')
    else:
        form = ArticleForm(instance=article)

    return render(request, 'articles/article_form.html', {
        'form': form,
        'categories': Category.objects.prefetch_related('subcategories'),
        'article': article,
    })

@login_required
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)

    if request.user != article.author and not request.user.is_superuser:
        messages.error(request, "You don't have permission to delete this article.")
        return redirect('articles:article_detail', pk=pk)

    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Article deleted successfully.')
        return redirect('articles:article_list')

    return render(request, 'articles/article_confirm_delete.html', {'article': article})

@login_required
def profile(request):
    user_role = getattr(request.user, 'role', 'Not defined')
    phone_number = getattr(request.user, 'phone_number', 'Not provided')

    return render(request, 'articles/profile.html', {
        'user': request.user,
        'user_role': user_role,
        'phone_number': phone_number,
    })

def subscribe(request, article_id):
    article = get_object_or_404(Article, id=article_id)  # Retrieve the specific article
    categories = Category.objects.all()  # Get all categories for the form

    if request.method == 'POST':
        email = request.POST.get('email')
        category_id = request.POST.get('category')  # Get selected category

        # Check if a subscription with this email already exists
        if Subscription.objects.filter(email=email).exists():
            return render(request, 'articles/article_detail.html', {
                'error': 'This email is already subscribed to the newsletter.',
                'article': article,  # Pass article to context
                'categories': categories,
            })

        # If the email is not already subscribed, create a new subscription
        try:
            subscription = Subscription.objects.create(
                user=request.user,
                email=email,
                category_id=category_id  # Link the selected category
            )
            subscription.save()
            return redirect('articles:subscription_success')  # Redirect to success page
        except IntegrityError:
            return render(request, 'articles/article_detail.html', {
                'error': 'There was an error processing your subscription. Please try again.',
                'article': article,  # Pass article to context
                'categories': categories,
            })

    # Render article detail if not a POST request
    return render(request, 'articles/article_detail.html', {
        'article': article,  # Ensure article is passed to context
        'categories': categories,
    })

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

def search_articles(request):
    query = request.GET.get('q', '')
    article_list = Article.objects.filter(title__icontains=query).order_by('-created_at')  # Order by created_at descending

    # Paginate results
    paginator = Paginator(article_list, 8)  # Show 8 articles per page
    page = request.GET.get('page', 1)  # Default to page 1

    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        # If the page is not an integer, deliver the first page.
        articles = paginator.page(1)
    except EmptyPage:
        # If the page is out of range (e.g. 9999), deliver the last page of results.
        articles = paginator.page(paginator.num_pages)

    context = {
        'articles': articles,
        'query': query,
        'page_obj': articles,  # Needed for pagination controls in the template
    }

    return render(request, 'articles/search_results.html', context)


def subscription_success(request):
    return render(request, 'articles/subscription_success.html')

def fetch_subcategories(request):
    category_id = request.GET.get('category_id')
    subcategories = Subcategory.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse({'subcategories': list(subcategories)})

def category_articles(request, category_name):
    # Fetch the category based on the name; this will also raise a 404 if it doesn't exist
    category = get_object_or_404(Category, name=category_name)
    
    # Filter articles that belong to the specified category
    articles = Article.objects.filter(category=category)  # Ensure that 'category' is the field in your Article model

    # Pass both the category and the articles to the template
    return render(request, 'articles/category_articles.html', {
        'category': category,
        'articles': articles
    })


# View to handle fetching subcategories based on a category
def get_subcategories(request, category_name):
    category = get_object_or_404(Category, name=category_name)
    subcategories = category.subcategories.all()
    return render(request, 'articles/subcategories.html', {'category': category, 'subcategories': subcategories})

# View to handle displaying articles for a specific subcategory
def subcategory_articles(request, subcategory_name):
    subcategory = get_object_or_404(Subcategory, name=subcategory_name)
    articles = Article.objects.filter(subcategory=subcategory)
    return render(request, 'articles/subcategory_articles.html', {'subcategory': subcategory, 'articles': articles})


def about(request):
    return render(request, 'articles/about.html')

def contact(request):
    return render(request, 'articles/contact.html')