from django.db import models
from accounts.models import StudentProfile, InstructorProfile
from enrollment.models import Subject, Enrollment
from core.soft_delete import SoftDeleteMixin


class Attendance(SoftDeleteMixin, models.Model):
    STATUS_PRESENT = 'present'
    STATUS_ABSENT = 'absent'
    STATUS_LATE = 'late'
    STATUS_EXCUSED = 'excused'
    STATUS_CHOICES = [
        (STATUS_PRESENT, 'Present'),
        (STATUS_ABSENT, 'Absent'),
        (STATUS_LATE, 'Late'),
        (STATUS_EXCUSED, 'Excused'),
    ]

    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='attendance_records')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='attendance_records')
    instructor = models.ForeignKey(InstructorProfile, on_delete=models.SET_NULL, null=True)
    date = models.DateField(db_index=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PRESENT, db_index=True)
    remarks = models.CharField(max_length=200, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('enrollment', 'subject', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.enrollment.student.student_id} - {self.subject.code} - {self.date} - {self.status}"
