# Generated by Django 5.1.7 on 2025-04-02 11:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0002_alter_learningmaterial_chapter_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='learningmaterial',
            name='chapter',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='materials', to='course.chapter'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='learningmaterial',
            name='title',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]
