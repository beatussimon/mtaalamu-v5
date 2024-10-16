from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages

from .forms import SignUpForm, LoginForm
from .models import CustomUser
from django.core.mail import send_mail
from django.contrib.auth.models import Group  # Ensure Group is imported for role assignment

from articles.models import Article, Category  # Importing models used in views


def signup(request):
    """Handle user signup, send activation email, and redirect to the verification waiting page."""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            role_name = form.cleaned_data['role']  # Get the selected role (as a string)

            try:
                # Create a Firebase user
                firebase_user = auth.create_user(
                    email=email,
                    password=password,
                    display_name=f"{first_name} {last_name}"
                )

                # Create the local Django user
                django_user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password
                )

                # Assign user to the selected group (role)
                role_group = Group.objects.get(name=role_name)  # Fetch the Group instance by name
                django_user.groups.add(role_group)  # Add user to the group

                # Send email verification link using Firebase
                confirmation_url = auth.generate_email_verification_link(email)

                send_mail(
                    'Verify your email',
                    f'Please click the link to verify your email: {confirmation_url}',
                    'no-reply@yourdomain.com',  # Replace with your actual sender email
                    [email],
                )

                messages.success(request, 'Please check your email for the activation link to verify your account.')
                return render(request, 'users/verification_waiting.html', {'email': email})

            except Exception as e:
                messages.error(request, f"Error creating account: {str(e)}")
                return redirect('users:signup')

    else:
        form = SignUpForm()

    return render(request, 'users/signup.html', {'form': form})


def confirm_email(request):
    """Confirm the email and log in the user."""
    email = request.GET.get('email')
    token = request.GET.get('token')

    if email and token:
        try:
            # Verify the token with Firebase
            decoded_token = auth.verify_id_token(token)
            if decoded_token['email'] == email:
                user = CustomUser.objects.get(email=email)  # Retrieve the Django user
                login(request, user)  # Log in the user
                messages.success(request, 'Email confirmed! You are now logged in.')
                return redirect('articles:article_list')  # Redirect to articles list
        except Exception as e:
            messages.error(request, f"Error confirming email: {str(e)}")
            return redirect('users:login')

    messages.error(request, "Invalid confirmation link.")
    return redirect('users:login')


def login_view(request):
    """Handle user login."""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome, {user.username}!")
                return redirect('articles:article_list')  # Redirect to articles list
            else:
                messages.error(request, 'Invalid username or password.')
                form.add_error(None, "Invalid username or password.")

    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('users:login')


def subcategory_articles(request, subcategory_name):
    """Retrieve articles by subcategory."""
    # Assuming that `subcategory` is a ForeignKey or ManyToMany relation in Article
    articles = Article.objects.filter(subcategory__name=subcategory_name)
    return render(request, 'articles/subcategory_articles.html', {'articles': articles})
