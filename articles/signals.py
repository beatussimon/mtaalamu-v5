from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def create_user_groups(sender, **kwargs):
    if sender.name == 'articles':  # Ensure this only runs for the articles app
        Group.objects.get_or_create(name='Readers')
        Group.objects.get_or_create(name='Editors')
        Group.objects.get_or_create(name='Admins')
