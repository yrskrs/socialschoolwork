"""Admin реєстрація моделей SchoolNet."""

from django.contrib import admin
from .models import Subject, ClassGroup, Teacher, Assignment, AssignmentFile


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'color']
    search_fields = ['name']


@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'grade', 'letter']
    ordering = ['grade', 'letter']


class AssignmentFileInline(admin.TabularInline):
    model = AssignmentFile
    extra = 1
    readonly_fields = ['uploaded_at']


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'avatar_color']
    filter_horizontal = ['subjects', 'classes']
    search_fields = ['full_name', 'user__username']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'subject', 'status', 'published_at', 'created_at']
    list_filter = ['status', 'subject', 'classes']
    search_fields = ['title', 'description', 'student_name']
    filter_horizontal = ['classes']
    inlines = [AssignmentFileInline]
    readonly_fields = ['created_at', 'updated_at', 'published_at']
    date_hierarchy = 'created_at'


@admin.register(AssignmentFile)
class AssignmentFileAdmin(admin.ModelAdmin):
    list_display = ['original_name', 'assignment', 'uploaded_at']
    readonly_fields = ['uploaded_at']
