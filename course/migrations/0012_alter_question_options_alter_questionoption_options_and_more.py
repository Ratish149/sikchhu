# Generated by Django 5.1.7 on 2025-04-08 08:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0011_remove_question_answer_question_correct_option_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='questionoption',
            options={'ordering': ['id']},
        ),
        migrations.RemoveField(
            model_name='question',
            name='correct_option',
        ),
        migrations.AlterField(
            model_name='question',
            name='lesson',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='course.lesson'),
        ),
        migrations.AlterField(
            model_name='questionoption',
            name='explanation',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='questionoption',
            name='option',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='questionoption',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='course.question'),
        ),
    ]
