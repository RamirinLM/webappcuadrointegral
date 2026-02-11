from django import forms
from .models import Resource

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['project', 'name', 'type', 'quantity', 'cost_per_unit', 'description']