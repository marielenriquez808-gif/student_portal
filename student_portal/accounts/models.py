from django.contrib.auth.models import AbstractUser
from django.db import models
from core.soft_delete import SoftDeleteMixin


class Department(models.Model):
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class Program(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='programs')

    def __str__(self):
        return f"{self.name} ({self.department.code})"


class User(AbstractUser):
    ROLE_STUDENT = 'student'
    ROLE_INSTRUCTOR = 'instructor'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = [
        (ROLE_STUDENT, 'Student'),
        (ROLE_INSTRUCTOR, 'Instructor'),
        (ROLE_ADMIN, 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    email = models.EmailField(unique=True)

    def is_student(self):
        return self.role == self.ROLE_STUDENT

    def is_instructor(self):
        return self.role == self.ROLE_INSTRUCTOR

    def is_admin_user(self):
        return self.role == self.ROLE_ADMIN


class StudentProfile(SoftDeleteMixin, models.Model):
    YEAR_LEVEL_CHOICES = [
        ('1', '1st Year'),
        ('2', '2nd Year'),
        ('3', '3rd Year'),
        ('4', '4th Year'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=50, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True)
    year_level = models.CharField(max_length=1, choices=YEAR_LEVEL_CHOICES)
    full_name = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    profile_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_id} - {self.full_name}"


class InstructorProfile(SoftDeleteMixin, models.Model):
    POSITION_CHOICES = [
        ('instructor_1', 'Instructor I'),
        ('instructor_2', 'Instructor II'),
        ('instructor_3', 'Instructor III'),
        ('assistant_prof_1', 'Assistant Professor I'),
        ('assistant_prof_2', 'Assistant Professor II'),
        ('associate_prof', 'Associate Professor'),
        ('full_prof', 'Full Professor'),
    ]
    YEAR_LEVEL_CHOICES = [
        ('1', '1st Year'),
        ('2', '2nd Year'),
        ('3', '3rd Year'),
        ('4', '4th Year'),
        ('all', 'All Year Levels'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='instructor_profile')
    faculty_id = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True, blank=True)
    year_level_handles = models.CharField(max_length=10, choices=YEAR_LEVEL_CHOICES, default='all')
    position = models.CharField(max_length=50, choices=POSITION_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.faculty_id} - {self.full_name}"
