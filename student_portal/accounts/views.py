from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from .models import User, StudentProfile, InstructorProfile, Department, Program
from .forms import (
    StudentRegistrationForm, InstructorRegistrationForm,
    StudentLoginForm, InstructorLoginForm, AdminLoginForm
)


# ─── AJAX: Get programs by department ───────────────────────────────────────
def get_programs(request):
    dept_id = request.GET.get('department_id')
    programs = Program.objects.filter(department_id=dept_id).values('id', 'name')
    return JsonResponse({'programs': list(programs)})


# ─── Student Registration ────────────────────────────────────────────────────
def student_register(request):
    form = StudentRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        cd = form.cleaned_data
        user = User.objects.create_user(
            username=cd['student_id'],
            email=cd['email'],
            password=cd['password'],
            role=User.ROLE_STUDENT,
        )
        StudentProfile.objects.create(
            user=user,
            student_id=cd['student_id'],
            full_name=cd['full_name'],
            department=cd['department'],
            program=cd['program'],
            year_level=cd['year_level'],
        )
        messages.success(request, "Account created successfully! Please log in.")
        return redirect('student_login')
    return render(request, 'accounts/student_register.html', {'form': form})


# ─── Student Login ───────────────────────────────────────────────────────────
def student_login(request):
    form = StudentLoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        cd = form.cleaned_data
        try:
            profile = StudentProfile.objects.get(student_id=cd['student_id'])
            user = authenticate(request, username=cd['student_id'], password=cd['password'])
            if user and user.role == User.ROLE_STUDENT:
                login(request, user)
                return redirect('student_landing')
            else:
                messages.error(request, "Invalid credentials. Please try again.")
        except StudentProfile.DoesNotExist:
            messages.error(request, "Student ID not found.")
    return render(request, 'accounts/student_login.html', {'form': form})


# ─── Instructor Registration ─────────────────────────────────────────────────
def instructor_register(request):
    form = InstructorRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        cd = form.cleaned_data
        user = User.objects.create_user(
            username=cd['faculty_id'],
            email=cd['email'],
            password=cd['password'],
            role=User.ROLE_INSTRUCTOR,
        )
        InstructorProfile.objects.create(
            user=user,
            faculty_id=cd['faculty_id'],
            full_name=cd['full_name'],
            department=cd['department'],
            program=cd.get('program'),
            year_level_handles=cd['year_level_handles'],
            position=cd['position'],
        )
        messages.success(request, "Instructor account created! Please log in.")
        return redirect('instructor_login')
    return render(request, 'accounts/instructor_register.html', {'form': form})


# ─── Instructor Login ────────────────────────────────────────────────────────
def instructor_login(request):
    form = InstructorLoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        cd = form.cleaned_data
        user = authenticate(request, username=cd['faculty_id'], password=cd['password'])
        if user and user.role == User.ROLE_INSTRUCTOR:
            login(request, user)
            return redirect('instructor_dashboard')
        messages.error(request, "Invalid credentials. Please try again.")
    return render(request, 'accounts/instructor_login.html', {'form': form})


# ─── Admin Login ─────────────────────────────────────────────────────────────
def admin_login(request):
    form = AdminLoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        cd = form.cleaned_data
        try:
            user_obj = User.objects.get(email=cd['email'], role=User.ROLE_ADMIN)
            user = authenticate(request, username=user_obj.username, password=cd['password'])
            if user:
                login(request, user)
                return redirect('admin_dashboard')
            messages.error(request, "Invalid credentials.")
        except User.DoesNotExist:
            messages.error(request, "Admin account not found.")
    return render(request, 'accounts/admin_login.html', {'form': form})


# ─── Logout ──────────────────────────────────────────────────────────────────
def user_logout(request):
    role = getattr(request.user, 'role', None)
    logout(request)
    if role == User.ROLE_INSTRUCTOR:
        return redirect('instructor_login')
    elif role == User.ROLE_ADMIN:
        return redirect('admin_login')
    return redirect('student_login')
