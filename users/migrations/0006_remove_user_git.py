# Generated by Django 4.0.4 on 2023-12-21 08:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_user_git'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='git',
        ),
    ]
