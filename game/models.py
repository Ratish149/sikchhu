from django.db import models
from course.models import Chapter


class Background(models.Model):
    """Reusable backgrounds for frames"""
    name = models.CharField(max_length=255)
    image = models.FileField(
        upload_to='game_backgrounds/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Frame(models.Model):
    FRAME_TYPES = [
        ('background', 'Background Only'),
        ('scene', 'Background with Objects and Text'),
        ('quiz', 'Quiz Frame'),
    ]
    chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE, related_name='frames', blank=True, null=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    frame_type = models.CharField(
        max_length=20, choices=FRAME_TYPES, default='background')
    background = models.ForeignKey(
        Background,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='frames'
    )

    previous_frame = models.OneToOneField(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='next_frame_relation'
    )

    def __str__(self):
        return f"Chapter {self.chapter.name} - Frame {self.id} - {self.get_frame_type_display()}"

    def get_next_frame(self):
        return self.next_frame if hasattr(self, 'next_frame') else None


class GameObject(models.Model):
    """Objects in the frame (e.g., a tree, a character, an apple)"""
    frame = models.ForeignKey(
        Frame, on_delete=models.CASCADE, related_name='objects')
    name = models.CharField(
        max_length=255, help_text="Name of the object (e.g., Newton, Apple, Tree)")
    image = models.FileField(upload_to='game_objects/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} in Frame {self.frame.id}"


class Dialogue(models.Model):
    """Links objects to dialogues (who says what)"""
    frame = models.ForeignKey(
        Frame, on_delete=models.CASCADE, related_name='dialogues')
    game_object = models.ForeignKey(
        GameObject, on_delete=models.CASCADE, related_name='dialogues', help_text="Who speaks this text")
    text = models.TextField(help_text="Dialogue text spoken by the object")

    def __str__(self):
        return f"{self.game_object.name} says: {self.text[:30]}..."


class Quiz(models.Model):
    """Quiz linked to a frame"""
    frame = models.OneToOneField(
        Frame, on_delete=models.CASCADE, related_name='quiz')
    question = models.TextField(help_text="Quiz question")
    options = models.ManyToManyField(
        'QuizOption', related_name='quizzes', blank=True)

    def __str__(self):
        return f"Quiz in Frame {self.frame.id}: {self.question[:30]}..."


class QuizOption(models.Model):
    text = models.CharField(max_length=255, help_text="Option text")
    is_correct = models.BooleanField(
        default=False, help_text="Is this the correct answer?")
    explanation = models.TextField(
        help_text="Explanation for the answer", blank=True, null=True)

    def __str__(self):
        return f"Option for Quiz {self.quiz.id}: {self.text} ({'Correct' if self.is_correct else 'Wrong'})"
