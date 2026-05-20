from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User, StudentProfile, InstructorProfile, Department, Program


class StudentRegistrationForm(forms.Form):
    student_id = forms.CharField(max_length=50, label="Student ID Number")
    full_name = forms.CharField(max_length=200, label="Full Name")
    email = forms.EmailField(label="Email Address")
    department = forms.ModelChoiceField(queryset=Department.objects.all(), label="Department", empty_label="Select Department")
    program = forms.ModelChoiceField(queryset=Program.objects.none(), label="Program/Course", empty_label="Select Program/Course")
    year_level = forms.ChoiceField(choices=[
        ('', '---------'),
        ('1', '1st Year'), ('2', '2nd Year'), ('3', '3rd Year'), ('4', '4th Year')
    ], label="Year Level")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    privacy_policy = forms.BooleanField(required=True, label="I agree to the Privacy Policy")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'department' in self.data:
            try:
                dept_id = int(self.data.get('department'))
                self.fields['program'].queryset = Program.objects.filter(department_id=dept_id)
            except (ValueError, TypeError):
                pass
        for field_name, field in self.fields.items():
            if field_name != 'privacy_policy':
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-check-input'

    def clean_student_id(self):
        sid = self.cleaned_data['student_id']
        if StudentProfile.objects.filter(student_id=sid).exists():
            raise forms.ValidationError("This Student ID is already registered.")
        return sid

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('confirm_password'):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned


class InstructorRegistrationForm(forms.Form):
    full_name = forms.CharField(max_length=200)
    faculty_id = forms.CharField(max_length=50, label="Faculty ID Number")
    email = forms.EmailField()
    department = forms.ModelChoiceField(queryset=Department.objects.all(), empty_label="Select Department")
    program = forms.ModelChoiceField(queryset=Program.objects.none(), required=False, empty_label="Select Program/Course")
    year_level_handles = forms.ChoiceField(choices=[
        ('all', 'All Year Levels'), ('1', '1st Year'),
        ('2', '2nd Year'), ('3', '3rd Year'), ('4', '4th Year'),
    ])
    position = forms.ChoiceField(choices=InstructorProfile.POSITION_CHOICES)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'department' in self.data:
            try:
                dept_id = int(self.data.get('department'))
                self.fields['program'].queryset = Program.objects.filter(department_id=dept_id)
            except (ValueError, TypeError):
                pass
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_faculty_id(self):
        fid = self.cleaned_data['faculty_id']
        if InstructorProfile.objects.filter(faculty_id=fid).exists():
            raise forms.ValidationError("This Faculty ID is already registered.")
        return fid

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('confirm_password'):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned


class StudentLoginForm(forms.Form):
    student_id = forms.CharField(max_length=50, label="Student ID Number")
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class InstructorLoginForm(forms.Form):
    faculty_id = forms.CharField(max_length=50, label="Faculty ID Number")
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class AdminLoginForm(forms.Form):
    email = forms.EmailField(label="Admin Email")
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
