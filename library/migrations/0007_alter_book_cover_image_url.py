# Generated by Django 4.2.6 on 2024-12-04 03:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0006_remove_borrowinghistory_return_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='cover_image_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]
