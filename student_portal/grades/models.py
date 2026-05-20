from django.db import models
from accounts.models import StudentProfile, InstructorProfile
from enrollment.models import Subject, Enrollment
from core.soft_delete import SoftDeleteMixin


class Grade(SoftDeleteMixin, models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='grades')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='grades')
    instructor = models.ForeignKey(InstructorProfile, on_delete=models.SET_NULL, null=True)

    # Grade components
    prelim = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    midterm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    pre_final = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    final = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    final_grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    REMARKS_CHOICES = [
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('incomplete', 'Incomplete'),
        ('dropped', 'Dropped'),
    ]
    remarks = models.CharField(max_length=20, choices=REMARKS_CHOICES, blank=True)
    school_year = models.CharField(max_length=20, default='2024-2025', db_index=True)
    semester = models.CharField(max_length=20, default='1st')
    date_encoded = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('enrollment', 'subject')

    def compute_final_grade(self):
        components = [self.prelim, self.midterm, self.pre_final, self.final]
        filled = [c for c in components if c is not None]
        if filled:
            avg = sum(filled) / len(filled)
            self.final_grade = round(avg, 2)
            self.remarks = 'passed' if avg <= 3.0 else 'failed'
        return self.final_grade

    def save(self, *args, **kwargs):
        self.compute_final_grade()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.enrollment.student.student_id} - {self.subject.code} - {self.final_grade}"
