# Generated by Django 3.2 on 2025-05-20 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0019_auto_20250521_0117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotation',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='picture',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='pictureslices',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
