from django import forms
from .models import Enrollment, EducationalBackground, Subject
from accounts.models import Department, Program


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = [
            'civil_status', 'ethnicity', 'nickname', 'address',
            'contact_number', 'date_of_birth', 'place_of_birth',
            'age', 'gender', 'zip_code',
            'mother_name', 'mother_occupation',
            'father_name', 'father_occupation',
            'guardian_name', 'guardian_relationship',
            'school_year', 'semester', 'subjects',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'subjects': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, student=None, **kwargs):
        super().__init__(*args, **kwargs)
        if student:
            base_qs = Subject.objects.filter(
                department=student.department,
                program=student.program,
                year_level=student.year_level,
            )
            # Determine semester from POST data or existing instance
            semester = None
            if self.data:
                semester = self.data.get('semester')
            elif self.instance and self.instance.pk:
                semester = self.instance.semester

            if semester:
                self.fields['subjects'].queryset = base_qs.filter(semester=semester)
            else:
                self.fields['subjects'].queryset = Subject.objects.none()

        for name, field in self.fields.items():
            if name != 'subjects':
                field.widget.attrs['class'] = 'form-control'


class EducationalBackgroundForm(forms.ModelForm):
    class Meta:
        model = EducationalBackground
        exclude = ['enrollment']
        widgets = {
            f: forms.TextInput(attrs={'class': 'form-control'})
            for f in [
                'primary_school', 'primary_address', 'primary_year_graduated',
                'secondary_school', 'secondary_address', 'secondary_year_graduated',
                'tertiary_school', 'tertiary_address', 'tertiary_year_graduated',
            ]
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['code', 'name', 'units', 'department', 'program', 'year_level', 'semester', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].empty_label = "Select Department"
        self.fields['program'].empty_label = "Select Program/Course"

        # Filter program by department if department data available
        if self.data.get('department'):
            try:
                dept_id = int(self.data['department'])
                self.fields['program'].queryset = Program.objects.filter(department_id=dept_id)
            except (ValueError, TypeError):
                self.fields['program'].queryset = Program.objects.none()
        elif self.instance and self.instance.pk and self.instance.department_id:
            self.fields['program'].queryset = Program.objects.filter(
                department_id=self.instance.department_id
            )
        else:
            self.fields['program'].queryset = Program.objects.none()

        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
