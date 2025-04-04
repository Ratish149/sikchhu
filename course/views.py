from rest_framework import status, generics, filters as rest_filters, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Class, Subject, Chapter, Lesson, Video, LearningMaterial, Answer, Question
from .serializers import (
    ClassSerializer, SubjectSerializer, ChapterSerializer, LessonSerializer,
    VideoSerializer, LearningMaterialSerializer, AnswerSerializer, QuestionSerializer
)
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
import json


class ClassListCreateView(generics.ListCreateAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def create(self, request, *args, **kwargs):
        try:
            name = request.data.get('name')
            description = request.data.get('description', '')
            icon = request.FILES.get('icon', None)

            if not name:
                return Response({'error': 'Name is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Create a new class instance
            class_obj = Class.objects.create(
                name=name,
                description=description,
                icon=icon
            )

            # Build the icon URL if it exists
            icon_url = None
            if class_obj.icon and hasattr(class_obj.icon, 'url'):
                icon_url = request.build_absolute_uri(class_obj.icon.url)

            # Return the created object data
            return Response({
                'id': class_obj.id,
                'name': class_obj.name,
                'slug': class_obj.slug,
                'description': class_obj.description,
                'icon': icon_url,
                'created_at': class_obj.created_at,
                'updated_at': class_obj.updated_at
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClassRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    lookup_field = 'slug'
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def retrieve(self, request, *args, **kwargs):
        try:
            class_obj = self.get_object()

            # Build the icon URL if it exists
            icon_url = None
            if class_obj.icon and hasattr(class_obj.icon, 'url'):
                icon_url = request.build_absolute_uri(class_obj.icon.url)

            # Return the class data
            return Response({
                'id': class_obj.id,
                'name': class_obj.name,
                'slug': class_obj.slug,
                'description': class_obj.description,
                'icon': icon_url,
                'created_at': class_obj.created_at,
                'updated_at': class_obj.updated_at
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            class_obj = self.get_object()

            # Get data from request
            name = request.data.get('name')
            description = request.data.get('description')
            icon = request.FILES.get('icon')

            # Update fields if provided
            if name is not None:
                class_obj.name = name
            if description is not None:
                class_obj.description = description
            if icon is not None:
                class_obj.icon = icon
            elif 'icon' in request.data and not icon:
                # Handle removing icon if empty value provided
                class_obj.icon = None

            class_obj.save()

            # Build the icon URL if it exists
            icon_url = None
            if class_obj.icon and hasattr(class_obj.icon, 'url'):
                icon_url = request.build_absolute_uri(class_obj.icon.url)

            # Return updated data
            return Response({
                'id': class_obj.id,
                'name': class_obj.name,
                'slug': class_obj.slug,
                'description': class_obj.description,
                'icon': icon_url,
                'created_at': class_obj.created_at,
                'updated_at': class_obj.updated_at
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            class_obj = self.get_object()
            class_obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubjectListCreateView(generics.ListCreateAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def create(self, request, *args, **kwargs):
        try:
            class_id = request.data.get('class_name')
            name = request.data.get('name')
            description = request.data.get('description', '')
            icon = request.FILES.get('icon', None)

            if not class_id:
                return Response({'error': 'Class is required'}, status=status.HTTP_400_BAD_REQUEST)
            if not name:
                return Response({'error': 'Name is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if class exists
            try:
                class_obj = Class.objects.get(id=class_id)
            except Class.DoesNotExist:
                return Response({'error': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)

            # Create a new subject instance
            subject = Subject.objects.create(
                class_name=class_obj,
                name=name,
                description=description,
                icon=icon
            )

            # Build the icon URL if it exists
            icon_url = None
            if subject.icon and hasattr(subject.icon, 'url'):
                icon_url = request.build_absolute_uri(subject.icon.url)

            # Return the created object data
            return Response({
                'id': subject.id,
                'class_name': subject.class_name.id,
                'name': subject.name,
                'slug': subject.slug,
                'description': subject.description,
                'icon': icon_url,
                'created_at': subject.created_at,
                'updated_at': subject.updated_at
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_queryset(self):
        queryset = Subject.objects.all()
        class_slug = self.request.query_params.get('class_slug', None)

        if class_slug is not None:
            queryset = queryset.filter(class_name__slug=class_slug)

        return queryset


class SubjectRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    lookup_field = 'slug'
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def retrieve(self, request, *args, **kwargs):
        try:
            subject = self.get_object()

            # Build the icon URL if it exists
            icon_url = None
            if subject.icon and hasattr(subject.icon, 'url'):
                icon_url = request.build_absolute_uri(subject.icon.url)

            # Return the subject data
            return Response({
                'id': subject.id,
                'class_name': subject.class_name.id,
                'name': subject.name,
                'slug': subject.slug,
                'description': subject.description,
                'icon': icon_url,
                'created_at': subject.created_at,
                'updated_at': subject.updated_at
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            subject = self.get_object()

            # Get data from request
            class_id = request.data.get('class_name')
            name = request.data.get('name')
            description = request.data.get('description')
            icon = request.FILES.get('icon')

            # Update fields if provided
            if class_id is not None:
                try:
                    class_obj = Class.objects.get(id=class_id)
                    subject.class_name = class_obj
                except Class.DoesNotExist:
                    return Response({'error': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)
            if name is not None:
                subject.name = name
            if description is not None:
                subject.description = description
            if icon is not None:
                subject.icon = icon
            elif 'icon' in request.data and not icon:
                # Handle removing icon if empty value provided
                subject.icon = None

            subject.save()

            # Build the icon URL if it exists
            icon_url = None
            if subject.icon and hasattr(subject.icon, 'url'):
                icon_url = request.build_absolute_uri(subject.icon.url)

            # Return updated data
            return Response({
                'id': subject.id,
                'class_name': subject.class_name.id,
                'name': subject.name,
                'slug': subject.slug,
                'description': subject.description,
                'icon': icon_url,
                'created_at': subject.created_at,
                'updated_at': subject.updated_at
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            subject = self.get_object()
            subject.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChapterListCreateView(generics.ListCreateAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def create(self, request, *args, **kwargs):
        try:
            subject_id = request.data.get('subject_name')
            name = request.data.get('name')
            description = request.data.get('description', '')
            icon = request.FILES.get('icon', None)

            if not subject_id:
                return Response({'error': 'Subject is required'}, status=status.HTTP_400_BAD_REQUEST)
            if not name:
                return Response({'error': 'Name is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if subject exists
            try:
                subject = Subject.objects.get(id=subject_id)
            except Subject.DoesNotExist:
                return Response({'error': 'Subject not found'}, status=status.HTTP_404_NOT_FOUND)

            # Create a new chapter instance
            chapter = Chapter.objects.create(
                subject_name=subject,
                name=name,
                description=description,
                icon=icon
            )

            # Build the icon URL if it exists
            icon_url = None
            if chapter.icon and hasattr(chapter.icon, 'url'):
                icon_url = request.build_absolute_uri(chapter.icon.url)

            # Return the created object data
            return Response({
                'id': chapter.id,
                'subject_name': chapter.subject_name.id,
                'name': chapter.name,
                'slug': chapter.slug,
                'description': chapter.description,
                'icon': icon_url,
                'created_at': chapter.created_at,
                'updated_at': chapter.updated_at
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_queryset(self):
        queryset = Chapter.objects.all()
        subject_slug = self.request.query_params.get('subject_slug', None)

        if subject_slug is not None:
            queryset = queryset.filter(subject_name__slug=subject_slug)

        return queryset


class ChapterRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def retrieve(self, request, *args, **kwargs):
        try:
            chapter = self.get_object()

            # Build the icon URL if it exists
            icon_url = None
            if chapter.icon and hasattr(chapter.icon, 'url'):
                icon_url = request.build_absolute_uri(chapter.icon.url)

            # Return the chapter data
            return Response({
                'id': chapter.id,
                'subject_name': chapter.subject_name.id,
                'name': chapter.name,
                'slug': chapter.slug,
                'description': chapter.description,
                'icon': icon_url,
                'created_at': chapter.created_at,
                'updated_at': chapter.updated_at
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            chapter = self.get_object()

            # Get data from request
            subject_id = request.data.get('subject_name')
            name = request.data.get('name')
            description = request.data.get('description')
            icon = request.FILES.get('icon')

            # Update fields if provided
            if subject_id is not None:
                try:
                    subject = Subject.objects.get(id=subject_id)
                    chapter.subject_name = subject
                except Subject.DoesNotExist:
                    return Response({'error': 'Subject not found'}, status=status.HTTP_404_NOT_FOUND)
            if name is not None:
                chapter.name = name
            if description is not None:
                chapter.description = description
            if icon is not None:
                chapter.icon = icon
            elif 'icon' in request.data and not icon:
                # Handle removing icon if empty value provided
                chapter.icon = None

            chapter.save()

            # Build the icon URL if it exists
            icon_url = None
            if chapter.icon and hasattr(chapter.icon, 'url'):
                icon_url = request.build_absolute_uri(chapter.icon.url)

            # Return updated data
            return Response({
                'id': chapter.id,
                'subject_name': chapter.subject_name.id,
                'name': chapter.name,
                'slug': chapter.slug,
                'description': chapter.description,
                'icon': icon_url,
                'created_at': chapter.created_at,
                'updated_at': chapter.updated_at
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            chapter = self.get_object()
            chapter.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all().order_by('-id')
    serializer_class = LessonSerializer
    filter_backends = [rest_filters.SearchFilter, rest_filters.OrderingFilter]
    search_fields = ['name', 'description', 'chapter_name__name']
    ordering_fields = ['-id', 'name', 'created_at']
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def create(self, request, *args, **kwargs):
        try:
            # Handle both form-data and raw JSON formats
            data = request.data.copy()

            # Get related data from request
            videos_data = []
            learning_materials_data = []
            questions_data = []

            # Handle videos data
            if isinstance(request.data.get('videos'), list):
                videos_data = request.data.get('videos')
            elif hasattr(request.data, 'getlist') and request.data.get('videos'):
                try:
                    videos_data = json.loads(request.data.get('videos'))
                except json.JSONDecodeError:
                    return Response(
                        {"error": "Invalid videos format"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Handle learning materials data
            if isinstance(request.data.get('learning_materials'), list):
                learning_materials_data = request.data.get(
                    'learning_materials')
            elif hasattr(request.data, 'getlist') and request.data.get('learning_materials'):
                try:
                    learning_materials_data = json.loads(
                        request.data.get('learning_materials'))
                except json.JSONDecodeError:
                    return Response(
                        {"error": "Invalid learning materials format"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Handle questions data
            if isinstance(request.data.get('questions'), list):
                questions_data = request.data.get('questions')
            elif hasattr(request.data, 'getlist') and request.data.get('questions'):
                try:
                    questions_data = json.loads(request.data.get('questions'))
                except json.JSONDecodeError:
                    return Response(
                        {"error": "Invalid questions format"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Create the modified data dictionary
            modified_data = {
                'chapter_name': request.data.get('chapter_name'),
                'name': request.data.get('name'),
                'description': request.data.get('description'),
                'videos': videos_data,
                'learning_materials': learning_materials_data,
                'questions': questions_data
            }

            # Handle icon file
            if 'icon' in request.FILES:
                modified_data['icon'] = request.FILES['icon']
            elif request.data.get('icon'):
                modified_data['icon'] = request.data.get('icon')

            # Update the request data
            request._full_data = modified_data

            # Validate required fields
            if not modified_data.get('chapter_name'):
                return Response(
                    {"error": "Chapter name is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not modified_data.get('name'):
                return Response(
                    {"error": "Lesson name is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if chapter exists
            try:
                chapter = Chapter.objects.get(
                    id=modified_data.get('chapter_name'))
            except Chapter.DoesNotExist:
                return Response(
                    {"error": "Chapter not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Create the lesson
            lesson = Lesson.objects.create(
                chapter_name=chapter,
                name=modified_data.get('name'),
                description=modified_data.get('description', ''),
                icon=modified_data.get('icon')
            )

            # Process videos
            created_videos = []
            for video_data in videos_data:
                video_name = video_data.get('name')
                video_url = video_data.get('video_url', None)
                video_file = request.FILES.get('video_file', None)

                if video_name:
                    video = Video.objects.create(
                        lesson_name=lesson,
                        name=video_name,
                        video_url=video_url,
                        video_file=video_file
                    )

                    video_file_url = None
                    if video.video_file and hasattr(video.video_file, 'url'):
                        video_file_url = request.build_absolute_uri(
                            video.video_file.url)

                    created_videos.append({
                        'id': video.id,
                        'name': video.name,
                        'slug': video.slug,
                        'video_url': video.video_url,
                        'video_file': video_file_url,
                        'created_at': video.created_at,
                        'updated_at': video.updated_at
                    })

            # Process learning materials
            created_materials = []
            for material_data in learning_materials_data:
                title = material_data.get('title')
                material_type = material_data.get('material_type')
                description = material_data.get('description', '')
                game_url = material_data.get('game_url', None)
                file = request.FILES.get('file', None)

                if title and material_type:
                    # Check material type validation
                    valid_types = [choice[0]
                                   for choice in LearningMaterial.CHOICES]
                    if material_type not in valid_types:
                        return Response({
                            'error': f"Invalid material_type. Must be one of: {', '.join(valid_types)}"
                        }, status=status.HTTP_400_BAD_REQUEST)

                    material = LearningMaterial.objects.create(
                        lesson=lesson,
                        title=title,
                        material_type=material_type,
                        description=description,
                        file=file,
                        game_url=game_url
                    )

                    file_url = None
                    if material.file and hasattr(material.file, 'url'):
                        file_url = request.build_absolute_uri(
                            material.file.url)

                    created_materials.append({
                        'id': material.id,
                        'title': material.title,
                        'material_type': material.material_type,
                        'description': material.description,
                        'file': file_url,
                        'game_url': material.game_url,
                        'created_at': material.created_at,
                        'updated_at': material.updated_at
                    })

            # Process questions and answers
            created_questions = []
            for question_data in questions_data:
                question_text = question_data.get('question_text')
                explanation = question_data.get('explanation', '')
                answers_data = question_data.get('answers', [])

                if question_text:
                    question = Question.objects.create(
                        lesson=lesson,
                        question_text=question_text,
                        explanation=explanation
                    )

                    created_answers = []
                    for answer_data in answers_data:
                        answer_text = answer_data.get('answer_text')
                        is_correct = answer_data.get('is_correct', False)

                        if answer_text:
                            answer = Answer.objects.create(
                                answer_text=answer_text,
                                is_correct=is_correct
                            )
                            question.answer.add(answer)

                            created_answers.append({
                                'id': answer.id,
                                'answer_text': answer.answer_text,
                                'is_correct': answer.is_correct,
                                'created_at': answer.created_at,
                                'updated_at': answer.updated_at
                            })

                    created_questions.append({
                        'id': question.id,
                        'question_text': question.question_text,
                        'explanation': question.explanation,
                        'answers': created_answers,
                        'created_at': question.created_at,
                        'updated_at': question.updated_at
                    })

            # Build the icon URL if it exists
            icon_url = None
            if lesson.icon and hasattr(lesson.icon, 'url'):
                icon_url = request.build_absolute_uri(lesson.icon.url)

            # Return the created object data
            return Response({
                'id': lesson.id,
                'chapter_name': lesson.chapter_name.id,
                'name': lesson.name,
                'slug': lesson.slug,
                'description': lesson.description,
                'icon': icon_url,
                'created_at': lesson.created_at,
                'updated_at': lesson.updated_at,
                'videos': created_videos,
                'learning_materials': created_materials,
                'questions': created_questions
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": f"Failed to create lesson: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    def get_queryset(self):
        queryset = Lesson.objects.all().order_by('-id')
        chapter_slug = self.request.query_params.get('chapter_slug', None)
        subject_slug = self.request.query_params.get('subject_slug', None)
        class_slug = self.request.query_params.get('class_slug', None)

        if chapter_slug:
            queryset = queryset.filter(chapter_name__slug=chapter_slug)
        if subject_slug:
            queryset = queryset.filter(
                chapter_name__subject_name__slug=subject_slug)
        if class_slug:
            queryset = queryset.filter(
                chapter_name__subject_name__class_name__slug=class_slug)

        return queryset


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        try:
            lesson = self.get_object()

            # Build the icon URL if it exists
            icon_url = None
            if lesson.icon and hasattr(lesson.icon, 'url'):
                icon_url = request.build_absolute_uri(lesson.icon.url)

            # Get videos related to this lesson - using the related manager
            videos = []
            for video in Video.objects.filter(lesson_name=lesson):
                video_file_url = None
                if video.video_file and hasattr(video.video_file, 'url'):
                    video_file_url = request.build_absolute_uri(
                        video.video_file.url)

                videos.append({
                    'id': video.id,
                    'name': video.name,
                    'slug': getattr(video, 'slug', None),
                    'video_url': video.video_url,
                    'video_file': video_file_url,

                })

            # Get learning materials related to this lesson - using the related_name "materials"
            learning_materials = []
            for material in lesson.materials.all():
                file_url = None
                if material.file and hasattr(material.file, 'url'):
                    file_url = request.build_absolute_uri(material.file.url)

                learning_materials.append({
                    'id': material.id,
                    'title': material.title,
                    'material_type': material.material_type,
                    'description': material.description,
                    'file': file_url,
                    'game_url': material.game_url,
                })

            # Get questions related to this lesson - using the related_name "questions"
            questions = []
            for question in lesson.questions.all():
                # Get answers for this question
                answers = []
                for answer in question.answer.all():
                    answers.append({
                        'id': answer.id,
                        'answer_text': answer.answer_text,
                        'is_correct': answer.is_correct,
                    })

                questions.append({
                    'id': question.id,
                    'question_text': question.question_text,
                    'explanation': question.explanation,
                    'answers': answers,
                })

            # Return the lesson data with related objects
            return Response({
                'id': lesson.id,
                'chapter_name': lesson.chapter_name.id,
                'name': lesson.name,
                'slug': lesson.slug,
                'description': lesson.description,
                'icon': icon_url,
                'videos': videos,
                'learning_materials': learning_materials,
                'questions': questions
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            lesson = self.get_object()

            # Get data from request
            chapter_id = request.data.get('chapter_name')
            name = request.data.get('name')
            description = request.data.get('description')
            icon = request.FILES.get('icon')

            # Update fields if provided
            if chapter_id is not None:
                try:
                    chapter = Chapter.objects.get(id=chapter_id)
                    lesson.chapter_name = chapter
                except Chapter.DoesNotExist:
                    return Response({'error': 'Chapter not found'}, status=status.HTTP_404_NOT_FOUND)
            if name is not None:
                lesson.name = name
            if description is not None:
                lesson.description = description
            if icon is not None:
                lesson.icon = icon
            elif 'icon' in request.data and not icon:
                # Handle removing icon if empty value provided
                lesson.icon = None

            lesson.save()

            # Build the icon URL if it exists
            icon_url = None
            if lesson.icon and hasattr(lesson.icon, 'url'):
                icon_url = request.build_absolute_uri(lesson.icon.url)

            # Get videos related to this lesson - using the related manager
            videos = []
            for video in Video.objects.filter(lesson_name=lesson):
                video_file_url = None
                if video.video_file and hasattr(video.video_file, 'url'):
                    video_file_url = request.build_absolute_uri(
                        video.video_file.url)

                videos.append({
                    'id': video.id,
                    'name': video.name,
                    'slug': getattr(video, 'slug', None),
                    'video_url': video.video_url,
                    'video_file': video_file_url,
                    'created_at': video.created_at,
                    'updated_at': video.updated_at
                })

            # Get learning materials related to this lesson - using the related_name "materials"
            learning_materials = []
            for material in lesson.materials.all():
                file_url = None
                if material.file and hasattr(material.file, 'url'):
                    file_url = request.build_absolute_uri(material.file.url)

                learning_materials.append({
                    'id': material.id,
                    'title': material.title,
                    'material_type': material.material_type,
                    'description': material.description,
                    'file': file_url,
                    'game_url': material.game_url,
                    'created_at': material.created_at,
                    'updated_at': material.updated_at
                })

            # Get questions related to this lesson - using the related_name "questions"
            questions = []
            for question in lesson.questions.all():
                # Get answers for this question
                answers = []
                for answer in question.answer.all():
                    answers.append({
                        'id': answer.id,
                        'answer_text': answer.answer_text,
                        'is_correct': answer.is_correct,
                        'created_at': answer.created_at,
                        'updated_at': answer.updated_at
                    })

                questions.append({
                    'id': question.id,
                    'question_text': question.question_text,
                    'explanation': question.explanation,
                    'answers': answers,
                    'created_at': question.created_at,
                    'updated_at': question.updated_at
                })

            # Return updated data with related objects
            return Response({
                'id': lesson.id,
                'chapter_name': lesson.chapter_name.id,
                'name': lesson.name,
                'slug': lesson.slug,
                'description': lesson.description,
                'icon': icon_url,
                'created_at': lesson.created_at,
                'updated_at': lesson.updated_at,
                'videos': videos,
                'learning_materials': learning_materials,
                'questions': questions
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            lesson = self.get_object()
            lesson.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VideoListCreateView(generics.ListCreateAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def create(self, request, *args, **kwargs):
        try:
            lesson_id = request.data.get('lesson_name')
            name = request.data.get('name')
            video_url = request.data.get('video_url', None)
            video_file = request.FILES.get('video_file', None)

            if not lesson_id:
                return Response({'error': 'Lesson is required'}, status=status.HTTP_400_BAD_REQUEST)
            if not name:
                return Response({'error': 'Name is required'}, status=status.HTTP_400_BAD_REQUEST)
            if not video_url and not video_file:
                return Response({'error': 'Either video URL or file is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if lesson exists
            try:
                lesson = Lesson.objects.get(id=lesson_id)
            except Lesson.DoesNotExist:
                return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)

            # Create a new video instance
            video = Video.objects.create(
                lesson_name=lesson,
                name=name,
                video_url=video_url,
                video_file=video_file
            )

            # Build the video file URL if it exists
            video_file_url = None
            if video.video_file and hasattr(video.video_file, 'url'):
                video_file_url = request.build_absolute_uri(
                    video.video_file.url)

            # Return the created object data
            return Response({
                'id': video.id,
                'lesson_name': video.lesson_name.id,
                'name': video.name,
                'slug': video.slug,
                'video_url': video.video_url,
                'video_file': video_file_url,
                'created_at': video.created_at,
                'updated_at': video.updated_at
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_queryset(self):
        queryset = Video.objects.all()
        lesson_slug = self.request.query_params.get('lesson_slug', None)

        if lesson_slug is not None:
            queryset = queryset.filter(lesson_name__slug=lesson_slug)

        return queryset


class VideoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def retrieve(self, request, *args, **kwargs):
        try:
            video = self.get_object()

            # Build the video file URL if it exists
            video_file_url = None
            if video.video_file and hasattr(video.video_file, 'url'):
                video_file_url = request.build_absolute_uri(
                    video.video_file.url)

            # Return the video data
            return Response({
                'id': video.id,
                'lesson_name': video.lesson_name.id,
                'name': video.name,
                'slug': video.slug,
                'video_url': video.video_url,
                'video_file': video_file_url,
                'created_at': video.created_at,
                'updated_at': video.updated_at
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            video = self.get_object()

            # Get data from request
            lesson_id = request.data.get('lesson_name')
            name = request.data.get('name')
            video_url = request.data.get('video_url')
            video_file = request.FILES.get('video_file')

            # Update fields if provided
            if lesson_id is not None:
                try:
                    lesson = Lesson.objects.get(id=lesson_id)
                    video.lesson_name = lesson
                except Lesson.DoesNotExist:
                    return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)
            if name is not None:
                video.name = name
            if video_url is not None:
                video.video_url = video_url
            if video_file is not None:
                video.video_file = video_file
            elif 'video_file' in request.data and not video_file:
                # Handle removing video file if empty value provided
                video.video_file = None

            video.save()

            # Build the video file URL if it exists
            video_file_url = None
            if video.video_file and hasattr(video.video_file, 'url'):
                video_file_url = request.build_absolute_uri(
                    video.video_file.url)

            # Return updated data
            return Response({
                'id': video.id,
                'lesson_name': video.lesson_name.id,
                'name': video.name,
                'slug': video.slug,
                'video_url': video.video_url,
                'video_file': video_file_url,
                'created_at': video.created_at,
                'updated_at': video.updated_at
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            video = self.get_object()
            video.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LearningMaterialListCreateView(generics.ListCreateAPIView):
    queryset = LearningMaterial.objects.all()
    serializer_class = LearningMaterialSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def create(self, request, *args, **kwargs):
        try:
            lesson_id = request.data.get('lesson')
            title = request.data.get('title')
            material_type = request.data.get('material_type')
            description = request.data.get('description', '')
            file = request.FILES.get('file', None)
            game_url = request.data.get('game_url', None)

            if not lesson_id:
                return Response({'error': 'Lesson is required'}, status=status.HTTP_400_BAD_REQUEST)
            if not material_type:
                return Response({'error': 'Material type is required'}, status=status.HTTP_400_BAD_REQUEST)

            # For gamification type, check if game_url is provided
            if material_type == 'Gamefication' and not game_url:
                return Response({'error': 'Game URL is required for Gamefication type'}, status=status.HTTP_400_BAD_REQUEST)

            # For other types, check if file is provided
            if material_type != 'Gamefication' and not file:
                return Response({'error': 'File is required for this material type'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if lesson exists
            try:
                lesson = Lesson.objects.get(id=lesson_id)
            except Lesson.DoesNotExist:
                return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)

            # Create a new learning material instance
            material = LearningMaterial.objects.create(
                lesson=lesson,
                title=title,
                material_type=material_type,
                description=description,
                file=file,
                game_url=game_url
            )

            # Build the file URL if it exists
            file_url = None
            if material.file and hasattr(material.file, 'url'):
                file_url = request.build_absolute_uri(material.file.url)

            # Return the created object data
            return Response({
                'id': material.id,
                'lesson': material.lesson.id,
                'title': material.title,
                'material_type': material.material_type,
                'description': material.description,
                'file': file_url,
                'game_url': material.game_url,
                'created_at': material.created_at,
                'updated_at': material.updated_at
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_queryset(self):
        queryset = LearningMaterial.objects.all()
        lesson_id = self.request.query_params.get('lesson', None)
        material_type = self.request.query_params.get('material_type', None)

        if lesson_id is not None:
            queryset = queryset.filter(lesson__id=lesson_id)
        if material_type is not None:
            queryset = queryset.filter(material_type=material_type)

        return queryset


class LearningMaterialRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LearningMaterial.objects.all()
    serializer_class = LearningMaterialSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def retrieve(self, request, *args, **kwargs):
        try:
            material = self.get_object()

            # Build the file URL if it exists
            file_url = None
            if material.file and hasattr(material.file, 'url'):
                file_url = request.build_absolute_uri(material.file.url)

            # Return the material data
            return Response({
                'id': material.id,
                'lesson': material.lesson.id if material.lesson else None,
                'title': material.title,
                'material_type': material.material_type,
                'description': material.description,
                'file': file_url,
                'game_url': material.game_url,
                'created_at': material.created_at,
                'updated_at': material.updated_at
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            material = self.get_object()

            # Get data from request
            lesson_id = request.data.get('lesson')
            title = request.data.get('title')
            material_type = request.data.get('material_type')
            description = request.data.get('description')
            file = request.FILES.get('file')
            game_url = request.data.get('game_url')

            # Update fields if provided
            if lesson_id is not None:
                try:
                    lesson = Lesson.objects.get(id=lesson_id)
                    material.lesson = lesson
                except Lesson.DoesNotExist:
                    return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)
            if title is not None:
                material.title = title
            if material_type is not None:
                material.material_type = material_type
            if description is not None:
                material.description = description
            if file is not None:
                material.file = file
            elif 'file' in request.data and not file:
                # Handle removing file if empty value provided
                material.file = None
            if game_url is not None:
                material.game_url = game_url

            material.save()

            # Build the file URL if it exists
            file_url = None
            if material.file and hasattr(material.file, 'url'):
                file_url = request.build_absolute_uri(material.file.url)

            # Return updated data
            return Response({
                'id': material.id,
                'lesson': material.lesson.id if material.lesson else None,
                'title': material.title,
                'material_type': material.material_type,
                'description': material.description,
                'file': file_url,
                'game_url': material.game_url,
                'created_at': material.created_at,
                'updated_at': material.updated_at
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            material = self.get_object()
            material.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AnswerListCreateView(generics.ListCreateAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def create(self, request, *args, **kwargs):
        try:
            answer_text = request.data.get('answer_text')
            is_correct = request.data.get('is_correct', False)

            if not answer_text:
                return Response({'error': 'Answer text is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Create a new answer instance
            answer = Answer.objects.create(
                answer_text=answer_text,
                is_correct=is_correct
            )

            # Return the created object data
            return Response({
                'id': answer.id,
                'answer_text': answer.answer_text,
                'is_correct': answer.is_correct,
                'created_at': answer.created_at,
                'updated_at': answer.updated_at
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AnswerRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def retrieve(self, request, *args, **kwargs):
        try:
            answer = self.get_object()

            # Return the answer data
            return Response({
                'id': answer.id,
                'answer_text': answer.answer_text,
                'is_correct': answer.is_correct,
                'created_at': answer.created_at,
                'updated_at': answer.updated_at
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            answer = self.get_object()

            # Get data from request
            answer_text = request.data.get('answer_text')
            is_correct = request.data.get('is_correct')

            # Update fields if provided
            if answer_text is not None:
                answer.answer_text = answer_text
            if is_correct is not None:
                answer.is_correct = is_correct

            answer.save()

            # Return updated data
            return Response({
                'id': answer.id,
                'answer_text': answer.answer_text,
                'is_correct': answer.is_correct,
                'created_at': answer.created_at,
                'updated_at': answer.updated_at
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            answer = self.get_object()
            answer.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuestionListCreateView(generics.ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def create(self, request, *args, **kwargs):
        try:
            lesson_id = request.data.get('lesson')
            question_text = request.data.get('question_text')
            explanation = request.data.get('explanation', '')
            answer_ids = request.data.get('answer', [])

            if not question_text:
                return Response({'error': 'Question text is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if lesson exists if provided
            lesson = None
            if lesson_id:
                try:
                    lesson = Lesson.objects.get(id=lesson_id)
                except Lesson.DoesNotExist:
                    return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)

            # Create a new question instance
            question = Question.objects.create(
                lesson=lesson,
                question_text=question_text,
                explanation=explanation
            )

            # Add answers if provided
            if answer_ids:
                answers = Answer.objects.filter(id__in=answer_ids)
                question.answer.set(answers)

            # Return the created object data with answer details
            answer_data = []
            for answer in question.answer.all():
                answer_data.append({
                    'id': answer.id,
                    'answer_text': answer.answer_text,
                    'is_correct': answer.is_correct
                })

            return Response({
                'id': question.id,
                'lesson': question.lesson.id if question.lesson else None,
                'question_text': question.question_text,
                'explanation': question.explanation,
                'answer': answer_data,
                'created_at': question.created_at,
                'updated_at': question.updated_at
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_queryset(self):
        queryset = Question.objects.all()
        lesson_id = self.request.query_params.get('lesson', None)

        if lesson_id is not None:
            queryset = queryset.filter(lesson__id=lesson_id)

        return queryset


class QuestionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def retrieve(self, request, *args, **kwargs):
        try:
            question = self.get_object()

            # Get answer details
            answer_data = []
            for answer in question.answer.all():
                answer_data.append({
                    'id': answer.id,
                    'answer_text': answer.answer_text,
                    'is_correct': answer.is_correct
                })

            # Return the question data
            return Response({
                'id': question.id,
                'lesson': question.lesson.id if question.lesson else None,
                'question_text': question.question_text,
                'explanation': question.explanation,
                'answer': answer_data,
                'created_at': question.created_at,
                'updated_at': question.updated_at
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            question = self.get_object()

            # Get data from request
            lesson_id = request.data.get('lesson')
            question_text = request.data.get('question_text')
            explanation = request.data.get('explanation')
            answer_ids = request.data.get('answer')

            # Update fields if provided
            if lesson_id is not None:
                try:
                    lesson = Lesson.objects.get(id=lesson_id)
                    question.lesson = lesson
                except Lesson.DoesNotExist:
                    return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)
            if question_text is not None:
                question.question_text = question_text
            if explanation is not None:
                question.explanation = explanation

            question.save()

            # Update answers if provided
            if answer_ids is not None:
                answers = Answer.objects.filter(id__in=answer_ids)
                question.answer.set(answers)

            # Get updated answer details
            answer_data = []
            for answer in question.answer.all():
                answer_data.append({
                    'id': answer.id,
                    'answer_text': answer.answer_text,
                    'is_correct': answer.is_correct
                })

            # Return updated data
            return Response({
                'id': question.id,
                'lesson': question.lesson.id if question.lesson else None,
                'question_text': question.question_text,
                'explanation': question.explanation,
                'answer': answer_data,
                'created_at': question.created_at,
                'updated_at': question.updated_at
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            question = self.get_object()
            question.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ValidateAnswerView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            question_id = request.data.get('question_id')
            answer_id = request.data.get('answer_id')

            # Validate input parameters
            if not question_id:
                return Response(
                    {"error": "Question ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not answer_id:
                return Response(
                    {"error": "Answer ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if question exists
            try:
                question = Question.objects.get(id=question_id)
            except Question.DoesNotExist:
                return Response(
                    {"error": "Question not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Check if answer exists and belongs to the question
            try:
                answer = Answer.objects.get(id=answer_id)
                if not question.answer.filter(id=answer_id).exists():
                    return Response(
                        {"error": "This answer doesn't belong to the specified question"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Answer.DoesNotExist:
                return Response(
                    {"error": "Answer not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Build response based on answer correctness
            response_data = {
                'is_correct': answer.is_correct,
                'explanation': question.explanation
            }

            return Response(response_data)

        except Exception as e:
            return Response(
                {"error": f"Failed to validate answer: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
