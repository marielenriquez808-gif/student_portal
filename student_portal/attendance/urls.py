from django.urls import path
from . import views

urlpatterns = [
    path('student/', views.student_attendance, name='student_attendance'),
    path('instructor/', views.instructor_attendance, name='instructor_attendance'),
    path('sheet/<int:subject_pk>/', views.attendance_sheet, name='attendance_sheet'),
    path('delete/<int:pk>/', views.attendance_delete, name='attendance_delete'),
]
