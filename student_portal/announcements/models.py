from django.db import models
from accounts.models import User, Department
from core.soft_delete import SoftDeleteMixin


class Announcement(SoftDeleteMixin, models.Model):
    AUDIENCE_ALL = 'all'
    AUDIENCE_STUDENTS = 'students'
    AUDIENCE_INSTRUCTORS = 'instructors'
    AUDIENCE_DEPT = 'department'
    AUDIENCE_CHOICES = [
        (AUDIENCE_ALL, 'All Users'),
        (AUDIENCE_STUDENTS, 'Students Only'),
        (AUDIENCE_INSTRUCTORS, 'Instructors Only'),
        (AUDIENCE_DEPT, 'Specific Department'),
    ]

    title = models.CharField(max_length=300)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default=AUDIENCE_ALL)
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True,
        help_text="Only if audience is specific department"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
