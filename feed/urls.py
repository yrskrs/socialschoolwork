"""Маршрути застосунку feed для SchoolNet."""

from django.urls import path
from . import views

urlpatterns = [
    # ── Публічна частина ──────────────────────────────────────────────────────
    path('', views.index, name='index'),
    path('feed/fragment/', views.feed_fragment, name='feed_fragment'),
    path('feed/calendar/', views.calendar_fragment, name='calendar_fragment'),
    path('feed/check-updates/', views.feed_check_updates, name='feed_check_updates'),
    path('api/server-stats/', views.server_stats, name='server_stats'),
    path('api/heartbeat/', views.client_heartbeat, name='client_heartbeat'),
    path('api/client-disconnect/', views.client_disconnect, name='client_disconnect'),
    path('assignment/<int:pk>/', views.assignment_detail, name='assignment_detail'),
    path('clear-class/', views.clear_class_filter, name='clear_class_filter'),

    # ── Авторизація вчителя ───────────────────────────────────────────────────
    path('teacher/login/', views.teacher_login, name='teacher_login'),
    path('teacher/logout/', views.teacher_logout, name='teacher_logout'),

    # ── Панель вчителя ────────────────────────────────────────────────────────
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/profile/', views.teacher_profile, name='teacher_profile'),

    # ── CRUD завдань ──────────────────────────────────────────────────────────
    path('teacher/assignment/create/', views.assignment_create, name='assignment_create'),
    path('teacher/assignment/<int:pk>/edit/', views.assignment_edit, name='assignment_edit'),
    path('teacher/assignment/<int:pk>/delete/', views.assignment_delete, name='assignment_delete'),
    path('teacher/assignment/<int:pk>/duplicate/', views.assignment_duplicate, name='assignment_duplicate'),
    path('teacher/assignment/<int:pk>/archive/', views.assignment_archive, name='assignment_archive'),
    path('teacher/assignment/<int:pk>/unarchive/', views.assignment_unarchive, name='assignment_unarchive'),
    path('teacher/assignment/<int:pk>/publish/', views.assignment_publish, name='assignment_publish'),
    # ── Перегляд файлів (docx, pdf, code тощо) ──────────────────────────────────
    path('assignment/file/<int:file_id>/preview/', views.file_preview, name='file_preview'),
    path('assignment/file/<int:file_id>/view/', views.file_view, name='file_view'),
]
