# Generated by Django 4.2.6 on 2024-12-04 03:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0007_alter_book_cover_image_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='cover_image_url',
            field=models.URLField(blank=True, max_length=1200, null=True),
        ),
    ]
