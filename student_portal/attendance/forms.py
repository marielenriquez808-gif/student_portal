from django import forms
from .models import Attendance


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['enrollment', 'subject', 'date', 'status', 'remarks']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, instructor=None, **kwargs):
        super().__init__(*args, **kwargs)
        from enrollment.models import Enrollment, Subject
        if instructor:
            self.fields['subject'].queryset = Subject.objects.filter(assigned_instructor=instructor)
            enrolled_ids = Enrollment.objects.filter(
                subjects__assigned_instructor=instructor, status='approved'
            ).values_list('id', flat=True)
            self.fields['enrollment'].queryset = Enrollment.objects.filter(id__in=enrolled_ids)
        for name, field in self.fields.items():
            if name != 'date':
                field.widget.attrs['class'] = 'form-control'
