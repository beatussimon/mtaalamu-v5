# Generated by Django 5.0.8 on 2024-09-20 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='youtube_link',
            field=models.URLField(blank=True, null=True),
        ),
    ]
