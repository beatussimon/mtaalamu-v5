from django.contrib import admin
from .models import Article, Category, Subcategory, Subscription

admin.site.register(Article)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Subscription)