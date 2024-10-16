from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver    

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        # Ensure it returns a meaningful string representation
        return self.get_full_name() or self.username or "Unnamed User"

# Assign default group to new users
@receiver(post_save, sender=CustomUser)
def assign_default_role(sender, instance, created, **kwargs):
    if created:
        # Create or get the default group
        default_group, _ = Group.objects.get_or_create(name='default_group')  # Replace 'default_group' with your actual group name
        # Add the user to the default group
        instance.groups.add(default_group)
