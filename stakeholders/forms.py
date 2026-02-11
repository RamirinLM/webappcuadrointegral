from django import forms
from projects.models import Project
from .models import Stakeholder

class StakeholderForm(forms.ModelForm):
    projects = forms.ModelMultipleChoiceField(queryset=Project.objects.all(), required=False)

    class Meta:
        model = Stakeholder
        fields = ['name', 'email', 'role', 'contact_info', 'interest_level', 'power_level', 'projects']