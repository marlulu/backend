# Generated by Django 3.2 on 2025-05-15 07:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0007_auto_20250515_1504'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='picture',
            name='study_group_name',
        ),
        migrations.AddField(
            model_name='picture',
            name='study_group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='apps.studygroup'),
        ),
    ]
