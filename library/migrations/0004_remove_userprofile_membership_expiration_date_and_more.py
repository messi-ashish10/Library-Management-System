# Generated by Django 4.2.6 on 2024-11-27 01:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0003_book_authors'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='membership_expiration_date',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='membership_start_date',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='role',
        ),
        migrations.DeleteModel(
            name='Membership',
        ),
        migrations.DeleteModel(
            name='MembershipType',
        ),
    ]