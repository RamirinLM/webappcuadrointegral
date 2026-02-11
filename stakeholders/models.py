from django.db import models
from projects.models import Project

class Stakeholder(models.Model):
    ROLE_CHOICES = [
        ('manager', 'Gerente de Proyecto'),
        ('team_member', 'Miembro del Equipo'),
        ('client', 'Cliente'),
        ('sponsor', 'Patrocinador'),
        ('other', 'Otro'),
    ]
    INTEREST_CHOICES = [
        ('low', 'Bajo'),
        ('medium', 'Medio'),
        ('high', 'Alto'),
    ]
    POWER_CHOICES = [
        ('low', 'Bajo'),
        ('medium', 'Medio'),
        ('high', 'Alto'),
    ]
    name = models.CharField(max_length=200, verbose_name='Nombre')
    email = models.EmailField(verbose_name='Correo Electrónico')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name='Rol')
    contact_info = models.TextField(blank=True, verbose_name='Información de Contacto')
    interest_level = models.CharField(max_length=10, choices=INTEREST_CHOICES, default='medium', verbose_name='Nivel de Interés')
    power_level = models.CharField(max_length=10, choices=POWER_CHOICES, default='medium', verbose_name='Nivel de Poder')
    projects = models.ManyToManyField(Project, related_name='stakeholders', verbose_name='Proyectos')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Interesado'
        verbose_name_plural = 'Interesados'
