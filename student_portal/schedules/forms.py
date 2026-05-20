from django import forms
from .models import Schedule


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = [
            'instructor', 'subject', 'section',
            'day', 'time_start', 'time_end', 'room',
            'school_year', 'semester',
        ]
        widgets = {
            'time_start': forms.TimeInput(attrs={'type': 'time'}),
            'time_end':   forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
