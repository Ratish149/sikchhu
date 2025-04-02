from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Frame, GameObject, Dialogue, Quiz, QuizOption, Background
from unfold.admin import ModelAdmin, TabularInline, StackedInline


admin.site.register(Background, ModelAdmin)


class GameObjectInline(TabularInline):
    """Inline for adding multiple objects inside a Frame"""
    model = GameObject
    extra = 1  # Show one empty row by default
    tab = True


class DialogueInline(TabularInline):
    """Inline for adding dialogues linked to objects inside a Frame"""
    model = Dialogue
    extra = 1  # Show one empty row by default
    tab = True


class QuizOptionInline(TabularInline):
    """Inline for adding multiple quiz options inside a Quiz"""
    model = QuizOption
    extra = 2  # Show two empty option rows by default
    tab = True


class QuizInline(StackedInline):
    """Inline for adding a Quiz inside a Frame"""
    model = Quiz
    extra = 1  # Allow adding quiz directly in Frame
    inlines = [QuizOptionInline]  # Nested quiz options
    tab = True


@admin.register(Frame)
class FrameAdmin(ModelAdmin):
    list_display = ('chapter', 'name', 'frame_type',
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
    inlines = [QuizOptionInline]


@admin.register(QuizOption)
class QuizOptionAdmin(ModelAdmin):
    list_display = ('text', 'quiz', 'is_correct')
    list_filter = ('is_correct',)
