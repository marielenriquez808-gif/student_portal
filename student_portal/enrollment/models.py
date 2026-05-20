from django.db import models
from accounts.models import StudentProfile, InstructorProfile, Department, Program
from core.soft_delete import SoftDeleteMixin


class Subject(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    units = models.PositiveIntegerField(default=3)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='subjects')
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='subjects')
    year_level = models.CharField(max_length=1, choices=[
        ('1', '1st Year'), ('2', '2nd Year'), ('3', '3rd Year'), ('4', '4th Year')
    ])
    semester = models.CharField(max_length=20, choices=[
        ('1st', '1st Semester'), ('2nd', '2nd Semester'), ('summer', 'Summer')
    ], default='1st')
    assigned_instructor = models.ForeignKey(
        InstructorProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='subjects'
    )

    def __str__(self):
        return f"{self.code} - {self.name}"


class Section(models.Model):
    name = models.CharField(max_length=10)  # A, B, C
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    year_level = models.CharField(max_length=1)
    max_slots = models.PositiveIntegerField(default=40)
    current_count = models.PositiveIntegerField(default=0)

    def is_full(self):
        return self.current_count >= self.max_slots

    def __str__(self):
        return f"Section {self.name} - {self.program.code} {self.year_level}"


class Enrollment(SoftDeleteMixin, models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Approval'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]
    CIVIL_STATUS_CHOICES = [
        ('single', 'Single'), ('married', 'Married'),
        ('widowed', 'Widowed'), ('separated', 'Separated'),
    ]
    GENDER_CHOICES = [
        ('male', 'Male'), ('female', 'Female'), ('other', 'Other'),
    ]

    student = models.OneToOneField(StudentProfile, on_delete=models.CASCADE, related_name='enrollment')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True)
    school_year = models.CharField(max_length=20, default='2024-2025', db_index=True)
    semester = models.CharField(max_length=20, choices=[
        ('1st', '1st Semester'), ('2nd', '2nd Semester'), ('summer', 'Summer')
    ], default='1st')
    subjects = models.ManyToManyField(Subject, blank=True)

    # Personal Information
    civil_status = models.CharField(max_length=20, choices=CIVIL_STATUS_CHOICES, blank=True)
    ethnicity = models.CharField(max_length=100, blank=True)
    nickname = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    contact_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    place_of_birth = models.CharField(max_length=200, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)

    # Guardian Information
    mother_name = models.CharField(max_length=200, blank=True)
    mother_occupation = models.CharField(max_length=200, blank=True)
    father_name = models.CharField(max_length=200, blank=True)
    father_occupation = models.CharField(max_length=200, blank=True)
    guardian_name = models.CharField(max_length=200, blank=True)
    guardian_relationship = models.CharField(max_length=100, blank=True)

    submitted_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.student.student_id} - {self.status}"


class EducationalBackground(models.Model):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='educational_background')

    primary_school = models.CharField(max_length=200, blank=True)
    primary_address = models.CharField(max_length=300, blank=True)
    primary_year_graduated = models.CharField(max_length=10, blank=True)

    secondary_school = models.CharField(max_length=200, blank=True)
    secondary_address = models.CharField(max_length=300, blank=True)
    secondary_year_graduated = models.CharField(max_length=10, blank=True)

    tertiary_school = models.CharField(max_length=200, blank=True)
    tertiary_address = models.CharField(max_length=300, blank=True)
    tertiary_year_graduated = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return f"Ed. Background - {self.enrollment.student.student_id}"
