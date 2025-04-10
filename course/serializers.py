from rest_framework import serializers
from .models import Class, Subject, Chapter, Lesson, Video, LearningMaterial, Question, LessonReview, QuestionOption


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
        fields = ['id', 'lesson_name', 'name',
                  'video_url', 'video_file', 'video_thumbnail', 'video_duration', 'created_at', 'updated_at']
        read_only_fields = [ 'created_at', 'updated_at']


class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ['id', 'option', 'is_correct', 'explanation']
        # Removed 'question' from fields since it will be nested


class QuestionSerializer(serializers.ModelSerializer):
    # Add nested serializer for options
    options = QuestionOptionSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'lesson', 'question_text', 'explanation', 'options']

    def create(self, validated_data):
        options_data = validated_data.pop('options')  # Extract options data
        question = Question.objects.create(**validated_data)  # Create question

        # Create options for the question
        for option_data in options_data:
            QuestionOption.objects.create(question=question, **option_data)

        return question

    def update(self, instance, validated_data):
        options_data = validated_data.pop('options', None)

        # Update question fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if options_data is not None:
            # Delete existing options
            instance.options.all().delete()
            # Create new options
            for option_data in options_data:
                QuestionOption.objects.create(question=instance, **option_data)

        return instance


class LearningMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningMaterial
        fields = ['id', 'lesson', 'title', 'file', 'material_type',
                  'description', 'game_url', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class LessonReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonReview
        fields = ['id', 'lesson', 'review_text',
                  'rating', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
