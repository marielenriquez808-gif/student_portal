from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, StudentProfile, InstructorProfile, Department, Program

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    fieldsets = UserAdmin.fieldsets + ((None, {'fields': ('role',)}),)

admin.site.register(StudentProfile)
admin.site.register(InstructorProfile)
admin.site.register(Department)
admin.site.register(Program)
