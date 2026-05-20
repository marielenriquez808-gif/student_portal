from django import forms
from .models import Grade


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['prelim', 'midterm', 'pre_final', 'final', 'school_year', 'semester']
        widgets = {
            'prelim':    forms.NumberInput(attrs={'step': '0.01', 'min': '1', 'max': '5'}),
            'midterm':   forms.NumberInput(attrs={'step': '0.01', 'min': '1', 'max': '5'}),
            'pre_final': forms.NumberInput(attrs={'step': '0.01', 'min': '1', 'max': '5'}),
            'final':     forms.NumberInput(attrs={'step': '0.01', 'min': '1', 'max': '5'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
