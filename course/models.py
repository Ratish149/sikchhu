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


class Lesson(models.Model):
    chapter_name = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
    icon = models.FileField(upload_to='lesson_icons/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Video(models.Model):
    lesson_name = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    video_url = models.URLField(null=True, blank=True)
    video_file = models.FileField(
        upload_to='video_files/', null=True, blank=True)
    video_thumbnail = models.FileField(
        upload_to='video_thumbnails/', null=True, blank=True)
    video_duration = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class LearningMaterial(models.Model):
    CHOICES = [
        ('Syllabus', 'Syllabus'),
        ('Notes', 'Notes'),
        ('Old Question', 'Old Question'),
        ('Gamefication', 'Gamefication'),
    ]
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="materials", null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    file = models.FileField(upload_to="materials/", null=True, blank=True)
    material_type = models.CharField(
        max_length=255, choices=CHOICES, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    game_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title if self.title else f"Learning Material {self.id} - {self.material_type}"


class Question(models.Model):
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    question_text = models.CharField(max_length=255)
    explanation = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question_text[:50] + "..." if len(self.question_text) > 50 else self.question_text

    class Meta:
        ordering = ['-created_at']


class QuestionOption(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='options'
    )
    option = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    explanation = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Option: {self.option} ({'Correct' if self.is_correct else 'Wrong'})"

    class Meta:
        ordering = ['id']


class LessonReview(models.Model):
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    review_text = models.TextField(null=True, blank=True)
    rating = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review for {self.lesson.name}"
