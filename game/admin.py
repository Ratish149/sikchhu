from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Frame, GameObject, Dialogue, Quiz, QuizOption, Background, UserProgress
from unfold.admin import ModelAdmin, TabularInline


admin.site.register(Background, ModelAdmin)


class GameObjectInline(TabularInline):
    """Inline for adding GameObjects linked to a Frame"""
    model = GameObject
    extra = 1
    tab = True


class DialogueInline(TabularInline):
    """Inline for adding dialogues linked to objects inside a Frame"""
    model = Dialogue
    extra = 1  # Show one empty row by default
    tab = True


class QuizInline(TabularInline):
    """Inline for adding a Quiz inside a Frame"""
    model = Quiz
    extra = 1  # Allow adding quiz directly in Frame
    tab = True


@admin.register(Frame)
class FrameAdmin(ModelAdmin):
    list_display = ('lesson', 'name', 'frame_type',
                    'previous_frame', 'get_next_frame')
    list_filter = ('frame_type',)
    search_fields = ('id', 'frame_type')

    inlines = [GameObjectInline, DialogueInline, QuizInline]

    def get_next_frame(self, obj):
        """Show the next frame in the admin panel"""
        return obj.get_next_frame()
    get_next_frame.short_description = "Next Frame"


@admin.register(GameObject)
class GameObjectAdmin(ModelAdmin):
    list_display = ('name', 'frame', 'preview_object')
    search_fields = ('name',)

    def preview_object(self, obj):
        """Show object image preview"""
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
        return "No Image"
    preview_object.short_description = "Object Image"


@admin.register(Dialogue)
class DialogueAdmin(ModelAdmin):
    list_display = ('game_object', 'frame', 'text_short')
    search_fields = ('text',)

    def text_short(self, obj):
        """Shorten text for display"""
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    text_short.short_description = "Dialogue"


@admin.register(Quiz)
class QuizAdmin(ModelAdmin):
    list_display = ('question', 'frame')


@admin.register(QuizOption)
class QuizOptionAdmin(ModelAdmin):
    list_display = ('text', 'is_correct')
    list_filter = ('is_correct',)


@admin.register(UserProgress)
class UserProgressAdmin(ModelAdmin):
    list_display = ('user', 'lesson', 'current_frame', 'score')
    list_filter = ('lesson',)
    search_fields = ('user__username', 'lesson__name')
