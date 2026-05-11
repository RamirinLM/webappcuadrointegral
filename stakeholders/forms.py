from django import forms
from projects.models import Project
from .models import Feedback, Stakeholder


def _apply_bootstrap_classes(form):
    for name, field in form.fields.items():
        widget = field.widget
        existing = widget.attrs.get("class", "")

        if isinstance(widget, forms.CheckboxInput):
            css_class = "form-check-input"
        elif isinstance(widget, forms.SelectMultiple):
            css_class = "form-select"
            widget.attrs.setdefault("size", 6)
        elif isinstance(widget, forms.Select):
            css_class = "form-select"
        else:
            css_class = "form-control"

        widget.attrs["class"] = f"{existing} {css_class}".strip()
        if isinstance(widget, forms.Textarea):
            widget.attrs.setdefault("rows", 4)

        if field.required:
            widget.attrs.setdefault("required", "required")


class StakeholderForm(forms.ModelForm):
    projects = forms.ModelMultipleChoiceField(queryset=Project.objects.all(), required=True)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        _apply_bootstrap_classes(self)
        if user is not None and getattr(getattr(user, "userprofile", None), "role", "") != "jefe_departamental":
            self.fields["projects"].queryset = Project.objects.filter(created_by=user)

    class Meta:
        model = Stakeholder
        fields = ['name', 'email', 'role', 'contact_info', 'interest_level', 'power_level', 'projects']

    def clean_projects(self):
        projects = self.cleaned_data.get("projects")
        if not projects:
            raise forms.ValidationError("Debe asociar al menos un proyecto al interesado.")
        return projects


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["stakeholder", "project", "rating", "comments"]
        widgets = {
            "comments": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        _apply_bootstrap_classes(self)
        if user is not None:
            projects = Project.objects.all() if getattr(getattr(user, "userprofile", None), "role", "") == "jefe_departamental" else Project.objects.filter(created_by=user)
            self.fields["project"].queryset = projects
            self.fields["stakeholder"].queryset = Stakeholder.objects.filter(projects__in=projects).distinct()
