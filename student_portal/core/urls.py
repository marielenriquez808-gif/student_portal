from django.urls import path
from . import views
from .admin_views import (
    admin_dashboard, admin_students, enrollment_detail,
    approve_enrollment, reject_enrollment, admin_instructors, assign_subject,
    admin_subjects, admin_subject_create, admin_subject_edit, admin_subject_delete,
    admin_schedules, admin_schedule_create, admin_schedule_edit, admin_schedule_delete,
    admin_deleted_records,
    admin_restore_grade, admin_restore_attendance,
    admin_restore_announcement, admin_restore_enrollment,
)
from .instructor_views import (
    instructor_dashboard, instructor_report,
    instructor_deleted_records, instructor_restore_grade, instructor_restore_attendance,
)

urlpatterns = [
    path('', views.home, name='home'),
    path('student/landing/', views.student_landing, name='student_landing'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    # Admin — students
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/students/', admin_students, name='admin_students'),
    path('admin/enrollment/<int:pk>/', enrollment_detail, name='enrollment_detail'),
    path('admin/enrollment/<int:pk>/approve/', approve_enrollment, name='approve_enrollment'),
    path('admin/enrollment/<int:pk>/reject/', reject_enrollment, name='reject_enrollment'),
    # Admin — instructors
    path('admin/instructors/', admin_instructors, name='admin_instructors'),
    path('admin/instructors/<int:instructor_pk>/assign/', assign_subject, name='assign_subject'),
    # Admin — subjects
    path('admin/subjects/', admin_subjects, name='admin_subjects'),
    path('admin/subjects/create/', admin_subject_create, name='admin_subject_create'),
    path('admin/subjects/<int:pk>/edit/', admin_subject_edit, name='admin_subject_edit'),
    path('admin/subjects/<int:pk>/delete/', admin_subject_delete, name='admin_subject_delete'),
    # Admin — schedules
    path('admin/schedules/', admin_schedules, name='admin_schedules'),
    path('admin/schedules/create/', admin_schedule_create, name='admin_schedule_create'),
    path('admin/schedules/<int:pk>/edit/', admin_schedule_edit, name='admin_schedule_edit'),
    path('admin/schedules/<int:pk>/delete/', admin_schedule_delete, name='admin_schedule_delete'),
    # Admin — deleted records & restore
    path('admin/deleted/', admin_deleted_records, name='admin_deleted_records'),
    path('admin/restore/grade/<int:pk>/', admin_restore_grade, name='admin_restore_grade'),
    path('admin/restore/attendance/<int:pk>/', admin_restore_attendance, name='admin_restore_attendance'),
    path('admin/restore/announcement/<int:pk>/', admin_restore_announcement, name='admin_restore_announcement'),
    path('admin/restore/enrollment/<int:pk>/', admin_restore_enrollment, name='admin_restore_enrollment'),
    # Instructor
    path('instructor/dashboard/', instructor_dashboard, name='instructor_dashboard'),
    path('instructor/report/', instructor_report, name='instructor_report'),
    path('instructor/deleted/', instructor_deleted_records, name='instructor_deleted_records'),
    path('instructor/restore/grade/<int:pk>/', instructor_restore_grade, name='instructor_restore_grade'),
    path('instructor/restore/attendance/<int:pk>/', instructor_restore_attendance, name='instructor_restore_attendance'),
]
