# Generated by Django 3.2 on 2025-05-20 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0016_auto_20250518_1246'),
    ]

    operations = [
        migrations.AddField(
            model_name='annotation',
            name='auto',
            field=models.IntegerField(default=0),
        ),
    ]
