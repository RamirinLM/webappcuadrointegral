from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Project, Activity, Milestone, UserProfile, Seguimiento, ActaConstitucion, ActivityAssignment

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'end_date', 'status', 'budget']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise ValidationError('La fecha de inicio no puede ser posterior a la fecha de fin.')
        
        return cleaned_data


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['project', 'name', 'description', 'start_date', 'end_date', 'status', 'assigned_to', 'cost', 'time_estimate', 'predecessor']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'time_estimate': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'predecessor': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar predecesoras: solo actividades del mismo proyecto, excluyendo la actual
        if self.instance and self.instance.pk and self.instance.project:
            self.fields['predecessor'].queryset = Activity.objects.filter(
                project=self.instance.project
            ).exclude(pk=self.instance.pk)
        elif 'initial' in kwargs and 'project' in kwargs['initial']:
            self.fields['predecessor'].queryset = Activity.objects.filter(
                project=kwargs['initial']['project']
            )
        else:
            self.fields['predecessor'].queryset = Activity.objects.none()
        
        # Hacer el campo predecessor opcional más claro
        self.fields['predecessor'].empty_label = "-- Sin predecesora --"


class ActivityAssignmentForm(forms.ModelForm):
    class Meta:
        model = ActivityAssignment
        fields = ['user', 'role', 'hours_assigned']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'hours_assigned': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }


class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ['project', 'name', 'description', 'due_date', 'completed', 'phase', 'is_phase_gate']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'phase': forms.Select(attrs={'class': 'form-select'}),
            'is_phase_gate': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, label='Rol', widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

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
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'proyecto': forms.Select(attrs={'class': 'form-select'}),
            'observacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'proyecto' in self.initial:
            self.fields['proyecto'].widget = forms.HiddenInput()


class ActaConstitucionForm(forms.ModelForm):
    class Meta:
        model = ActaConstitucion
        fields = ['alcance', 'entregables', 'justificacion', 'objetivos']
        widgets = {
            'alcance': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'entregables': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'justificacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'objetivos': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
