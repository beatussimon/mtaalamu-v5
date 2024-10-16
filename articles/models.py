from django.db import models
from django.conf import settings  # Import settings to use the custom user model
import re
from django.core.validators import EmailValidator
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Subcategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.category.name} - {self.name}'

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Use the custom user model
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='articles/images/', blank=True, null=True)
    youtube_link = models.URLField(blank=True, null=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_articles', blank=True)

    class Meta:
        permissions = [
            ('can_publish', 'Can Publish Articles'),
            ('can_edit', 'Can Edit Articles'),
            ('can_read', 'Can Read Articles'),
        ]

    def __str__(self):
        return self.title

    def extract_youtube_link(self, content):
        youtube_regex = r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.?be/)([a-zA-Z0-9_-]{11})'
        match = re.search(youtube_regex, content)
        if match:
            return match.group(0)
        return None

    def save(self, *args, **kwargs):
        self.youtube_link = self.extract_youtube_link(self.content)
        super().save(*args, **kwargs)

class Comment(models.Model):
    article = models.ForeignKey('Article', related_name='comments', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(max_length=500)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_comments', blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)  # Ensure this line is present

    def __str__(self):
        return f'Comment by {self.author} on {self.article.title}'

    def is_parent(self):
        return self.parent is None

    def can_edit(self, user):
        return self.author == user
    
    @property
    def like_count(self):
        return self.likes.count()
    
class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)  # Allow null for unauthenticated users
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE)  # Make nullable
    subcategory = models.ForeignKey(Subcategory, null=True, blank=True, on_delete=models.CASCADE)
    date_subscribed = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(validators=[EmailValidator()], unique=True, default='no-reply@example.com')

    def __str__(self):
        category_name = self.category.name if self.category else 'No category'
        return f'{self.email} subscribed to {category_name} on {self.date_subscribed}'
