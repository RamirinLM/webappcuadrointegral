from django import forms
from .models import Resource
from projects.models import Activity

class ResourceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['activity'].queryset = Activity.objects.filter(project__created_by=user)

    class Meta:
        model = Resource
        fields = ['activity', 'name', 'type', 'quantity', 'cost_per_unit', 'description']