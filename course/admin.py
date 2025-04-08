from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from tinymce.widgets import TinyMCE
from django.db import models
from .models import Class, Subject, Chapter, Lesson, Video, LearningMaterial, Question, LessonReview, QuestionOption
# Register your models here.


class TinyMCEWidget(TinyMCE):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({'class': 'tinymce'})


class LearningMaterialInline(TabularInline):
    model = LearningMaterial
    extra = 1
    tab = True


class VideoInline(TabularInline):
    model = Video
    extra = 1
    tab = True


class QuestionOptionInline(TabularInline):
    model = QuestionOption
    extra = 1
    tab = True
    fields = ('option', 'is_correct', 'explanation')


class QuestionInline(StackedInline):
    inlines = [QuestionOptionInline]
    model = Question
    extra = 1
    tab = True


class QuestionAdmin(ModelAdmin):
    inlines = [QuestionOptionInline]
    list_display = ('question_text', 'lesson', 'created_at')
    search_fields = ('question_text', 'lesson__name')
    list_filter = ('lesson', 'created_at')
    fields = ('lesson', 'question_text', 'explanation')


class ChapterAdmin(ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': TinyMCEWidget}
    }


class LessonAdmin(ModelAdmin):
    inlines = [VideoInline, LearningMaterialInline, QuestionInline]
    formfield_overrides = {
        models.TextField: {'widget': TinyMCEWidget}
    }


class LessonReviewAdmin(ModelAdmin):
    list_display = ('lesson', 'review_text', 'rating',
                    'created_at', 'updated_at')
    search_fields = ('lesson__name', 'review_text')
    list_filter = ('lesson__name', 'rating')


admin.site.register(Class, ModelAdmin)
admin.site.register(Subject, ModelAdmin)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Video, ModelAdmin)
admin.site.register(LearningMaterial, ModelAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(LessonReview, LessonReviewAdmin)
