from django import forms
from django.utils.text import slugify

from .models import (
    Proyecto, Interesado, ActaConstitucion, Comunicacion, Riesgo, Alcance,
    Adquisicion, FeedbackInteresado, PerfilUsuario,
)
from .models import ESTADO, NIVEL_PODER, NIVEL_INTERES, ROLES


def _generar_slug(instancia, campo_nombre='nombre', max_len=200):
    valor = getattr(instancia, campo_nombre, None) or str(instancia.pk)
    base = slugify(str(valor))[:max_len] or str(instancia.pk)
    slug = base
    modelo = type(instancia)
    n = 0
    while modelo.objects.filter(slug=slug).exclude(pk=instancia.pk).exists():
        n += 1
        slug = f"{base}-{n}"[:max_len]
    return slug


class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ['nombre', 'descripcion', 'fecha_inicio', 'fecha_fin', 'estado', 'acta_constitucion',
                  'interesados', 'comunicaciones', 'riesgos', 'alcances']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-select'}, choices=ESTADO),
            'acta_constitucion': forms.Select(attrs={'class': 'form-select'}),
            'interesados': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'comunicaciones': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'riesgos': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'alcances': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

    def save(self, commit=True):
        obj = super().save(commit=commit)
        if not obj.slug:
            obj.slug = _generar_slug(obj, 'nombre')
            if commit:
                obj.save()
        return obj


class InteresadoForm(forms.ModelForm):
    class Meta:
        model = Interesado
        fields = ['nombre', 'apellido', 'email', 'rol', 'nivel_poder', 'nivel_interes']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'rol': forms.TextInput(attrs={'class': 'form-control'}),
            'nivel_poder': forms.Select(attrs={'class': 'form-select'}, choices=NIVEL_PODER),
            'nivel_interes': forms.Select(attrs={'class': 'form-select'}, choices=NIVEL_INTERES),
        }

    def save(self, commit=True):
        obj = super().save(commit=commit)
        if not obj.slug:
            obj.slug = _generar_slug(obj, 'nombre', 180) + '-' + slugify(obj.apellido or '')[:20]
            if not obj.slug.strip('-'):
                obj.slug = f"interesado-{obj.pk}"
            if commit:
                obj.save()
        return obj


class ActaConstitucionForm(forms.ModelForm):
    class Meta:
        model = ActaConstitucion
        fields = ['alcance', 'objetivos', 'entregables', 'justificacion']
        widgets = {
            'alcance': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'objetivos': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'entregables': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'justificacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def save(self, commit=True):
        obj = super().save(commit=commit)
        if not obj.slug:
            obj.slug = _generar_slug(obj, 'alcance', 180) or f"acta-{obj.pk}"
            if commit:
                obj.save()
        return obj


class ComunicacionForm(forms.ModelForm):
    class Meta:
        model = Comunicacion
        fields = ['observaciones', 'fecha', 'interesado']
        widgets = {
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'interesado': forms.Select(attrs={'class': 'form-select'}),
        }

    def save(self, commit=True):
        obj = super().save(commit=commit)
        if not obj.slug:
            obj.slug = _generar_slug(obj, 'observaciones', 180) or f"com-{obj.pk}"
            if commit:
                obj.save()
        return obj


class RiesgoForm(forms.ModelForm):
    class Meta:
        model = Riesgo
        fields = ['descripcion', 'probabilidad', 'impacto', 'estrategia_mitigacion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'probabilidad': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'impacto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estrategia_mitigacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def save(self, commit=True):
        obj = super().save(commit=commit)
        if not obj.slug:
            obj.slug = _generar_slug(obj, 'descripcion', 180) or f"riesgo-{obj.pk}"
            if commit:
                obj.save()
        return obj


class AlcanceForm(forms.ModelForm):
    class Meta:
        model = Alcance
        fields = ['descripcion', 'metas', 'tiempo']
        widgets = {
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'metas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'tiempo': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        obj = super().save(commit=commit)
        if not obj.slug:
            obj.slug = _generar_slug(obj, 'descripcion', 180) or f"alcance-{obj.pk}"
            if commit:
                obj.save()
        return obj


class AdquisicionForm(forms.ModelForm):
    class Meta:
        model = Adquisicion
        fields = ['proyecto', 'descripcion', 'proveedor', 'monto_estimado', 'estado', 'fecha_limite', 'observaciones']
        widgets = {
            'proyecto': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'proveedor': forms.TextInput(attrs={'class': 'form-control'}),
            'monto_estimado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estado': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_limite': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def save(self, commit=True):
        obj = super().save(commit=commit)
        if not obj.slug:
            obj.slug = _generar_slug(obj, 'descripcion', 180) or f"adq-{obj.pk}"
            if commit:
                obj.save()
        return obj


class FeedbackInteresadoForm(forms.ModelForm):
    class Meta:
        model = FeedbackInteresado
        fields = ['proyecto', 'interesado', 'valoracion', 'comentario']
        widgets = {
            'proyecto': forms.Select(attrs={'class': 'form-select'}),
            'interesado': forms.Select(attrs={'class': 'form-select'}),
            'valoracion': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'comentario': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def save(self, commit=True):
        obj = super().save(commit=commit)
        if not obj.slug and obj.pk:
            obj.slug = f"fb-{obj.pk}"
            if commit:
                obj.save()
        return obj


class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['rol']
        widgets = {
            'rol': forms.Select(attrs={'class': 'form-select'}, choices=ROLES),
        }
