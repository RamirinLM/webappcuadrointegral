"""
Formularios específicos para el Wizard de Creación de Proyectos
"""
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from .models import Project, ActaConstitucion, Alcance, Activity, Milestone
from stakeholders.models import Stakeholder
from risks.models import Risk
from resources.models import Resource


class WizardProjectForm(forms.ModelForm):
    """Formulario para el Paso 1: Datos del Proyecto"""
    
    budget = forms.DecimalField(
        max_digits=10, decimal_places=2, required=False,
        validators=[MinValueValidator(0)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'placeholder': '0.00'
        }),
        label='Presupuesto Estimado'
    )
    
    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'end_date', 'budget']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Nombre del proyecto',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción detallada del proyecto...'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': True
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': True
            }),
            'budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
        }
        labels = {
            'name': 'Nombre del Proyecto',
            'description': 'Descripción',
            'start_date': 'Fecha de Inicio',
            'end_date': 'Fecha de Fin',
            'budget': 'Presupuesto Estimado'
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise ValidationError('La fecha de inicio no puede ser posterior a la fecha de fin.')
        
        return cleaned_data


class WizardActaForm(forms.ModelForm):
    """Formulario para el Paso 2: Acta de Constitución"""
    
    class Meta:
        model = ActaConstitucion
        fields = ['alcance', 'entregables', 'justificacion', 'objetivos']
        widgets = {
            'alcance': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Defina el alcance general del proyecto...',
                'required': True
            }),
            'entregables': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Liste los entregables principales del proyecto...',
                'required': True
            }),
            'justificacion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Justificación del proyecto...',
                'required': True
            }),
            'objetivos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Objetivos del proyecto...',
                'required': True
            }),
        }
        labels = {
            'alcance': 'Alcance del Proyecto',
            'entregables': 'Entregables',
            'justificacion': 'Justificación',
            'objetivos': 'Objetivos'
        }


class WizardAlcanceForm(forms.ModelForm):
    """Formulario para el Paso 4: Alcance Detallado"""
    
    class Meta:
        model = Alcance
        fields = ['descripcion', 'objetivos']
        widgets = {
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Descripción técnica detallada del alcance...',
                'required': True
            }),
            'objetivos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Objetivos específicos y medibles...',
                'required': True
            }),
        }
        labels = {
            'descripcion': 'Descripción del Alcance',
            'objetivos': 'Objetivos Específicos'
        }


class WizardStakeholderForm(forms.ModelForm):
    """Formulario para agregar stakeholders en el Paso 3"""
    
    class Meta:
        model = Stakeholder
        fields = ['name', 'email', 'role', 'contact_info', 'interest_level', 'power_level']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com',
                'required': True
            }),
            'role': forms.Select(attrs={
                'class': 'form-select'
            }),
            'contact_info': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Teléfono, dirección, etc.'
            }),
            'interest_level': forms.Select(attrs={
                'class': 'form-select'
            }),
            'power_level': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'name': 'Nombre',
            'email': 'Correo Electrónico',
            'role': 'Rol',
            'contact_info': 'Información de Contacto',
            'interest_level': 'Nivel de Interés',
            'power_level': 'Nivel de Poder'
        }


class WizardRiskForm(forms.ModelForm):
    """Formulario para agregar riesgos en el Paso 5"""
    
    class Meta:
        model = Risk
        fields = ['description', 'probability', 'impact', 'mitigation_plan', 'identified_by']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del riesgo...',
                'required': True
            }),
            'probability': forms.Select(attrs={
                'class': 'form-select'
            }),
            'impact': forms.Select(attrs={
                'class': 'form-select'
            }),
            'mitigation_plan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Plan de mitigación...'
            }),
            'identified_by': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del identificador'
            }),
        }
        labels = {
            'description': 'Descripción del Riesgo',
            'probability': 'Probabilidad',
            'impact': 'Impacto',
            'mitigation_plan': 'Plan de Mitigación',
            'identified_by': 'Identificado Por'
        }


class WizardCommunicationForm(forms.Form):
    """Formulario para agregar comunicaciones en el Paso 5"""
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            from .permissions import get_user_projects
            self.fields['stakeholder'].queryset = Stakeholder.objects.filter(
                projects__in=get_user_projects(user)
            ).distinct()
    
    stakeholder = forms.ModelChoiceField(
        queryset=Stakeholder.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Interesado',
        required=False
    )
    tipo = forms.ChoiceField(
        choices=[('email', 'Email'), ('reunion', 'Reunión'), ('llamada', 'Llamada')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tipo de Comunicación'
    )
    mensaje = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Descripción de la comunicación...'
        }),
        label='Mensaje/Descripción',
        required=False
    )
    frecuencia = forms.ChoiceField(
        choices=[
            ('diaria', 'Diaria'),
            ('semanal', 'Semanal'),
            ('quincenal', 'Quincenal'),
            ('mensual', 'Mensual'),
            ('segun_necesidad', 'Según Necesidad'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Frecuencia',
        required=False
    )


class WizardActivityForm(forms.ModelForm):
    """Formulario para agregar actividades en el Paso 6"""
    
    def __init__(self, *args, **kwargs):
        project_id = kwargs.pop('project_id', None)
        super().__init__(*args, **kwargs)
        if project_id:
            self.fields['predecessor'].queryset = Activity.objects.filter(project_id=project_id)
        else:
            self.fields['predecessor'].queryset = Activity.objects.none()
    
    class Meta:
        model = Activity
        fields = ['name', 'description', 'start_date', 'end_date', 'cost', 'predecessor']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la actividad',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Descripción de la actividad...'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'predecessor': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'name': 'Nombre de la Actividad',
            'description': 'Descripción',
            'start_date': 'Fecha de Inicio',
            'end_date': 'Fecha de Fin',
            'cost': 'Costo Estimado',
            'predecessor': 'Actividad Predecesora'
        }


class WizardResourceForm(forms.ModelForm):
    """Formulario para agregar recursos a una actividad en el Paso 6"""
    
    quantity = forms.IntegerField(
        initial=1,
        validators=[MinValueValidator(1)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'value': '1'
        }),
        label='Cantidad'
    )
    cost_per_unit = forms.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'placeholder': '0.00'
        }),
        label='Costo por Unidad'
    )
    
    class Meta:
        model = Resource
        fields = ['name', 'type', 'quantity', 'cost_per_unit', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del recurso',
                'required': True
            }),
            'type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Descripción del recurso...'
            }),
        }
        labels = {
            'name': 'Nombre del Recurso',
            'type': 'Tipo',
            'quantity': 'Cantidad',
            'cost_per_unit': 'Costo por Unidad',
            'description': 'Descripción'
        }


class WizardMilestoneForm(forms.ModelForm):
    """Formulario para agregar hitos en el Paso 7"""
    
    def __init__(self, *args, **kwargs):
        project_id = kwargs.pop('project_id', None)
        super().__init__(*args, **kwargs)
        if project_id:
            self.fields['activities'].queryset = Activity.objects.filter(project_id=project_id)
        else:
            self.fields['activities'].queryset = Activity.objects.none()
    
    class Meta:
        model = Milestone
        fields = ['name', 'description', 'due_date', 'phase', 'is_phase_gate', 'activities']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del hito',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Descripción del hito...'
            }),
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': True
            }),
            'phase': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_phase_gate': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'activities': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5'
            }),
        }
        labels = {
            'name': 'Nombre del Hito',
            'description': 'Descripción',
            'due_date': 'Fecha Límite',
            'phase': 'Fase del Proyecto',
            'is_phase_gate': 'Es Cierre de Fase',
            'activities': 'Actividades Asociadas'
        }
