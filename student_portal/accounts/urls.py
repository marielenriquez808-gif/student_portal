from django.urls import path
from . import views

urlpatterns = [
    path('student/register/', views.student_register, name='student_register'),
    path('student/login/', views.student_login, name='student_login'),
    path('instructor/register/', views.instructor_register, name='instructor_register'),
    path('instructor/login/', views.instructor_login, name='instructor_login'),
    path('admin/login/', views.admin_login, name='admin_login'),
    path('logout/', views.user_logout, name='logout'),
    path('ajax/programs/', views.get_programs, name='get_programs'),
]
