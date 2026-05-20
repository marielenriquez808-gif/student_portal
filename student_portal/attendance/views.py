from datetime import date as date_cls
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from accounts.models import User
from enrollment.models import Enrollment, Subject
from .models import Attendance


@login_required
def student_attendance(request):
    if request.user.role != User.ROLE_STUDENT:
        return redirect('home')
    profile = request.user.student_profile
    enrollment = get_object_or_404(Enrollment, student=profile, status='approved')
    records = Attendance.objects.filter(enrollment=enrollment).select_related('subject').order_by('-date')
    subjects = enrollment.subjects.all()

    subject_stats = []
    for subj in subjects:
        subj_records = records.filter(subject=subj)
        total = subj_records.count()
        present = subj_records.filter(status='present').count()
        rate = round((present / total * 100) if total > 0 else 0, 1)
        subject_stats.append({'subject': subj, 'total': total, 'present': present, 'rate': rate})

    paginator = Paginator(records, 30)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'attendance/student_attendance.html', {
        'subject_stats': subject_stats,
        'all_records': page_obj,
        'page_obj': page_obj,
        'enrollment': enrollment,
    })


@login_required
def instructor_attendance(request):
    if request.user.role != User.ROLE_INSTRUCTOR:
        return redirect('home')
    instructor = request.user.instructor_profile
    subjects = Subject.objects.filter(assigned_instructor=instructor)

    subject_stats = []
    for subject in subjects:
        enrolled_count = Enrollment.objects.filter(subjects=subject, status='approved').count()
        records_count = Attendance.objects.filter(subject=subject, instructor=instructor).count()
        subject_stats.append({
            'subject': subject,
            'enrolled_count': enrolled_count,
            'records_count': records_count,
        })

    recent_records = Attendance.objects.filter(
        instructor=instructor
    ).select_related('enrollment__student', 'subject').order_by('-date', '-recorded_at')[:30]

    return render(request, 'attendance/instructor_attendance.html', {
        'subject_stats': subject_stats,
        'recent_records': recent_records,
        'instructor': instructor,
    })


@login_required
def attendance_sheet(request, subject_pk):
    if request.user.role != User.ROLE_INSTRUCTOR:
        return redirect('home')
    instructor = request.user.instructor_profile
    subject = get_object_or_404(Subject, pk=subject_pk, assigned_instructor=instructor)

    enrollments = Enrollment.objects.filter(
        subjects=subject, status='approved'
    ).select_related('student').order_by('student__full_name')

    # Resolve selected date
    today = timezone.localdate()
    date_str = request.POST.get('date') if request.method == 'POST' else request.GET.get('date', str(today))
    try:
        selected_date = date_cls.fromisoformat(date_str)
    except (ValueError, TypeError):
        selected_date = today

    if request.method == 'POST' and 'save_attendance' in request.POST:
        saved = 0
        for enrollment in enrollments:
            status = request.POST.get(f'status_{enrollment.id}', Attendance.STATUS_ABSENT)
            remarks = request.POST.get(f'remarks_{enrollment.id}', '')
            Attendance.all_objects.update_or_create(
                enrollment=enrollment,
                subject=subject,
                date=selected_date,
                defaults={
                    'status': status,
                    'instructor': instructor,
                    'remarks': remarks,
                    'is_deleted': False,
                    'deleted_at': None,
                },
            )
            saved += 1
        messages.success(request, f"Attendance saved for {selected_date.strftime('%B %d, %Y')} ({saved} students).")
        return redirect(f"{request.path}?date={selected_date}")

    # Load existing records for the selected date
    existing = {
        a.enrollment_id: a
        for a in Attendance.objects.filter(subject=subject, date=selected_date)
    }

    student_rows = [
        {'enrollment': e, 'record': existing.get(e.id)}
        for e in enrollments
    ]

    # Past dates already recorded for this subject
    past_dates = (
        Attendance.objects.filter(subject=subject, instructor=instructor)
        .values_list('date', flat=True)
        .distinct()
        .order_by('-date')[:10]
    )

    return render(request, 'attendance/attendance_sheet.html', {
        'subject': subject,
        'student_rows': student_rows,
        'selected_date': selected_date,
        'past_dates': past_dates,
        'today': today,
        'status_choices': Attendance.STATUS_CHOICES,
    })


@login_required
def attendance_delete(request, pk):
    if request.user.role != User.ROLE_INSTRUCTOR:
        return redirect('home')
    instructor = request.user.instructor_profile
    record = get_object_or_404(Attendance, pk=pk, instructor=instructor)
    if request.method == 'POST':
        record.delete()
        messages.success(request, "Record deleted.")
    return redirect('instructor_attendance')
