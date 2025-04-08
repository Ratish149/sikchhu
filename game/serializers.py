from rest_framework import serializers
from .models import Background, Frame, GameObject, Dialogue, Quiz, QuizOption, UserProgress


class BackgroundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Background
        fields = ['id', 'name', 'image', 'description']


class QuizOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizOption
        fields = ['id', 'text', 'is_correct', 'explanation',
                  'height', 'width', 'position_x', 'position_y']


class GameObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameObject
        fields = ['id', 'frame', 'name', 'image']


class DialogueSerializer(serializers.ModelSerializer):
    game_object = GameObjectSerializer(read_only=True)

    class Meta:
        model = Dialogue
        fields = ['id', 'frame', 'game_object', 'text']


class QuizSerializer(serializers.ModelSerializer):
    options = QuizOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'frame', 'question', 'options',
                  'height', 'width', 'position_x', 'position_y']


class FrameSerializer(serializers.ModelSerializer):
    objects = GameObjectSerializer(many=True, read_only=True)
    dialogues = DialogueSerializer(many=True, read_only=True)
    quiz = QuizSerializer(read_only=True)

    class Meta:
        model = Frame
        fields = ['id', 'lesson', 'name', 'frame_type', 'background',
                  'previous_frame', 'objects', 'dialogues', 'quiz']


class UserProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProgress
        fields = ['id', 'user', 'lesson', 'current_frame',
                  'completed_frames', 'score', 'last_interaction']
        read_only_fields = ['last_interaction']
