from django.contrib import admin
from .models import Class, Attendance

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'created_at')
    search_fields = ('name', 'teacher__name')
    list_filter = ('created_at',)

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_instance', 'attendance_count')
    list_filter = ('class_instance', 'student')
    search_fields = ('student__user__name', 'class_instance__name') 