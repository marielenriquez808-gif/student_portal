from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from accounts.models import User
from enrollment.models import Enrollment, Subject
from .models import Grade
from .forms import GradeForm


@login_required
def student_grades(request):
    if request.user.role != User.ROLE_STUDENT:
        return redirect('home')
    profile = request.user.student_profile
    enrollment = get_object_or_404(Enrollment, student=profile, status='approved')
    grades = Grade.objects.filter(enrollment=enrollment).select_related('subject')
    gwa = grades.aggregate(avg=Avg('final_grade'))['avg'] or 0
    return render(request, 'grades/student_grades.html', {
        'grades': grades, 'gwa': round(gwa, 2), 'enrollment': enrollment
    })


@login_required
def instructor_grades(request):
    if request.user.role != User.ROLE_INSTRUCTOR:
        return redirect('home')
    instructor = request.user.instructor_profile
    subjects = Subject.objects.filter(assigned_instructor=instructor)

    subject_data = []
    for subject in subjects:
        enrollments = Enrollment.objects.filter(
            subjects=subject, status='approved'
        ).select_related('student').order_by('student__full_name')

        grades_map = {
            g.enrollment_id: g
            for g in Grade.objects.filter(subject=subject, instructor=instructor)
        }

        rows = [
            {'enrollment': e, 'grade': grades_map.get(e.id)}
            for e in enrollments
        ]
        subject_data.append({'subject': subject, 'rows': rows})

    return render(request, 'grades/instructor_grades.html', {
        'subject_data': subject_data, 'instructor': instructor
    })


@login_required
def grade_add(request, subject_pk, enrollment_pk):
    if request.user.role != User.ROLE_INSTRUCTOR:
        return redirect('home')
    instructor = request.user.instructor_profile
    subject = get_object_or_404(Subject, pk=subject_pk, assigned_instructor=instructor)
    enrollment = get_object_or_404(Enrollment, pk=enrollment_pk, subjects=subject, status='approved')

    existing = Grade.all_objects.filter(enrollment=enrollment, subject=subject).first()
    if existing:
        if existing.is_deleted:
            existing.restore()
            messages.info(request, "Restored previously deleted grade record.")
            return redirect('instructor_grades')
        messages.warning(request, "Grade already exists. Use Edit to modify.")
        return redirect('instructor_grades')

    form = GradeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        grade = form.save(commit=False)
        grade.enrollment = enrollment
        grade.subject = subject
        grade.instructor = instructor
        grade.save()
        messages.success(request, f"Grade added for {enrollment.student.full_name}.")
        return redirect('instructor_grades')

    return render(request, 'grades/grade_form.html', {
        'form': form,
        'title': 'Add Grade',
        'subject': subject,
        'enrollment': enrollment,
    })


@login_required
def grade_update(request, pk):
    if request.user.role != User.ROLE_INSTRUCTOR:
        return redirect('home')
    instructor = request.user.instructor_profile
    grade = get_object_or_404(Grade, pk=pk, instructor=instructor)
    form = GradeForm(request.POST or None, instance=grade)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Grade updated.")
        return redirect('instructor_grades')
    return render(request, 'grades/grade_form.html', {
        'form': form,
        'title': 'Edit Grade',
        'subject': grade.subject,
        'enrollment': grade.enrollment,
    })


@login_required
def grade_delete(request, pk):
    if request.user.role != User.ROLE_INSTRUCTOR:
        return redirect('home')
    instructor = request.user.instructor_profile
    grade = get_object_or_404(Grade, pk=pk, instructor=instructor)
    if request.method == 'POST':
        grade.delete()
        messages.success(request, "Grade deleted.")
    return redirect('instructor_grades')
