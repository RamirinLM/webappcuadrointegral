from django import forms
from projects.permissions import get_user_projects
from .models import Risk


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


class RiskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        _apply_bootstrap_classes(self)
        if user is not None:
            self.fields["project"].queryset = get_user_projects(user)

    class Meta:
        model = Risk
        fields = ['project', 'description', 'probability', 'impact', 'status', 'mitigation_plan', 'identified_by']
