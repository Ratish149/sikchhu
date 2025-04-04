from django.urls import path
from . import views

urlpatterns = [
    # Class URLs
    path('classes/', views.ClassListCreateView.as_view(), name='class-list-create'),
    path('classes/<slug:slug>/',
         views.ClassRetrieveUpdateDestroyView.as_view(), name='class-detail'),

    # Subject URLs
    path('subjects/', views.SubjectListCreateView.as_view(),
         name='subject-list-create'),
    path('subjects/<slug:slug>/',
         views.SubjectRetrieveUpdateDestroyView.as_view(), name='subject-detail'),

    # Chapter URLs
    path('chapters/', views.ChapterListCreateView.as_view(),
         name='chapter-list-create'),
    path('chapters/<slug:slug>/',
         views.ChapterRetrieveUpdateDestroyView.as_view(), name='chapter-detail'),

    # Lesson URLs
    path('lessons/', views.LessonListCreateView.as_view(),
         name='lesson-list-create'),
    path('lessons/<slug:slug>/',
         views.LessonRetrieveUpdateDestroyView.as_view(), name='lesson-detail'),

    # Video URLs
    path('videos/', views.VideoListCreateView.as_view(), name='video-list-create'),
    path('videos/<slug:slug>/',
         views.VideoRetrieveUpdateDestroyView.as_view(), name='video-detail'),

    # Learning Material URLs
    path('learning-materials/', views.LearningMaterialListCreateView.as_view(),
         name='learning-material-list-create'),
    path('learning-materials/<int:pk>/',
         views.LearningMaterialRetrieveUpdateDestroyView.as_view(), name='learning-material-detail'),

    # Answer URLs
    path('answers/', views.AnswerListCreateView.as_view(),
         name='answer-list-create'),
    path('answers/<int:pk>/',
         views.AnswerRetrieveUpdateDestroyView.as_view(), name='answer-detail'),

    # Question URLs
    path('questions/', views.QuestionListCreateView.as_view(),
         name='question-list-create'),
    path('questions/<int:pk>/',
         views.QuestionRetrieveUpdateDestroyView.as_view(), name='question-detail'),

    # Validate Answer URLs
    path('validate-answer/', views.ValidateAnswerView.as_view(),
         name='validate-answer'),
]
