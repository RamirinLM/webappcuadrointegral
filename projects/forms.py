from django import forms
from django.contrib.auth.models import User
from .models import Project, Activity, Milestone, UserProfile, Seguimiento, ActaConstitucion

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'end_date', 'status', 'budget']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['project', 'name', 'description', 'start_date', 'end_date', 'status', 'assigned_to', 'cost', 'time_estimate']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ['project', 'name', 'description', 'due_date', 'completed']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, label='Rol')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['role'].initial = self.instance.userprofile.role
            self.fields['password'].required = False
        else:
            self.fields['password'].required = True

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            if hasattr(user, 'userprofile'):
                user.userprofile.role = self.cleaned_data['role']
                user.userprofile.save()
            else:
                UserProfile.objects.create(user=user, role=self.cleaned_data['role'])
        return user

class SeguimientoForm(forms.ModelForm):
    class Meta:
        model = Seguimiento
        fields = ['proyecto', 'fecha', 'observacion']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'proyecto' in self.initial:
            self.fields['proyecto'].widget = forms.HiddenInput()

class ActaConstitucionForm(forms.ModelForm):
    class Meta:
        model = ActaConstitucion
        fields = ['alcance', 'entregables', 'justificacion', 'objetivos']
