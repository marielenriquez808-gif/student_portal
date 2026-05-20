from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from accounts.models import User


def home(request):
    if request.user.is_authenticated:
        if request.user.role == User.ROLE_STUDENT:
            return redirect('student_landing')
        elif request.user.role == User.ROLE_INSTRUCTOR:
            return redirect('instructor_dashboard')
        elif request.user.role == User.ROLE_ADMIN:
            return redirect('admin_dashboard')
    return render(request, 'core/home.html')


@login_required
def student_landing(request):
    if request.user.role != User.ROLE_STUDENT:
        return redirect('home')
    profile = request.user.student_profile
    enrollment = getattr(profile, 'enrollment', None)
    return render(request, 'core/student_landing.html', {
        'profile': profile,
        'enrollment': enrollment,
    })


@login_required
def student_dashboard(request):
    if request.user.role != User.ROLE_STUDENT:
        return redirect('home')
    profile = request.user.student_profile
    enrollment = getattr(profile, 'enrollment', None)

    if not enrollment or enrollment.status != 'approved':
        return redirect('student_landing')

    from grades.models import Grade
    from attendance.models import Attendance
    from announcements.models import Announcement
    from schedules.models import Schedule
    import datetime

    grades = Grade.objects.filter(enrollment=enrollment)
    gwa = grades.aggregate(avg=Avg('final_grade'))['avg'] or 0

    total_att = Attendance.objects.filter(enrollment=enrollment).count()
    present_att = Attendance.objects.filter(enrollment=enrollment, status='present').count()
    att_rate = round((present_att / total_att * 100) if total_att > 0 else 0, 1)

    today = datetime.date.today().strftime('%A').lower()
    schedules = Schedule.objects.filter(section=enrollment.section, day=today)
    announcements = Announcement.objects.filter(is_active=True)[:5]

    return render(request, 'core/student_dashboard.html', {
        'profile': profile,
        'enrollment': enrollment,
        'gwa': round(gwa, 2),
        'att_rate': att_rate,
        'subjects_count': enrollment.subjects.count(),
        'schedules': schedules,
        'announcements': announcements,
        'grades': grades,
    })
