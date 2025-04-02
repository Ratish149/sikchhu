from django.db import models
from django.utils.text import slugify
# Create your models here.


class Class(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
    icon = models.FileField(upload_to='class_icons/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Subject(models.Model):
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
    icon = models.FileField(upload_to='subject_icons/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Chapter(models.Model):
    subject_name = models.ForeignKey(Subject, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
    icon = models.FileField(upload_to='chapter_icons/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Video(models.Model):
    chapter_name = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)
    video_file = models.FileField(
        upload_to='video_files/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class LearningMaterial(models.Model):
    CHOICES = [
        ('Syllabus', 'Syllabus'),
        ('Notes', 'Notes'),
        ('Old Question', 'Old Question'),
        ('Gamefication', 'Gamefication'),
    ]
    chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE, related_name="materials")
    title = models.CharField(max_length=255, null=True, blank=True)
    file = models.FileField(upload_to="materials/", null=True, blank=True)
    material_type = models.CharField(max_length=255, choices=CHOICES)
    description = models.TextField(null=True, blank=True)
    game_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title if self.title else f"Learning Material {self.id} - {self.material_type}"


class Answer(models.Model):
    answer_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.answer_text[:50] + "..." if len(self.answer_text) > 50 else self.answer_text


class Question(models.Model):
    chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE, related_name='questions')
    question_text = models.CharField(max_length=255)
    explanation = models.TextField(null=True, blank=True)
    answer = models.ManyToManyField(Answer, related_name='questions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question_text[:50] + "..." if len(self.question_text) > 50 else self.question_text
