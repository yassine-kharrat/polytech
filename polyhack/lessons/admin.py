from django.contrib import admin
from .models import Lesson

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'class_instance', 'created_at')
    list_filter = ('class_instance', 'created_at')
    search_fields = ('title', 'content', 'class_instance__name')
    date_hierarchy = 'created_at' 