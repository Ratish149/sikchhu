from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from tinymce.widgets import TinyMCE
from django.db import models
from .models import Class, Subject, Chapter, Lesson, Video, LearningMaterial, Question, Answer
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


class QuestionAdmin(TabularInline):
    model = Question
    extra = 1
    tab = True


class ChapterAdmin(ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': TinyMCEWidget}
    }


class LessonAdmin(ModelAdmin):
    inlines = [VideoInline, LearningMaterialInline, QuestionAdmin]
    formfield_overrides = {
        models.TextField: {'widget': TinyMCEWidget}
    }


admin.site.register(Class, ModelAdmin)
admin.site.register(Subject, ModelAdmin)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Video, ModelAdmin)
admin.site.register(LearningMaterial, ModelAdmin)
# admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, ModelAdmin)
admin.site.register(Lesson, LessonAdmin)
