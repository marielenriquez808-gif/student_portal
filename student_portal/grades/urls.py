from django.urls import path
from . import views

urlpatterns = [
    path('student/', views.student_grades, name='student_grades'),
    path('instructor/', views.instructor_grades, name='instructor_grades'),
    path('add/<int:subject_pk>/<int:enrollment_pk>/', views.grade_add, name='grade_add'),
    path('update/<int:pk>/', views.grade_update, name='grade_update'),
    path('delete/<int:pk>/', views.grade_delete, name='grade_delete'),
]
