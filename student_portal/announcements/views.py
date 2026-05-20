from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import User
from .models import Announcement


class AnnouncementForm:
    pass


from django import forms
class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'audience', 'department', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


@login_required
def announcement_list(request):
    user = request.user
    qs = Announcement.objects.filter(is_active=True)
    if user.role == User.ROLE_STUDENT:
        profile = user.student_profile
        qs = qs.filter(audience__in=['all', 'students']) | qs.filter(audience='department', department=profile.department)
    elif user.role == User.ROLE_INSTRUCTOR:
        qs = qs.filter(audience__in=['all', 'instructors'])
    return render(request, 'announcements/list.html', {'announcements': qs.distinct()})


@login_required
def announcement_create(request):
    if request.user.role not in [User.ROLE_ADMIN, User.ROLE_INSTRUCTOR]:
        return redirect('home')
    form = AnnouncementForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        ann = form.save(commit=False)
        ann.author = request.user
        ann.save()
        messages.success(request, "Announcement created.")
        return redirect('announcement_list')
    return render(request, 'announcements/form.html', {'form': form, 'title': 'Create Announcement'})


@login_required
def announcement_update(request, pk):
    ann = get_object_or_404(Announcement, pk=pk)
    form = AnnouncementForm(request.POST or None, instance=ann)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Announcement updated.")
        return redirect('announcement_list')
    return render(request, 'announcements/form.html', {'form': form, 'title': 'Edit Announcement'})


@login_required
def announcement_delete(request, pk):
    ann = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        ann.delete()
        messages.success(request, "Announcement deleted.")
    return redirect('announcement_list')
