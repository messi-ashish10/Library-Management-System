# Generated by Django 4.2.6 on 2024-12-03 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0004_remove_userprofile_membership_expiration_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='borrowinghistory',
            name='returned_date',
            field=models.DateField(default='2024-12-03'),
            preserve_default=False,
        ),
    ]
