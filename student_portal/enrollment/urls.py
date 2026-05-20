from django.urls import path
from . import views

urlpatterns = [
    path('form/', views.enrollment_form, name='enrollment_form'),
    path('copy/', views.enrollment_copy, name='enrollment_copy'),
    path('ajax/subjects/', views.get_subjects_ajax, name='get_subjects_ajax'),
]

