from django import forms
from .models import Risk

class RiskForm(forms.ModelForm):
    class Meta:
        model = Risk
        fields = ['project', 'description', 'probability', 'impact', 'status', 'mitigation_plan', 'identified_by']