from django.contrib.auth.models import Group, Permission
from django.dispatch import receiver
from django.db.models.signals import post_migrate
from django.contrib.contenttypes.models import ContentType
from .models import CustomUser

@receiver(post_migrate)
def create_user_groups(sender, **kwargs):
    # Create the groups if they don't already exist
    reader_group, _ = Group.objects.get_or_create(name='Reader')
    editor_group, _ = Group.objects.get_or_create(name='Editor')
    admin_group, _ = Group.objects.get_or_create(name='Admin')

    # Define permissions
    user_permissions = Permission.objects.filter(content_type=ContentType.objects.get_for_model(CustomUser))

    # Assign permissions to each group
    if not reader_group.permissions.exists():
        reader_group.permissions.set(user_permissions.filter(codename='view_customuser'))
    
    if not editor_group.permissions.exists():
        editor_group.permissions.set(user_permissions.filter(codename__in=['view_customuser', 'change_customuser']))

    if not admin_group.permissions.exists():
        admin_group.permissions.set(user_permissions)  # Full permissions
