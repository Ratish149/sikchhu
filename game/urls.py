from django.urls import path
from . import views

urlpatterns = [
    # Background routes
    path('backgrounds/', views.BackgroundListCreateView.as_view(),
         name='background-list-create'),
    path('backgrounds/<int:pk>/',
         views.BackgroundRetrieveUpdateDestroyView.as_view(), name='background-detail'),

    # Frame routes
    path('frames/', views.FrameListCreateView.as_view(), name='frame-list-create'),
    path('frames/<int:pk>/',
         views.FrameRetrieveUpdateDestroyView.as_view(), name='frame-detail'),

    # GameObject routes
    path('objects/', views.GameObjectListCreateView.as_view(),
         name='gameobject-list-create'),
    path('objects/<int:pk>/', views.GameObjectRetrieveUpdateDestroyView.as_view(),
         name='gameobject-detail'),

    # Dialogue routes
    path('dialogues/', views.DialogueListCreateView.as_view(),
         name='dialogue-list-create'),
    path('dialogues/<int:pk>/',
         views.DialogueRetrieveUpdateDestroyView.as_view(), name='dialogue-detail'),

    # QuizOption routes
    path('quiz-options/', views.QuizOptionListCreateView.as_view(),
         name='quizoption-list-create'),
    path('quiz-options/<int:pk>/',
         views.QuizOptionRetrieveUpdateDestroyView.as_view(), name='quizoption-detail'),

    # Quiz routes
    path('quizzes/', views.QuizListCreateView.as_view(), name='quiz-list-create'),
    path('quizzes/<int:pk>/',
         views.QuizRetrieveUpdateDestroyView.as_view(), name='quiz-detail'),
    path('validate-quiz-answer/', views.ValidateQuizAnswerView.as_view(),
         name='validate-quiz-answer'),

    # UserProgress routes
    path('progress/', views.UserProgressListCreateView.as_view(),
         name='progress-list-create'),
    path('progress/<int:pk>/',
         views.UserProgressRetrieveUpdateDestroyView.as_view(), name='progress-detail'),
]
