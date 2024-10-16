from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Article, Category
from .forms import ArticleForm

# Model Test for Article
class ArticleModelTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.article = Article.objects.create(
            title="Test Article",
            content="This is a test article.",
            author=self.user,
            category=self.category
        )

    def test_article_creation(self):
        self.assertEqual(self.article.title, "Test Article")
        self.assertEqual(self.article.content, "This is a test article.")
        self.assertEqual(self.article.author.username, "testuser")
        self.assertTrue(self.article.created_at)

    def test_article_str_representation(self):
        self.assertEqual(str(self.article), "Test Article")


# View Tests for Article
class ArticleViewTests(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.article = Article.objects.create(
            title="Test Article",
            content="This is a test article.",
            author=self.user,
            category=self.category
        )

    def test_article_list_view(self):
        response = self.client.get(reverse('articles:article_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Article")
        self.assertTemplateUsed(response, 'articles/article_list.html')

    def test_article_detail_view(self):
        response = self.client.get(reverse('articles:article_detail', args=[self.article.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This is a test article.")
        self.assertTemplateUsed(response, 'articles/article_detail.html')

    def test_article_create_view(self):
        response = self.client.post(reverse('articles:article_create'), {
            'title': 'New Article',
            'content': 'This is a new test article.',
            'category': self.category.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Article.objects.filter(title="New Article").exists())


# Form Tests for Article
class ArticleFormTest(TestCase):

    def test_valid_form(self):
        category = Category.objects.create(name="Test Category")
        form_data = {
            'title': 'Valid Title',
            'content': 'Valid content for the article.',
            'category': category.id
        }
        form = ArticleForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        category = Category.objects.create(name="Test Category")
        form_data = {
            'title': '',
            'content': 'Valid content',
            'category': category.id
        }
        form = ArticleForm(data=form_data)
        self.assertFalse(form.is_valid())
