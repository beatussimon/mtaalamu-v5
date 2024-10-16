from django.urls import path
from .views import signup, login_view, logout_view, confirm_email

app_name = 'users'

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('confirm_email/', confirm_email, name='confirm_email'),  # Email confirmation
]
