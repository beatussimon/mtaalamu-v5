from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

# User Authentication Tests (Signup and Login)
class UserAuthTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')

    def test_login_view(self):
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after login
        self.assertRedirects(response, reverse('articles:article_list'))  # Assuming login redirects to article list

    def test_signup_view(self):
        response = self.client.post(reverse('users:signup'), {
            'username': 'newuser',
            'password1': 'newpassword',
            'password2': 'newpassword'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after successful signup
        self.assertTrue(get_user_model().objects.filter(username='newuser').exists())
