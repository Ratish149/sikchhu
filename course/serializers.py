from rest_framework import serializers
from .models import Class, Subject, Chapter, Lesson, Video, LearningMaterial, Answer, Question


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ['id', 'name', 'slug', 'icon',
                  'description', 'created_at', 'updated_at']
        read_only_fields = ['slug', 'created_at', 'updated_at']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'class_name', 'name', 'slug', 'icon',
                  'description', 'created_at', 'updated_at']
        read_only_fields = ['slug', 'created_at', 'updated_at']


class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['id', 'subject_name', 'name', 'slug',
                  'icon', 'description', 'created_at', 'updated_at']
        read_only_fields = ['slug', 'created_at', 'updated_at']


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'chapter_name', 'name', 'slug',
                  'icon', 'description', 'created_at', 'updated_at']
        read_only_fields = ['slug', 'created_at', 'updated_at']


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'lesson_name', 'name', 'slug',
                  'video_url', 'video_file', 'created_at', 'updated_at']
        read_only_fields = ['slug', 'created_at', 'updated_at']


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'answer_text', 'is_correct',
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class QuestionSerializer(serializers.ModelSerializer):
    answer = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'lesson', 'question_text',
                  'explanation', 'answer', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class LearningMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningMaterial
        fields = ['id', 'lesson', 'title', 'file', 'material_type',
                  'description', 'game_url', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
