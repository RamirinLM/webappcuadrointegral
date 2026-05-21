from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import (
    ActaConstitucion,
    Activity,
    ActivityAssignment,
    ChangeRequest,
    Milestone,
    Project,
    Seguimiento,
    UserProfile,
)


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "start_date", "end_date", "status", "budget"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "end_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "budget": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and start_date > end_date:
            raise ValidationError("La fecha de inicio no puede ser posterior a la fecha de fin.")

        return cleaned_data


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = [
            "project",
            "name",
            "description",
            "start_date",
            "end_date",
            "actual_start_date",
            "actual_end_date",
            "status",
            "assigned_to",
            "cost",
            "actual_cost",
            "time_estimate",
            "predecessor",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "end_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "actual_start_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "actual_end_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "project": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "assigned_to": forms.Select(attrs={"class": "form-select"}),
            "cost": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "actual_cost": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "time_estimate": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "predecessor": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Descripción opcional (el modelo no tiene blank=True, se maneja a nivel form)
        self.fields['description'].required = False

        # Filtrar proyectos a los que el usuario tiene acceso
        if user:
            from .permissions import get_user_projects
            self.fields["project"].queryset = get_user_projects(user)

        # Filtrar predecesoras: solo actividades del mismo proyecto, excluyendo la actual.
        if self.instance and self.instance.pk and self.instance.project:
            self.fields["predecessor"].queryset = Activity.objects.filter(project=self.instance.project).exclude(
                pk=self.instance.pk
            )
        elif "initial" in kwargs and "project" in kwargs["initial"]:
            self.fields["predecessor"].queryset = Activity.objects.filter(project=kwargs["initial"]["project"])
        else:
            self.fields["predecessor"].queryset = Activity.objects.none()

        # Hacer el campo predecessor opcional mas claro.
        self.fields["predecessor"].empty_label = "-- Sin predecesora --"

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        actual_start_date = cleaned_data.get("actual_start_date")
        actual_end_date = cleaned_data.get("actual_end_date")
        project = cleaned_data.get("project")

        if start_date and end_date and start_date > end_date:
            raise ValidationError("La fecha de inicio no puede ser posterior a la fecha de fin.")

        # Validar que las fechas esten dentro del rango del proyecto.
        if project:
            if start_date and project.start_date and start_date < project.start_date:
                raise ValidationError(
                    f"La fecha de inicio no puede ser anterior a la fecha de inicio del proyecto ({project.start_date})."
                )
            if end_date and project.end_date and end_date > project.end_date:
                raise ValidationError(
                    f"La fecha de fin no puede ser posterior a la fecha de fin del proyecto ({project.end_date})."
                )

        # Validar fechas reales vs rango del proyecto
        if project:
            if actual_start_date and project.start_date and actual_start_date < project.start_date:
                raise ValidationError(
                    f"La fecha de inicio real no puede ser anterior al inicio del proyecto ({project.start_date})."
                )
            if actual_end_date and project.end_date and actual_end_date > project.end_date:
                raise ValidationError(
                    f"La fecha de fin real no puede ser posterior al fin del proyecto ({project.end_date})."
                )

        # Validar coherencia de fechas reales
        if actual_start_date and actual_end_date and actual_start_date > actual_end_date:
            raise ValidationError("La fecha de inicio real no puede ser posterior a la fecha de fin real.")

        return cleaned_data


class ActivityAssignmentForm(forms.ModelForm):
    class Meta:
        model = ActivityAssignment
        fields = ["user", "role", "hours_assigned"]
        widgets = {
            "user": forms.Select(attrs={"class": "form-select"}),
            "role": forms.Select(attrs={"class": "form-select"}),
            "hours_assigned": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
        }


class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ["project", "name", "description", "due_date", "completed", "phase", "is_phase_gate"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "project": forms.Select(attrs={"class": "form-select"}),
            "phase": forms.Select(attrs={"class": "form-select"}),
            "is_phase_gate": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "completed": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            from .permissions import get_user_projects
            self.fields["project"].queryset = get_user_projects(user)

    def clean(self):
        cleaned_data = super().clean()
        due_date = cleaned_data.get("due_date")
        project = cleaned_data.get("project")

        # Validar que la fecha este dentro del rango del proyecto.
        if project and due_date:
            if project.start_date and due_date < project.start_date:
                raise ValidationError(
                    f"La fecha limite no puede ser anterior a la fecha de inicio del proyecto ({project.start_date})."
                )
            if project.end_date and due_date > project.end_date:
                raise ValidationError(
                    f"La fecha limite no puede ser posterior a la fecha de fin del proyecto ({project.end_date})."
                )

        return cleaned_data


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}), required=False)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, label="Rol", widget=forms.Select(attrs={"class": "form-select"}))

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_active"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["role"].initial = self.instance.userprofile.role
            self.fields["password"].required = False
        else:
            self.fields["password"].required = True

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data["password"]:
            user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            if hasattr(user, "userprofile"):
                user.userprofile.role = self.cleaned_data["role"]
                user.userprofile.save()
            else:
                UserProfile.objects.create(user=user, role=self.cleaned_data["role"])
        return user


class SeguimientoForm(forms.ModelForm):
    class Meta:
        model = Seguimiento
        fields = ["proyecto", "fecha", "observacion"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "proyecto": forms.Select(attrs={"class": "form-select"}),
            "observacion": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "proyecto" in self.initial:
            self.fields["proyecto"].widget = forms.HiddenInput()


class ActaConstitucionForm(forms.ModelForm):
    class Meta:
        model = ActaConstitucion
        fields = ["alcance", "entregables", "justificacion", "objetivos"]
        widgets = {
            "alcance": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "entregables": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "justificacion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "objetivos": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class ChangeRequestForm(forms.ModelForm):
    """Formulario para solicitudes de cambio."""

    class Meta:
        model = ChangeRequest
        fields = ["project", "description", "justification", "impact"]
        widgets = {
            "project": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 4, "placeholder": "Describe el cambio solicitado..."}
            ),
            "justification": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Justificacion del cambio..."}
            ),
            "impact": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Impacto esperado del cambio..."}
            ),
        }

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user:
            # Filtrar proyectos segun el rol del usuario.
            if hasattr(user, "userprofile") and user.userprofile.role == "jefe_departamental":
                self.fields["project"].queryset = Project.objects.all()
            else:
                self.fields["project"].queryset = Project.objects.filter(created_by=user)
