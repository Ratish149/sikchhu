# Generated by Django 5.1.7 on 2025-04-02 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_frame_chapter'),
    ]

    operations = [
        migrations.AddField(
            model_name='frame',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
