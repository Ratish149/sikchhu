from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Blog, BlogCategory, BlogTag
from tinymce.widgets import TinyMCE
from django.db import models
# Register your models here.


admin.site.register(BlogCategory, ModelAdmin)
admin.site.register(BlogTag, ModelAdmin)


class BlogAdmin(ModelAdmin):
    list_display = ('title', 'slug', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE(attrs={'cols': 80, 'rows': 30})},
    }


admin.site.register(Blog, BlogAdmin)
