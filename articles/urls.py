from django.urls import path
from .views import (
    article_list,
    article_detail,
    article_create,
    article_edit,
    article_delete,
    like_article,
    category_articles,
    get_subcategories,
    subcategory_articles,
    profile,
    subscribe,
    search_articles,
    delete_comment,
    edit_comment,
    like_comment,
    reply_comment,
    subscription_success,
    fetch_subcategories,
    about,
    contact
)

app_name = 'articles'

urlpatterns = [
    path('', article_list, name='article_list'),
    path('article/<int:pk>/', article_detail, name='article_detail'),
    path('article/<int:pk>/like/', like_article, name='like_article'),
    path('create/', article_create, name='article_create'),
    path('edit/<int:pk>/', article_edit, name='article_edit'),
    path('delete/<int:pk>/', article_delete, name='article_delete'),
    path('categories/<str:category_name>/', category_articles, name='category_articles'),
    path('subcategories/<int:category_id>/', get_subcategories, name='get_subcategories'),
    path('subcategories/<str:subcategory_name>/', subcategory_articles, name='subcategory_articles'),
    path('profile/', profile, name='profile'),
    # Update this line to include <int:article_id> parameter
    path('subscribe/<int:article_id>/', subscribe, name='subscribe'),
    path('search/', search_articles, name='search_articles'),
    path('comment/delete/<int:comment_id>/', delete_comment, name='delete_comment'),
    path('comment/edit/<int:comment_id>/', edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/like/', like_comment, name='like_comment'),
    path('comment/<int:comment_id>/reply/', reply_comment, name='reply_comment'),
    path('subscribe/success/', subscription_success, name='subscription_success'),
    path('fetch-subcategories/', fetch_subcategories, name='fetch_subcategories'),
        path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
]
