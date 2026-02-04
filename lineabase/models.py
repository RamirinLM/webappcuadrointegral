from datetime import timedelta
from django.db import models
from django.http import JsonResponse
from django.shortcuts import render

ESTADO = [
    (0, 'Iniciado'),
    (1, 'En Progreso'),
    (2, 'Completado'),
    (3, 'Cancelado'), 
]

# Create your models here.
class Cronograma(models.Model):
    costoEstimado = models.DecimalField( decimal_places=2, max_digits=10)
    fechaFinProyecto = models.DateField()
    fechaInicioProyecto = models.DateField()
    observaciones = models.TextField()
    proyecto = models.ForeignKey(to='gestionproyecto.Proyecto', on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, max_length=200, blank=True)
    @property
    def costoRealTotal(self):
        actividades = self.actividad_set.all()
        return sum(actividad.costoReal for actividad in actividades)
    @property
    def diferenciaCostoProyecto(self):
        return self.costoEstimado - self.costoRealTotal
    @property
    def diferenciaDiasTotal(self):
        actividades = self.actividad_set.all()
        return sum(actividad.diferenciaTiempo for actividad in actividades)
    @property
    def porcentajeCompletado(self):
        actividades = self.actividad_set.all()
        if actividades:
            return sum(actividad.porcentajeCompletado for actividad in actividades) // actividades.count()
        return 0
    
    @property
    def fechaInicioRealProyecto(self):
        actividades = self.actividad_set.all()
        if actividades:
            return min(actividad.fechaInicioReal for actividad in actividades)
        return None
    
    @property
    def fechaFinRealProyecto(self):
        actividades = self.actividad_set.all()
        if actividades:
            return max(actividad.fechaFinReal for actividad in actividades)
        return None
    
    @property
    def listaActividades(self):
        return self.actividad_set.all()  

    def __str__(self):
        return self.proyecto.nombre
        
class Recurso(models.Model):
    cantidad = models.IntegerField( default=0)
    costoUnitario = models.DecimalField( decimal_places=2, max_digits=10)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=200, blank=True)

    @property
    def costoTotal(self):
        return self.cantidad * self.costoUnitario

    def __str__(self):
        return self.nombre
    
class Presupuesto(models.Model):
    montoTotal = models.DecimalField( decimal_places=2, max_digits=10)
    slug = models.SlugField(unique=True, max_length=200, blank=True)

    def __str__(self):
        return str(self.montoTotal)

class Actividad(models.Model):
    actividadAnterior = models.ForeignKey(to='self', on_delete=models.CASCADE, null=True, blank=True)
    costoPlanificado = models.DecimalField( decimal_places=2, max_digits=10)
    costoReal = models.DecimalField( decimal_places=2, max_digits=10)
    descripcion = models.TextField()
    #diferenciaCosto = models.DecimalField( decimal_places=2, max_digits=10)
    #diferenciaTiempo = models.IntegerField()
    esHito = models.BooleanField()
    estado = models.IntegerField(choices=ESTADO, default=0)
    fechaInicio = models.DateField()
    fechaFin = models.DateField()
    fechaInicioReal = models.DateField()
    fechaFinReal = models.DateField()
    porcentajeCompletado = models.IntegerField()
    #totalRecursosActividad = models.DecimalField( decimal_places=2, max_digits=10)

    cronograma = models.ForeignKey(to=Cronograma, on_delete=models.CASCADE)
    recursos = models.ManyToManyField(to=Recurso, blank=True)
    presupuesto = models.ForeignKey(to=Presupuesto, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, max_length=200, blank=True)

    @property
    def diferenciaCosto(self):
        return self.costoPlanificado - self.costoReal
    @property
    def diferenciaTiempo(self):
        return (self.fechaFin - self.fechaFinReal).days
    
    #calcular total de recursos
    totalRecursosActividad = property(lambda self: sum(recurso.costoUnitario * recurso.cantidad for recurso in self.recursos.all()))

    def __str__(self):
        return self.descripcion

