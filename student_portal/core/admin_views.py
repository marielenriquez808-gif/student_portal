from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from accounts.models import User, StudentProfile, InstructorProfile, Department, Program
from enrollment.models import Enrollment, Section, Subject
from enrollment.forms import SubjectForm
from grades.models import Grade
from attendance.models import Attendance
from schedules.models import Schedule
from schedules.forms import ScheduleForm
from announcements.models import Announcement


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.ROLE_ADMIN:
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def admin_dashboard(request):
    context = {
        'total_students': StudentProfile.objects.count(),
        'total_instructors': InstructorProfile.objects.count(),
        'total_subjects': Subject.objects.count(),
        'pending_enrollments': Enrollment.objects.filter(status='pending').count(),
        'approved_enrollments': Enrollment.objects.filter(status='approved').count(),
        'announcements': Announcement.objects.filter(is_active=True)[:5],
    }
    return render(request, 'admin/dashboard.html', context)


# ─── Student Admin Panel ─────────────────────────────────────────────────────
@admin_required
def admin_students(request):
    dept = request.GET.get('dept')
    course = request.GET.get('course')
    year = request.GET.get('year')
    enrollments = Enrollment.objects.select_related('student', 'student__department', 'student__program')
    if dept:
        enrollments = enrollments.filter(student__department_id=dept)
    if course:
        enrollments = enrollments.filter(student__program_id=course)
    if year:
        enrollments = enrollments.filter(student__year_level=year)
    paginator = Paginator(enrollments, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin/students.html', {
        'enrollments': page_obj,
        'page_obj': page_obj,
        'departments': Department.objects.all(),
        'programs': Program.objects.all(),
    })


@admin_required
def enrollment_detail(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    return render(request, 'admin/enrollment_detail.html', {'enrollment': enrollment})


@admin_required
def approve_enrollment(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    if request.method == 'POST':
        # Auto-assign section
        section = _auto_assign_section(enrollment.student)
        enrollment.section = section
        enrollment.status = Enrollment.STATUS_APPROVED
        enrollment.approved_at = timezone.now()
        enrollment.save()
        if section:
            section.current_count += 1
            section.save()
        messages.success(request, f"Enrollment approved. Assigned to Section {section.name if section else 'N/A'}.")
    return redirect('admin_students')


@admin_required
def reject_enrollment(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    if request.method == 'POST':
        enrollment.status = Enrollment.STATUS_REJECTED
        enrollment.remarks = request.POST.get('remarks', '')
        enrollment.save()
        messages.warning(request, "Enrollment rejected.")
    return redirect('admin_students')


def _auto_assign_section(student):
    for section_name in ['A', 'B', 'C', 'D']:
        section, created = Section.objects.get_or_create(
            name=section_name,
            department=student.department,
            program=student.program,
            year_level=student.year_level,
            defaults={'max_slots': 40, 'current_count': 0}
        )
        if not section.is_full():
            return section
    return None


# ─── Instructor Admin Panel ──────────────────────────────────────────────────
@admin_required
def admin_instructors(request):
    instructors = InstructorProfile.objects.select_related('department', 'program')
    paginator = Paginator(instructors, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin/instructors.html', {
        'instructors': page_obj,
        'page_obj': page_obj,
    })


@admin_required
def assign_subject(request, instructor_pk):
    instructor = get_object_or_404(InstructorProfile, pk=instructor_pk)
    subjects = Subject.objects.filter(department=instructor.department)
    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        subject = get_object_or_404(Subject, pk=subject_id)
        subject.assigned_instructor = instructor
        subject.save()
        messages.success(request, f"Subject {subject.code} assigned to {instructor.full_name}.")
        return redirect('admin_instructors')
    return render(request, 'admin/assign_subject.html', {
        'instructor': instructor, 'subjects': subjects
    })


# ─── Subject Management ───────────────────────────────────────────────────────
@admin_required
def admin_subjects(request):
    subjects = Subject.objects.select_related('department', 'program').order_by(
        'department', 'program', 'year_level', 'semester', 'code'
    )
    dept_filter = request.GET.get('dept')
    prog_filter = request.GET.get('prog')
    year_filter = request.GET.get('year')
    sem_filter = request.GET.get('sem')
    if dept_filter:
        subjects = subjects.filter(department_id=dept_filter)
    if prog_filter:
        subjects = subjects.filter(program_id=prog_filter)
    if year_filter:
        subjects = subjects.filter(year_level=year_filter)
    if sem_filter:
        subjects = subjects.filter(semester=sem_filter)
    paginator = Paginator(subjects, 50)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin/subjects.html', {
        'subjects': page_obj,
        'page_obj': page_obj,
        'departments': Department.objects.all(),
        'programs': Program.objects.all(),
    })


