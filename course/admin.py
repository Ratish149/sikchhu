from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from tinymce.widgets import TinyMCE
from django.db import models
from .models import Class, Subject, Chapter, Lesson, Video, LearningMaterial, Question, Answer, LessonReview
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


class QuestionInline(TabularInline):
    model = Question
    extra = 1
    tab = True


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
admin.site.register(Question, ModelAdmin)
admin.site.register(Answer, ModelAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(LessonReview, LessonReviewAdmin)
