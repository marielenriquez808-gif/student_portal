from django.db import models
from accounts.models import InstructorProfile
from enrollment.models import Subject, Section


class Schedule(models.Model):
    DAY_CHOICES = [
        ('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday'),
    ]

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='schedules')
    instructor = models.ForeignKey(InstructorProfile, on_delete=models.CASCADE, related_name='schedules')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='schedules')
    day = models.CharField(max_length=15, choices=DAY_CHOICES)
    time_start = models.TimeField()
    time_end = models.TimeField()
    room = models.CharField(max_length=50, blank=True)
    school_year = models.CharField(max_length=20, default='2024-2025')
    semester = models.CharField(max_length=20, default='1st')

    class Meta:
        ordering = ['day', 'time_start']

    def __str__(self):
        return f"{self.subject.code} - {self.section} - {self.day} {self.time_start}"
