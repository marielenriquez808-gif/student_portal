from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import User
from enrollment.models import Enrollment
from .models import Schedule


@login_required
def student_schedule(request):
    if request.user.role != User.ROLE_STUDENT:
        return redirect('home')
    profile = request.user.student_profile
    enrollment = get_object_or_404(Enrollment, student=profile, status='approved')
    schedules = Schedule.objects.filter(section=enrollment.section).select_related('subject', 'instructor')
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    schedule_by_day = {day: schedules.filter(day=day) for day in days}
    return render(request, 'schedules/student_schedule.html', {
        'schedule_by_day': schedule_by_day, 'days': days, 'enrollment': enrollment
    })


@login_required
def instructor_schedule(request):
    if request.user.role != User.ROLE_INSTRUCTOR:
        return redirect('home')
    instructor = request.user.instructor_profile
    schedules = Schedule.objects.filter(instructor=instructor).select_related('subject', 'section').order_by('day', 'time_start')
    return render(request, 'schedules/instructor_schedule.html', {
        'schedules': schedules, 'instructor': instructor
    })
