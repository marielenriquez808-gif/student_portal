from datetime import date as date_cls
from django.db.models import Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from accounts.models import User
from enrollment.models import Subject, Enrollment, Section
from grades.models import Grade
from attendance.models import Attendance


@login_required
def instructor_dashboard(request):
    if request.user.role != User.ROLE_INSTRUCTOR:
        return redirect('home')
    instructor = request.user.instructor_profile
    subjects = Subject.objects.filter(assigned_instructor=instructor).select_related('department', 'program')

    subject_data = []
    total_students = 0
    for subject in subjects:
        enrollments = Enrollment.objects.filter(
            subjects=subject, status='approved'
        ).select_related('student').order_by('student__full_name')
        count = enrollments.count()
        total_students += count
        subject_data.append({
            'subject': subject,
            'enrollments': enrollments,
            'count': count,
        })

    return render(request, 'instructor/dashboard.html', {
        'instructor': instructor,
        'subject_data': subject_data,
        'total_students': total_students,
    })


@login_required
def instructor_report(request):
    if request.user.role != User.ROLE_INSTRUCTOR:
        return redirect('home')

    instructor = request.user.instructor_profile
    all_subjects = Subject.objects.filter(
        assigned_instructor=instructor
    ).select_related('department', 'program').order_by('year_level', 'code')

    # --- Parse filters ---
    subject_filter = request.GET.get('subject', '').strip()
    year_filter = request.GET.get('year_level', '').strip()
    section_filter = request.GET.get('section', '').strip()
    date_from_str = request.GET.get('date_from', '').strip()
    date_to_str = request.GET.get('date_to', '').strip()

    date_from = date_to = None
    try:
        if date_from_str:
            date_from = date_cls.fromisoformat(date_from_str)
    except ValueError:
        pass
    try:
        if date_to_str:
            date_to = date_cls.fromisoformat(date_to_str)
    except ValueError:
        pass

    subjects = all_subjects
    if subject_filter:
        subjects = subjects.filter(pk=subject_filter)

    # --- Build report rows ---
    report_data = []
    for subject in subjects:
        enrollments = Enrollment.objects.filter(
            subjects=subject, status='approved'
        ).select_related('student', 'section', 'student__program').order_by('student__full_name')

        if year_filter:
            enrollments = enrollments.filter(student__year_level=year_filter)
        if section_filter:
            enrollments = enrollments.filter(section_id=section_filter)

        if not enrollments.exists():
            continue

        grades_map = {
            g.enrollment_id: g
            for g in Grade.objects.filter(subject=subject, instructor=instructor)
        }

        att_filter = Q(attendance_records__subject=subject, attendance_records__instructor=instructor)
        if date_from:
            att_filter &= Q(attendance_records__date__gte=date_from)
        if date_to:
            att_filter &= Q(attendance_records__date__lte=date_to)

        att_stats = {
            row['id']: row
            for row in enrollments.annotate(
                att_total=Count('attendance_records', filter=att_filter),
                att_present=Count('attendance_records', filter=att_filter & Q(attendance_records__status=Attendance.STATUS_PRESENT)),
                att_late=Count('attendance_records', filter=att_filter & Q(attendance_records__status=Attendance.STATUS_LATE)),
                att_absent=Count('attendance_records', filter=att_filter & Q(attendance_records__status=Attendance.STATUS_ABSENT)),
                att_excused=Count('attendance_records', filter=att_filter & Q(attendance_records__status=Attendance.STATUS_EXCUSED)),
            ).values('id', 'att_total', 'att_present', 'att_late', 'att_absent', 'att_excused')
        }

        rows = []
        for enrollment in enrollments:
            stats = att_stats.get(enrollment.id, {})
            total = stats.get('att_total', 0)
            present = stats.get('att_present', 0)
            late = stats.get('att_late', 0)
            absent = stats.get('att_absent', 0)
            excused = stats.get('att_excused', 0)
            attended = present + late
            rate = round((attended / total * 100) if total > 0 else 0, 1)
            rows.append({
                'enrollment': enrollment,
                'grade': grades_map.get(enrollment.id),
                'att': {
                    'total': total,
                    'present': present,
                    'late': late,
                    'absent': absent,
                    'excused': excused,
                    'rate': rate,
                },
            })

        graded = sum(1 for r in rows if r['grade'])
        no_grade = len(rows) - graded
        total_present = sum(r['att']['present'] for r in rows)
        total_late = sum(r['att']['late'] for r in rows)
        total_absent = sum(r['att']['absent'] for r in rows)
        total_excused = sum(r['att']['excused'] for r in rows)
        total_sessions = sum(r['att']['total'] for r in rows)
        avg_rate = round(
            (sum(r['att']['rate'] for r in rows) / len(rows)) if rows else 0, 1
        )
        report_data.append({
            'subject': subject,
            'rows': rows,
            'totals': {
                'graded': graded,
                'no_grade': no_grade,
                'present': total_present,
                'late': total_late,
                'absent': total_absent,
                'excused': total_excused,
                'sessions': total_sessions,
                'avg_rate': avg_rate,
            },
        })

    return render(request, 'instructor/report.html', {
        'instructor': instructor,
        'all_subjects': all_subjects,
        'sections': Section.objects.all().order_by('program__code', 'year_level', 'name'),
        'report_data': report_data,
        'filters': {
            'subject': subject_filter,
            'year_level': year_filter,
            'section': section_filter,
            'date_from': date_from_str,
            'date_to': date_to_str,
        },
        'today': timezone.localdate(),
    })


@login_required
def instructor_deleted_records(request):
    if request.user.role != User.ROLE_INSTRUCTOR:
        return redirect('home')
    instructor = request.user.instructor_profile

    deleted_grades = Grade.deleted_objects.filter(
        instructor=instructor
    ).select_related('enrollment__student', 'subject').order_by('-deleted_at')

    deleted_attendance = Attendance.deleted_objects.filter(
        instructor=instructor
    ).select_related('enrollment__student', 'subject').order_by('-deleted_at')

    return render(request, 'instructor/deleted_records.html', {
        'instructor': instructor,
        'deleted_grades': deleted_grades,
        'deleted_attendance': deleted_attendance,
    })


@login_required
def instructor_restore_grade(request, pk):
    if request.user.role != User.ROLE_INSTRUCTOR:
        return redirect('home')
    instructor = request.user.instructor_profile
    grade = get_object_or_404(Grade.all_objects, pk=pk, instructor=instructor, is_deleted=True)
    if request.method == 'POST':
        grade.restore()
        messages.success(request, f"Grade for {grade.enrollment.student.full_name} ({grade.subject.code}) restored.")
    return redirect('instructor_deleted_records')


@login_required
def instructor_restore_attendance(request, pk):
    if request.user.role != User.ROLE_INSTRUCTOR:
        return redirect('home')
    instructor = request.user.instructor_profile
    record = get_object_or_404(Attendance.all_objects, pk=pk, instructor=instructor, is_deleted=True)
    if request.method == 'POST':
        record.restore()
        messages.success(request, f"Attendance for {record.enrollment.student.full_name} on {record.date} restored.")
    return redirect('instructor_deleted_records')
