from django.urls import path
from . import views

urlpatterns = [
    path('student/', views.student_schedule, name='student_schedule'),
    path('instructor/', views.instructor_schedule, name='instructor_schedule'),
]
