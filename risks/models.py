from django.db import models
from projects.models import Project

class Risk(models.Model):
    PROBABILITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
    ]
    IMPACT_CHOICES = [
        ('low', 'Bajo'),
        ('medium', 'Medio'),
        ('high', 'Alto'),
    ]
    STATUS_CHOICES = [
        ('identified', 'Identificado'),
        ('mitigated', 'Mitigado'),
        ('occurred', 'Ocurrido'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='Proyecto')
    description = models.TextField(verbose_name='Descripción')
    probability = models.CharField(max_length=10, choices=PROBABILITY_CHOICES, default='medium', verbose_name='Probabilidad')
    impact = models.CharField(max_length=10, choices=IMPACT_CHOICES, default='medium', verbose_name='Impacto')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='identified', verbose_name='Estado')
    mitigation_plan = models.TextField(blank=True, verbose_name='Plan de Mitigación')
    identified_by = models.CharField(max_length=200, verbose_name='Identificado Por')
    identified_date = models.DateField(auto_now_add=True, verbose_name='Fecha de Identificación')

    def __str__(self):
        return f"Riesgo: {self.description[:50]} - {self.project.name}"

    class Meta:
        verbose_name = 'Riesgo'
        verbose_name_plural = 'Riesgos'
