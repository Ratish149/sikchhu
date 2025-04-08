from django.shortcuts import render
from rest_framework import status, generics, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from .models import Background, Frame, GameObject, Dialogue, Quiz, QuizOption, UserProgress
from .serializers import (
    BackgroundSerializer, FrameSerializer, GameObjectSerializer,
    DialogueSerializer, QuizSerializer, QuizOptionSerializer, UserProgressSerializer
)
import json


class BackgroundListCreateView(generics.ListCreateAPIView):
    queryset = Background.objects.all()
    serializer_class = BackgroundSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def create(self, request, *args, **kwargs):
        try:
            name = request.data.get('name')
            image = request.FILES.get('image', None)
            description = request.data.get('description', '')

            if not name:
                return Response({'error': 'Name is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Create a new background instance
            background = Background.objects.create(
                name=name,
                image=image,
                description=description
            )

            # Build the image URL if it exists
            image_url = None
            if background.image and hasattr(background.image, 'url'):
                image_url = request.build_absolute_uri(background.image.url)

            # Return the created object data
            return Response({
                'id': background.id,
                'name': background.name,
                'image': image_url,
                'description': background.description,
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BackgroundRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Background.objects.all()
    serializer_class = BackgroundSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def retrieve(self, request, *args, **kwargs):
        try:
            background = self.get_object()

            # Build the image URL if it exists
            image_url = None
            if background.image and hasattr(background.image, 'url'):
                image_url = request.build_absolute_uri(background.image.url)

            # Return the background data
            return Response({
                'id': background.id,
                'name': background.name,
                'image': image_url,
                'description': background.description,
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            background = self.get_object()

            # Get data from request
            name = request.data.get('name')
            description = request.data.get('description')
            image = request.FILES.get('image')

            # Update fields if provided
            if name is not None:
                background.name = name
            if description is not None:
                background.description = description
            if image is not None:
                background.image = image
            elif 'image' in request.data and not image:
                # Handle removing image if empty value provided
                background.image = None

            background.save()

            # Build the image URL if it exists
            image_url = None
            if background.image and hasattr(background.image, 'url'):
                image_url = request.build_absolute_uri(background.image.url)

            # Return updated data
            return Response({
                'id': background.id,
                'name': background.name,
                'image': image_url,
                'description': background.description,
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            background = self.get_object()
            background.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FrameListCreateView(generics.ListCreateAPIView):
    serializer_class = FrameSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def create(self, request, *args, **kwargs):
        try:
            # Extract frame data
            lesson_id = request.data.get('lesson')
            name = request.data.get('name', '')
            frame_type = request.data.get('frame_type', 'background')
            background_id = request.data.get('background')
            previous_frame_id = request.data.get('previous_frame')
            color = request.data.get('color')
            height = request.data.get('height', 100)
            width = request.data.get('width', 100)
            order = request.data.get('order', 0)

            # Handle related data
            objects_data = []
            quiz_data = None

            # Parse objects data from request (objects now include their dialogues)
            if isinstance(request.data.get('objects'), list):
                objects_data = request.data.get('objects')
            elif hasattr(request.data, 'getlist') and request.data.get('objects'):
                try:
                    objects_data = json.loads(request.data.get('objects'))
                except json.JSONDecodeError:
                    return Response(
                        {"error": "Invalid objects format"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Parse quiz data from request
            if isinstance(request.data.get('quiz'), dict):
                quiz_data = request.data.get('quiz')
            elif hasattr(request.data, 'getlist') and request.data.get('quiz'):
                try:
                    quiz_data = json.loads(request.data.get('quiz'))
                except json.JSONDecodeError:
                    return Response(
                        {"error": "Invalid quiz format"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Create the frame instance
            frame = Frame()

            # Set lesson if provided
            if lesson_id:
                from course.models import Lesson
                try:
                    lesson = Lesson.objects.get(id=lesson_id)
                    frame.lesson = lesson
                except Lesson.DoesNotExist:
                    return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)

            # Set name and frame type
            frame.name = name
            frame.frame_type = frame_type

            # Set dimensions, color and order
            if color:
                frame.color = color
            frame.height = height
            frame.width = width
            frame.order = order

            # Set background if provided
            if background_id:
                try:
                    background = Background.objects.get(id=background_id)
                    frame.background = background
                except Background.DoesNotExist:
                    return Response({'error': 'Background not found'}, status=status.HTTP_404_NOT_FOUND)

            # Set previous frame if provided
            if previous_frame_id:
                try:
                    previous_frame = Frame.objects.get(id=previous_frame_id)
                    frame.previous_frame = previous_frame
                except Frame.DoesNotExist:
                    return Response({'error': 'Previous frame not found'}, status=status.HTTP_404_NOT_FOUND)

            # Save the frame
            frame.save()

            # Process objects and their dialogues
            created_objects = []
            for object_data in objects_data:
                name = object_data.get('name')
                image = request.FILES.get(f"object_image_{name}", None)
                dialogues = object_data.get('dialogues', [])

                if name:
                    # Create the game object
                    obj = GameObject.objects.create(
                        frame=frame,
                        name=name,
                        image=image
                    )

                    image_url = None
                    if obj.image and hasattr(obj.image, 'url'):
                        image_url = request.build_absolute_uri(obj.image.url)

                    # Process dialogues for this object
                    obj_dialogues = []
                    for dialogue_text in dialogues:
                        if dialogue_text:
                            dialogue = Dialogue.objects.create(
                                frame=frame,
                                game_object=obj,
                                text=dialogue_text
                            )
                            obj_dialogues.append({
                                'id': dialogue.id,
                                'text': dialogue.text
                            })

                    created_objects.append({
                        'id': obj.id,
                        'name': obj.name,
                        'image': image_url,
                        'dialogues': obj_dialogues
                    })

            # Process quiz if frame_type is 'quiz'
            created_quiz = None
            if frame.frame_type == 'quiz' and quiz_data:
                question_text = quiz_data.get('question')
                options_data = quiz_data.get('options', [])

                if question_text:
                    quiz = Quiz.objects.create(
                        frame=frame,
                        question=question_text
                    )

                    # Process quiz options
                    created_options = []
                    for option_data in options_data:
                        option_text = option_data.get('text')
                        is_correct = option_data.get('is_correct', False)
                        explanation = option_data.get('explanation', '')

                        if option_text:
                            quiz_option = QuizOption.objects.create(
                                text=option_text,
                                is_correct=is_correct,
                                explanation=explanation
                            )
                            quiz.options.add(quiz_option)

                            created_options.append({
                                'id': quiz_option.id,
                                'text': quiz_option.text,
                                'is_correct': quiz_option.is_correct,
                                'explanation': quiz_option.explanation
                            })

                    created_quiz = {
                        'id': quiz.id,
                        'question': quiz.question,
                        'options': created_options
                    }

            # Prepare the response
            response_data = {
                'id': frame.id,
                'lesson': frame.lesson.id if frame.lesson else None,
                'name': frame.name,
                'frame_type': frame.frame_type,
                'background': frame.background.id if frame.background else None,
                'previous_frame': frame.previous_frame.id if frame.previous_frame else None,
                'objects': created_objects,
                'quiz': created_quiz
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_queryset(self):
        queryset = Frame.objects.all()  # Initialize the base queryset first
        lesson_slug = self.request.query_params.get('lesson', None)
        order = self.request.query_params.get('order', None)
        frame_type = self.request.query_params.get('frame_type', None)

        if lesson_slug:
            queryset = queryset.filter(lesson__slug=lesson_slug)
        if frame_type:
            queryset = queryset.filter(frame_type=frame_type)
        if lesson_slug and order:
            queryset = queryset.filter(lesson__slug=lesson_slug, order=order)
        return queryset


class FrameRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Frame.objects.all()
    serializer_class = FrameSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def retrieve(self, request, *args, **kwargs):
        try:
            frame = self.get_object()

            # Get game objects with their dialogues
            objects_data = []
            for obj in frame.game_objects.all():
                image_url = None
                if obj.image and hasattr(obj.image, 'url'):
                    image_url = request.build_absolute_uri(obj.image.url)

                # Get dialogues for this object
                obj_dialogues = []
                for dialogue in obj.dialogues.all():
                    obj_dialogues.append({
                        'id': dialogue.id,
                        'text': dialogue.text,
                        'height': dialogue.height,
                        'width': dialogue.width,
                        'position_x': dialogue.position_x,
                        'position_y': dialogue.position_y
                    })

                objects_data.append({
                    'id': obj.id,
                    'name': obj.name,
                    'image': image_url,
                    'position_x': obj.position_x,
                    'position_y': obj.position_y,
                    'animation': obj.animation,
                    'animation_speed': obj.animation_speed,
                    'animation_direction': obj.animation_direction,
                    'dialogues': obj_dialogues
                })

            # Get quiz data if exists
            quiz_data = None
            if hasattr(frame, 'quiz'):
                quiz = frame.quiz
                options_data = []
                for option in quiz.options.all():
                    options_data.append({
                        'id': option.id,
                        'text': option.text,
                        'is_correct': option.is_correct,
                        'explanation': option.explanation,
                        'height': option.height,
                        'width': option.width,
                        'position_x': option.position_x,
                        'position_y': option.position_y
                    })

                quiz_data = {
                    'id': quiz.id,
                    'question': quiz.question,
                    'options': options_data,
                    'height': quiz.height,
                    'width': quiz.width,
                    'position_x': quiz.position_x,
                    'position_y': quiz.position_y
                }

            # Build the response
            response_data = {
                'id': frame.id,
                'lesson': frame.lesson.id if frame.lesson else None,
                'name': frame.name,
                'frame_type': frame.frame_type,
                'background': frame.background.id if frame.background else None,
                'color': frame.color,
                'height': frame.height,
                'width': frame.width,
                'order': frame.order,
                'previous_frame': frame.previous_frame.id if frame.previous_frame else None,
                'next_frame': frame.get_next_frame().id if frame.get_next_frame() else None,
                'objects': objects_data,
                'quiz': quiz_data
            }

            return Response(response_data)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            frame = self.get_object()

            # Extract frame data
            lesson_id = request.data.get('lesson')
            name = request.data.get('name')
            frame_type = request.data.get('frame_type')
            background_id = request.data.get('background')
            previous_frame_id = request.data.get('previous_frame')
            color = request.data.get('color')
            height = request.data.get('height')
            width = request.data.get('width')
            order = request.data.get('order')

            # Update frame fields if provided
            if lesson_id is not None:
                from course.models import Lesson
                try:
                    lesson = Lesson.objects.get(id=lesson_id)
                    frame.lesson = lesson
                except Lesson.DoesNotExist:
                    return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)

            if name is not None:
                frame.name = name

            if frame_type is not None:
                frame.frame_type = frame_type

            if background_id is not None:
                try:
                    background = Background.objects.get(id=background_id)
                    frame.background = background
                except Background.DoesNotExist:
                    return Response({'error': 'Background not found'}, status=status.HTTP_404_NOT_FOUND)

            if previous_frame_id is not None:
                try:
                    previous_frame = Frame.objects.get(id=previous_frame_id)
                    frame.previous_frame = previous_frame
                except Frame.DoesNotExist:
                    return Response({'error': 'Previous frame not found'}, status=status.HTTP_404_NOT_FOUND)

            if color is not None:
                frame.color = color

            if height is not None:
                frame.height = height

            if width is not None:
                frame.width = width

            if order is not None:
                frame.order = order

            frame.save()

            # Return updated frame (using retrieve method)
            return self.retrieve(request, *args, **kwargs)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            frame = self.get_object()
            frame.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GameObjectListCreateView(generics.ListCreateAPIView):
    queryset = GameObject.objects.all()
    serializer_class = GameObjectSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def create(self, request, *args, **kwargs):
        try:
            frame_id = request.data.get('frame')
            name = request.data.get('name')
            image = request.FILES.get('image', None)
            position_x = request.data.get('position_x', 0)
            position_y = request.data.get('position_y', 0)
            animation = request.data.get('animation', None)
            animation_speed = request.data.get('animation_speed', 1)
            animation_direction = request.data.get('animation_direction', None)

            if not frame_id:
                return Response({'error': 'Frame is required'}, status=status.HTTP_400_BAD_REQUEST)
            if not name:
                return Response({'error': 'Name is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if frame exists
            try:
                frame = Frame.objects.get(id=frame_id)
            except Frame.DoesNotExist:
                return Response({'error': 'Frame not found'}, status=status.HTTP_404_NOT_FOUND)

            # Create a new game object
            obj = GameObject.objects.create(
                frame=frame,
                name=name,
                image=image,
                position_x=position_x,
                position_y=position_y,
                animation=animation,
                animation_speed=animation_speed,
                animation_direction=animation_direction
            )

            # Build image URL if it exists
            image_url = None
            if obj.image and hasattr(obj.image, 'url'):
                image_url = request.build_absolute_uri(obj.image.url)

            # Return the created object data
            return Response({
                'id': obj.id,
                'frame': obj.frame.id,
                'name': obj.name,
                'image': image_url,
                'position_x': obj.position_x,
                'position_y': obj.position_y,
                'animation': obj.animation,
                'animation_speed': obj.animation_speed,
                'animation_direction': obj.animation_direction
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_queryset(self):
        queryset = GameObject.objects.all()
        frame_id = self.request.query_params.get('frame', None)

        if frame_id:
            queryset = queryset.filter(frame__id=frame_id)

        return queryset


class GameObjectRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GameObject.objects.all()
    serializer_class = GameObjectSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def retrieve(self, request, *args, **kwargs):
        try:
            obj = self.get_object()

            # Build image URL if it exists
            image_url = None
            if obj.image and hasattr(obj.image, 'url'):
                image_url = request.build_absolute_uri(obj.image.url)

            # Return the object data
            return Response({
                'id': obj.id,
                'frame': obj.frame.id,
                'name': obj.name,
                'image': image_url,
                'position_x': obj.position_x,
                'position_y': obj.position_y,
                'animation': obj.animation,
                'animation_speed': obj.animation_speed,
                'animation_direction': obj.animation_direction
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            obj = self.get_object()

            # Get data from request
            frame_id = request.data.get('frame')
            name = request.data.get('name')
            image = request.FILES.get('image')
            position_x = request.data.get('position_x')
            position_y = request.data.get('position_y')
            animation = request.data.get('animation')
            animation_speed = request.data.get('animation_speed')
            animation_direction = request.data.get('animation_direction')

            # Update fields if provided
            if frame_id is not None:
                try:
                    frame = Frame.objects.get(id=frame_id)
                    obj.frame = frame
                except Frame.DoesNotExist:
                    return Response({'error': 'Frame not found'}, status=status.HTTP_404_NOT_FOUND)
            if name is not None:
                obj.name = name
            if image is not None:
                obj.image = image
            elif 'image' in request.data and not image:
                # Handle removing image if empty value provided
                obj.image = None
            if position_x is not None:
                obj.position_x = position_x
            if position_y is not None:
                obj.position_y = position_y
            if animation is not None:
                obj.animation = animation
            if animation_speed is not None:
                obj.animation_speed = animation_speed
            if animation_direction is not None:
                obj.animation_direction = animation_direction

            obj.save()

            # Build image URL if it exists
            image_url = None
            if obj.image and hasattr(obj.image, 'url'):
                image_url = request.build_absolute_uri(obj.image.url)

            # Return updated data
            return Response({
                'id': obj.id,
                'frame': obj.frame.id,
                'name': obj.name,
                'image': image_url,
                'position_x': obj.position_x,
                'position_y': obj.position_y,
                'animation': obj.animation,
                'animation_speed': obj.animation_speed,
                'animation_direction': obj.animation_direction
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            obj = self.get_object()
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DialogueListCreateView(generics.ListCreateAPIView):
    queryset = Dialogue.objects.all()
    serializer_class = DialogueSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def create(self, request, *args, **kwargs):
        try:
            frame_id = request.data.get('frame')
            game_object_id = request.data.get('game_object')
            text = request.data.get('text')
            height = request.data.get('height', 100)
            width = request.data.get('width', 100)
            position_x = request.data.get('position_x', 0)
            position_y = request.data.get('position_y', 0)

            if not frame_id:
                return Response({'error': 'Frame is required'}, status=status.HTTP_400_BAD_REQUEST)
            if not game_object_id:
                return Response({'error': 'Game object is required'}, status=status.HTTP_400_BAD_REQUEST)
            if not text:
                return Response({'error': 'Text is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if frame exists
            try:
                frame = Frame.objects.get(id=frame_id)
            except Frame.DoesNotExist:
                return Response({'error': 'Frame not found'}, status=status.HTTP_404_NOT_FOUND)

            # Check if game object exists
            try:
                game_object = GameObject.objects.get(id=game_object_id)
            except GameObject.DoesNotExist:
                return Response({'error': 'Game object not found'}, status=status.HTTP_404_NOT_FOUND)

            # Create dialogue
            dialogue = Dialogue.objects.create(
                frame=frame,
                game_object=game_object,
                text=text,
                height=height,
                width=width,
                position_x=position_x,
                position_y=position_y
            )

            # Return the created dialogue data
            return Response({
                'id': dialogue.id,
                'frame': dialogue.frame.id,
                'game_object': dialogue.game_object.id,
                'text': dialogue.text,
                'height': dialogue.height,
                'width': dialogue.width,
                'position_x': dialogue.position_x,
                'position_y': dialogue.position_y
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_queryset(self):
        queryset = Dialogue.objects.all()
        frame_id = self.request.query_params.get('frame', None)
        game_object_id = self.request.query_params.get('game_object', None)

        if frame_id:
            queryset = queryset.filter(frame__id=frame_id)
        if game_object_id:
            queryset = queryset.filter(game_object__id=game_object_id)

        return queryset


class DialogueRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Dialogue.objects.all()
    serializer_class = DialogueSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def retrieve(self, request, *args, **kwargs):
        try:
            dialogue = self.get_object()

            # Return the dialogue data
            return Response({
                'id': dialogue.id,
                'frame': dialogue.frame.id,
                'game_object': dialogue.game_object.id,
                'text': dialogue.text,
                'height': dialogue.height,
                'width': dialogue.width,
                'position_x': dialogue.position_x,
                'position_y': dialogue.position_y
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            dialogue = self.get_object()

            # Get data from request
            frame_id = request.data.get('frame')
            game_object_id = request.data.get('game_object')
            text = request.data.get('text')
            height = request.data.get('height')
            width = request.data.get('width')
            position_x = request.data.get('position_x')
            position_y = request.data.get('position_y')

            # Update fields if provided
            if frame_id is not None:
                try:
                    frame = Frame.objects.get(id=frame_id)
                    dialogue.frame = frame
                except Frame.DoesNotExist:
                    return Response({'error': 'Frame not found'}, status=status.HTTP_404_NOT_FOUND)

            if game_object_id is not None:
                try:
                    game_object = GameObject.objects.get(id=game_object_id)
                    dialogue.game_object = game_object
                except GameObject.DoesNotExist:
                    return Response({'error': 'Game object not found'}, status=status.HTTP_404_NOT_FOUND)

            if text is not None:
                dialogue.text = text

            if height is not None:
                dialogue.height = height

            if width is not None:
                dialogue.width = width

            if position_x is not None:
                dialogue.position_x = position_x

            if position_y is not None:
                dialogue.position_y = position_y

            dialogue.save()

            # Return updated data
            return Response({
                'id': dialogue.id,
                'frame': dialogue.frame.id,
                'game_object': dialogue.game_object.id,
                'text': dialogue.text,
                'height': dialogue.height,
                'width': dialogue.width,
                'position_x': dialogue.position_x,
                'position_y': dialogue.position_y
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            dialogue = self.get_object()
            dialogue.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuizOptionListCreateView(generics.ListCreateAPIView):
    queryset = QuizOption.objects.all()
    serializer_class = QuizOptionSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def create(self, request, *args, **kwargs):
        try:
            text = request.data.get('text')
            is_correct = request.data.get('is_correct', False)
            explanation = request.data.get('explanation', '')

            if not text:
                return Response({'error': 'Text is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Create quiz option
            option = QuizOption.objects.create(
                text=text,
                is_correct=is_correct,
                explanation=explanation
            )

            # Return the created option data
            return Response({
                'id': option.id,
                'text': option.text,
                'is_correct': option.is_correct,
                'explanation': option.explanation
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuizOptionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = QuizOption.objects.all()
    serializer_class = QuizOptionSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def retrieve(self, request, *args, **kwargs):
        try:
            option = self.get_object()

            # Return the option data
            return Response({
                'id': option.id,
                'text': option.text,
                'is_correct': option.is_correct,
                'explanation': option.explanation
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            option = self.get_object()

            # Get data from request
            text = request.data.get('text')
            is_correct = request.data.get('is_correct', False)
            explanation = request.data.get('explanation', '')

            # Update fields if provided
            if text is not None:
                option.text = text
            if is_correct is not None:
                option.is_correct = is_correct
            if explanation is not None:
                option.explanation = explanation

            option.save()

            # Return updated data
            return Response({
                'id': option.id,
                'text': option.text,
                'is_correct': option.is_correct,
                'explanation': option.explanation
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            option = self.get_object()
            option.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuizListCreateView(generics.ListCreateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def create(self, request, *args, **kwargs):
        try:
            frame_id = request.data.get('frame')
            question = request.data.get('question')
            options_data = request.data.get('options', [])

            if not frame_id:
                return Response({'error': 'Frame is required'}, status=status.HTTP_400_BAD_REQUEST)
            if not question:
                return Response({'error': 'Question is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if frame exists
            try:
                frame = Frame.objects.get(id=frame_id)
            except Frame.DoesNotExist:
                return Response({'error': 'Frame not found'}, status=status.HTTP_404_NOT_FOUND)

            # Create quiz
            quiz = Quiz.objects.create(
                frame=frame,
                question=question
            )

            # Process options if provided
            created_options = []
            for option_data in options_data:
                text = option_data.get('text')
                is_correct = option_data.get('is_correct', False)
                explanation = option_data.get('explanation', '')

                if text:
                    option = QuizOption.objects.create(
                        text=text,
                        is_correct=is_correct,
                        explanation=explanation
                    )
                    quiz.options.add(option)

                    created_options.append({
                        'id': option.id,
                        'text': option.text,
                        'is_correct': option.is_correct,
                        'explanation': option.explanation
                    })

            # Return the created quiz data
            return Response({
                'id': quiz.id,
                'frame': quiz.frame.id,
                'question': quiz.question,
                'options': created_options
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_queryset(self):
        queryset = Quiz.objects.all()
        frame_id = self.request.query_params.get('frame', None)

        if frame_id:
            queryset = queryset.filter(frame__id=frame_id)

        return queryset


class QuizRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def retrieve(self, request, *args, **kwargs):
        try:
            quiz = self.get_object()

            # Get quiz options
            options_data = []
            for option in quiz.options.all():
                options_data.append({
                    'id': option.id,
                    'text': option.text,
                    'is_correct': option.is_correct,
                    'explanation': option.explanation
                })

            # Return the quiz data
            return Response({
                'id': quiz.id,
                'frame': quiz.frame.id,
                'question': quiz.question,
                'options': options_data
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            quiz = self.get_object()

            # Get data from request
            frame_id = request.data.get('frame')
            question = request.data.get('question')
            options_data = request.data.get('options', [])

            # Update fields if provided
            if frame_id:
                try:
                    frame = Frame.objects.get(id=frame_id)
                    quiz.frame = frame
                except Frame.DoesNotExist:
                    return Response({'error': 'Frame not found'}, status=status.HTTP_404_NOT_FOUND)

            if question:
                quiz.question = question

            quiz.save()

            # Update options if provided
            if options_data:
                # Clear existing options and add new ones
                quiz.options.clear()

                for option_data in options_data:
                    text = option_data.get('text')
                    is_correct = option_data.get('is_correct', False)
                    explanation = option_data.get('explanation', '')

                    if text:
                        option = QuizOption.objects.create(
                            text=text,
                            is_correct=is_correct,
                            explanation=explanation
                        )
                        quiz.options.add(option)

            # Return updated quiz data (using retrieve)
            return self.retrieve(request, *args, **kwargs)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            quiz = self.get_object()
            quiz.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ValidateQuizAnswerView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            quiz_id = request.data.get('quiz_id')
            option_id = request.data.get('option_id')

            # Validate input parameters
            if not quiz_id:
                return Response(
                    {"error": "Quiz ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not option_id:
                return Response(
                    {"error": "Option ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if quiz exists
            try:
                quiz = Quiz.objects.get(id=quiz_id)
            except Quiz.DoesNotExist:
                return Response(
                    {"error": "Quiz not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Check if option exists and belongs to the quiz
            try:
                option = QuizOption.objects.get(id=option_id)
                if not quiz.options.filter(id=option_id).exists():
                    return Response(
                        {"error": "This option doesn't belong to the specified quiz"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except QuizOption.DoesNotExist:
                return Response(
                    {"error": "Option not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Build response based on option correctness
            response_data = {
                'is_correct': option.is_correct,
                'explanation': option.explanation
            }

            # Update user progress if user is authenticated and option is correct
            if option.is_correct:
                user = request.user
                frame = quiz.frame
                lesson = frame.lesson

                if lesson:
                    # Get or create user progress for this lesson
                    user_progress, created = UserProgress.objects.get_or_create(
                        user=user,
                        lesson=lesson,
                        defaults={'current_frame': frame, 'score': 0}
                    )

                    # Add this frame to completed frames
                    user_progress.completed_frames.add(frame)

                    # Update score
                    user_progress.score += 1
                    user_progress.save()

            return Response(response_data)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProgressListCreateView(generics.ListCreateAPIView):
    queryset = UserProgress.objects.all()
    serializer_class = UserProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users should only see their own progress
        return UserProgress.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            user = request.user
            lesson_id = request.data.get('lesson')
            current_frame_id = request.data.get('current_frame')
            completed_frame_ids = request.data.get('completed_frames', [])
            score = request.data.get('score', 0)

            if not lesson_id:
                return Response({'error': 'Lesson is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if lesson exists
            from course.models import Lesson
            try:
                lesson = Lesson.objects.get(id=lesson_id)
            except Lesson.DoesNotExist:
                return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)

            # Get current frame if provided
            current_frame = None
            if current_frame_id:
                try:
                    current_frame = Frame.objects.get(id=current_frame_id)
                except Frame.DoesNotExist:
                    return Response({'error': 'Current frame not found'}, status=status.HTTP_404_NOT_FOUND)

            # Create or update user progress
            user_progress, created = UserProgress.objects.get_or_create(
                user=user,
                lesson=lesson,
                defaults={'current_frame': current_frame, 'score': score}
            )

            if not created:
                # Update existing progress
                if current_frame:
                    user_progress.current_frame = current_frame
                user_progress.score = score
                user_progress.save()

            # Add completed frames if provided
            if completed_frame_ids:
                completed_frames = Frame.objects.filter(
                    id__in=completed_frame_ids)
                user_progress.completed_frames.add(*completed_frames)

            # Prepare response data
            completed_frames_data = []
            for frame in user_progress.completed_frames.all():
                completed_frames_data.append(frame.id)

            return Response({
                'id': user_progress.id,
                'user': user_progress.user.id,
                'lesson': user_progress.lesson.id,
                'current_frame': user_progress.current_frame.id if user_progress.current_frame else None,
                'completed_frames': completed_frames_data,
                'score': user_progress.score,
                'last_interaction': user_progress.last_interaction
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProgressRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProgress.objects.all()
    serializer_class = UserProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users should only access their own progress
        return UserProgress.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        try:
            user_progress = self.get_object()

            # Prepare completed frames data
            completed_frames_data = []
            for frame in user_progress.completed_frames.all():
                completed_frames_data.append(frame.id)

            # Return the progress data
            return Response({
                'id': user_progress.id,
                'user': user_progress.user.id,
                'lesson': user_progress.lesson.id,
                'current_frame': user_progress.current_frame.id if user_progress.current_frame else None,
                'completed_frames': completed_frames_data,
                'score': user_progress.score,
                'last_interaction': user_progress.last_interaction
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            user_progress = self.get_object()

            # Get data from request
            lesson_id = request.data.get('lesson')
            current_frame_id = request.data.get('current_frame')
            completed_frame_ids = request.data.get('completed_frames')
            score = request.data.get('score')

            # Update fields if provided
            if lesson_id:
                from course.models import Lesson
                try:
                    lesson = Lesson.objects.get(id=lesson_id)
                    user_progress.lesson = lesson
                except Lesson.DoesNotExist:
                    return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)

            if current_frame_id:
                try:
                    current_frame = Frame.objects.get(id=current_frame_id)
                    user_progress.current_frame = current_frame
                except Frame.DoesNotExist:
                    return Response({'error': 'Current frame not found'}, status=status.HTTP_404_NOT_FOUND)

            if score is not None:
                user_progress.score = score

            user_progress.save()

            # Update completed frames if provided
            if completed_frame_ids is not None:
                user_progress.completed_frames.clear()
                if completed_frame_ids:
                    completed_frames = Frame.objects.filter(
                        id__in=completed_frame_ids)
                    user_progress.completed_frames.add(*completed_frames)

            # Return updated progress data
            return self.retrieve(request, *args, **kwargs)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            user_progress = self.get_object()
            user_progress.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
