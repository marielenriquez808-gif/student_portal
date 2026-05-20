from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from accounts.models import User
from .models import Enrollment, EducationalBackground, Section, Subject
from .forms import EnrollmentForm, EducationalBackgroundForm


@login_required
def enrollment_form(request):
    if request.user.role != User.ROLE_STUDENT:
        return redirect('home')
    profile = request.user.student_profile
    existing = getattr(profile, 'enrollment', None)
    if existing and existing.status == 'approved':
        messages.info(request, "You are already enrolled and approved.")
        return redirect('student_dashboard')

    enroll_form = EnrollmentForm(request.POST or None, student=profile, instance=existing)
    edu_form = EducationalBackgroundForm(
        request.POST or None,
        instance=getattr(existing, 'educational_background', None) if existing else None
    )

    if request.method == 'POST' and enroll_form.is_valid() and edu_form.is_valid():
        enrollment = enroll_form.save(commit=False)
        enrollment.student = profile
        enrollment.status = Enrollment.STATUS_PENDING
        enrollment.save()
        enroll_form.save_m2m()

        edu = edu_form.save(commit=False)
        edu.enrollment = enrollment
        edu.save()

        messages.success(request, "Enrollment submitted! Please wait for admin approval.")
        return redirect('student_landing')

    # Build selected subject ID list for JS pre-selection
    selected_subject_ids = []
    current_semester = ''
    if request.method == 'POST':
        current_semester = request.POST.get('semester', '')
        selected_subject_ids = [
            int(x) for x in request.POST.getlist('subjects') if x.isdigit()
        ]
    elif existing:
        current_semester = existing.semester
        selected_subject_ids = list(existing.subjects.values_list('id', flat=True))

    return render(request, 'enrollment/enrollment_form.html', {
        'enroll_form': enroll_form,
        'edu_form': edu_form,
        'profile': profile,
        'current_semester': current_semester,
        'selected_subject_ids': selected_subject_ids,
    })


@login_required
def enrollment_copy(request):
    if request.user.role != User.ROLE_STUDENT:
        return redirect('home')
    profile = request.user.student_profile
    enrollment = get_object_or_404(Enrollment, student=profile)
    return render(request, 'enrollment/enrollment_copy.html', {
        'enrollment': enrollment,
        'profile': profile,
    })


def get_subjects_ajax(request):
    dept_id = request.GET.get('department')
    program_id = request.GET.get('program')
    year_level = request.GET.get('year_level')
    semester = request.GET.get('semester')

    qs = Subject.objects.filter(
        department_id=dept_id,
        program_id=program_id,
        year_level=year_level,
    ).order_by('code')

    if semester:
        qs = qs.filter(semester=semester)

    subjects = list(qs.values('id', 'code', 'name', 'units', 'semester'))
    return JsonResponse({'subjects': subjects})
