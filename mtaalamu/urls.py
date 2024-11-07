from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('articles.urls')),  # Assuming articles URLs are included here
    path('users/', include('users.urls')),  # Assuming users URLs are included here

    # Add the following line for the login view
    path('accounts/login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
