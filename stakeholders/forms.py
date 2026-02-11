from django import forms
from .models import Stakeholder

class StakeholderForm(forms.ModelForm):
    class Meta:
        model = Stakeholder
        fields = ['name', 'email', 'role', 'contact_info', 'interest_level', 'power_level', 'projects']