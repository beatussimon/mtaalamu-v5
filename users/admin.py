from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import CustomUser
from .forms import SignUpForm

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = SignUpForm  # Form for creating a new user
    form = SignUpForm  # Form for editing an existing user

    # Fields displayed in the list view of users
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'is_staff')

    # Fields to show when editing a user in the admin
    fieldsets = (
        *UserAdmin.fieldsets,  # Unpack the original UserAdmin fieldsets
        (None, {'fields': ('phone_number', 'role')}),  # Add phone_number and role for editing
    )

    # Fields to show when adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'phone_number', 'role', 'password1', 'password2', 'groups'),
        }),
    )

    # Make sure that the groups field is editable in the user admin
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None:  # if adding a new user
            form.base_fields['groups'].queryset = Group.objects.all()  # Include all groups for new users
        return form

# Register the custom user model with the admin site
admin.site.register(CustomUser, CustomUserAdmin)
