from django.contrib import admin
from .models import CustomUser, Organization
from unfold.admin import ModelAdmin
# Register your models here.


class CustomUserAdmin(ModelAdmin):
    list_display = ('email', 'first_name', 'last_name',
                    'user_type', 'organization', 'phone_number')
    list_filter = ('user_type', 'organization')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Organization, ModelAdmin)