@admin_required
def admin_subject_create(request):
    form = SubjectForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Subject created successfully.")
        return redirect('admin_subjects')
    return render(request, 'admin/subject_form.html', {'form': form, 'action': 'Create'})


@admin_required
def admin_subject_edit(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    form = SubjectForm(request.POST or None, instance=subject)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Subject updated successfully.")
        return redirect('admin_subjects')
    return render(request, 'admin/subject_form.html', {'form': form, 'action': 'Edit', 'subject': subject})


@admin_required
def admin_subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject.delete()
        messages.success(request, "Subject deleted.")
    return redirect('admin_subjects')


# ─── Schedule Management ──────────────────────────────────────────────────────
@admin_required
def admin_schedules(request):
    schedules = Schedule.objects.select_related(
        'instructor', 'subject', 'section'
    ).order_by('instructor__full_name', 'day', 'time_start')

    instructor_filter = request.GET.get('instructor')
    day_filter = request.GET.get('day')
    semester_filter = request.GET.get('semester')
    if instructor_filter:
        schedules = schedules.filter(instructor_id=instructor_filter)
    if day_filter:
        schedules = schedules.filter(day=day_filter)
    if semester_filter:
        schedules = schedules.filter(semester=semester_filter)

    paginator = Paginator(schedules, 30)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin/schedules.html', {
        'schedules': page_obj,
        'page_obj': page_obj,
        'instructors': InstructorProfile.objects.select_related('user').all(),
    })


@admin_required
def admin_schedule_create(request):
    form = ScheduleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Schedule created successfully.")
        return redirect('admin_schedules')
    return render(request, 'admin/schedule_form.html', {'form': form, 'action': 'Create'})


@admin_required
def admin_schedule_edit(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    form = ScheduleForm(request.POST or None, instance=schedule)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Schedule updated successfully.")
        return redirect('admin_schedules')
    return render(request, 'admin/schedule_form.html', {'form': form, 'action': 'Edit', 'schedule': schedule})


@admin_required
def admin_schedule_delete(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, "Schedule deleted.")
    return redirect('admin_schedules')


# ─── Deleted Records / Restore ────────────────────────────────────────────────
@admin_required
def admin_deleted_records(request):
    deleted_grades = Grade.deleted_objects.select_related(
        'enrollment__student', 'subject', 'instructor'
    ).order_by('-deleted_at')

    deleted_attendance = Attendance.deleted_objects.select_related(
        'enrollment__student', 'subject', 'instructor'
    ).order_by('-deleted_at')

    deleted_announcements = Announcement.deleted_objects.select_related('author').order_by('-deleted_at')

    deleted_enrollments = Enrollment.deleted_objects.select_related(
        'student', 'student__department', 'student__program'
    ).order_by('-deleted_at')

    return render(request, 'admin/deleted_records.html', {
        'deleted_grades': deleted_grades,
        'deleted_attendance': deleted_attendance,
        'deleted_announcements': deleted_announcements,
        'deleted_enrollments': deleted_enrollments,
    })


@admin_required
def admin_restore_grade(request, pk):
    grade = get_object_or_404(Grade.all_objects, pk=pk, is_deleted=True)
    if request.method == 'POST':
        grade.restore()
        messages.success(request, f"Grade for {grade.enrollment.student.full_name} ({grade.subject.code}) restored.")
    return redirect('admin_deleted_records')


@admin_required
def admin_restore_attendance(request, pk):
    record = get_object_or_404(Attendance.all_objects, pk=pk, is_deleted=True)
    if request.method == 'POST':
        record.restore()
        messages.success(request, f"Attendance record for {record.enrollment.student.full_name} on {record.date} restored.")
    return redirect('admin_deleted_records')


@admin_required
def admin_restore_announcement(request, pk):
    ann = get_object_or_404(Announcement.all_objects, pk=pk, is_deleted=True)
    if request.method == 'POST':
        ann.restore()
        messages.success(request, f"Announcement '{ann.title}' restored.")
    return redirect('admin_deleted_records')


@admin_required
def admin_restore_enrollment(request, pk):
    enrollment = get_object_or_404(Enrollment.all_objects, pk=pk, is_deleted=True)
    if request.method == 'POST':
        enrollment.restore()
        messages.success(request, f"Enrollment for {enrollment.student.full_name} restored.")
    return redirect('admin_deleted_records')
