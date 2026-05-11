from django import forms
from .models import Resource
from projects.models import Activity
from projects.permissions import is_jefe_departamental, get_user_projects


def _apply_bootstrap_classes(form):
    for field in form.fields.values():
        widget = field.widget
        existing = widget.attrs.get("class", "")

        if isinstance(widget, forms.Select):
            css_class = "form-select"
        elif isinstance(widget, forms.Textarea):
            css_class = "form-control"
            widget.attrs.setdefault("rows", 4)
        else:
            css_class = "form-control"

        widget.attrs["class"] = f"{existing} {css_class}".strip()
        if field.required:
            widget.attrs.setdefault("required", "required")


class ResourceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        _apply_bootstrap_classes(self)
        if user:
            if is_jefe_departamental(user):
                self.fields['activity'].queryset = Activity.objects.all()
            else:
                user_projects = get_user_projects(user)
                self.fields['activity'].queryset = Activity.objects.filter(project__in=user_projects)

    class Meta:
        model = Resource
        fields = ['activity', 'name', 'type', 'quantity', 'cost_per_unit', 'description']
