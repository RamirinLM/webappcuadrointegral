from decimal import Decimal
from django.db import models

# Create your models here.
class Seguimiento(models.Model):
    observacion = models.TextField()
    fecha = models.DateField()
    proyecto = models.ForeignKey(to='gestionproyecto.Proyecto', on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, max_length=200, blank=True)

    @property
    def CostPerformanceIndexCPIs(self):
        return CostPerformanceIndexCPI.objects.filter(seguimiento=self)
    @property
    def EarnedValueEVs(self):
        return EarnedValueEV.objects.filter(seguimiento=self)
    @property
    def PlannedValuePVs(self):
        return PlannedValuePV.objects.filter(seguimiento=self)
    @property
    def ShedulePerformanceIndexSPIs(self):
        return ShedulePerformanceIndexSPI.objects.filter(seguimiento=self)
    def __str__(self):
        return f"Seguimiento del proyecto {self.proyecto.nombre} en fecha {self.fecha}"
    
class CostPerformanceIndexCPI(models.Model):
    fecha = models.DateField()
    observaciones = models.TextField()
    seguimiento = models.ForeignKey(to='seguimiento.Seguimiento', on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, max_length=200, blank=True)

    @property
    def estado(self):
        if self.valorCPI >= 1:
            return 'Bueno'
        elif 0.9 <= self.valor < 1:
            return 'Aceptable'
        else:
            return 'Malo'
    
    @property
    def costoReal(self):
        cronograma = self.seguimiento.proyecto.cronograma_set.first()
        if cronograma:
            return cronograma.costoRealTotal
        return 0
    
    @property
    def costoPlanificado(self):
        cronograma = self.seguimiento.proyecto.cronograma_set.first()
        if cronograma:
            return cronograma.costoEstimado
        return 0
    
    @property
    def valorCPI(self):
        if self.costoReal > 0:
            return self.costoPlanificado / self.costoReal
        return 0
    
    def __str__(self):
        return f"CPI: {self.valorCPI} - Estado: {self.estado}"

class EarnedValueEV(models.Model):
    fecha = models.DateField()
    observaciones = models.TextField()
    seguimiento = models.ForeignKey(to='seguimiento.Seguimiento', on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, max_length=200, blank=True)

    @property
    def valor(self):
        cronograma = self.seguimiento.proyecto.cronograma_set.first()
        if cronograma:
            porcentaje_completado = cronograma.porcentajeCompletado / 100
            return cronograma.costoEstimado * Decimal(str(porcentaje_completado))
        return 0

    def __str__(self):
        return f"EVM Valor: {self.valor}"

class PlannedValuePV(models.Model):
    fecha = models.DateField()
    observaciones = models.TextField()
    seguimiento = models.ForeignKey(to='seguimiento.Seguimiento', on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, max_length=200, blank=True)

    @property
    def valor(self):
        cronograma = self.seguimiento.proyecto.cronograma_set.first()
        if cronograma:
            tiempo_total = (cronograma.fechaFinProyecto - cronograma.fechaInicioProyecto).days
            dias_transcurridos = (self.fecha - cronograma.fechaInicioProyecto).days
            if tiempo_total > 0:
                porcentaje_planificado = min(dias_transcurridos / tiempo_total, 1)
                return cronograma.costoEstimado * Decimal(str(porcentaje_planificado))
        return 0

    def __str__(self):
        return f"PVM Valor: {self.valor}"
    
class ShedulePerformanceIndexSPI(models.Model):
    fecha = models.DateField()
    observaciones = models.TextField()
    seguimiento = models.ForeignKey(to='seguimiento.Seguimiento', on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, max_length=200, blank=True)

    @property
    def valor(self):
        evm = EarnedValueEV.objects.filter(seguimiento=self.seguimiento).first()
        pvm = PlannedValuePV.objects.filter(seguimiento=self.seguimiento).first()
        if pvm and pvm.valor > 0:
            return evm.valor / pvm.valor
        return 0

    @property
    def estado(self):
        if self.valor >= 1:
            return 'Adelantado'
        elif 0.9 <= self.valor < 1:
            return 'A tiempo'
        else:
            return 'Retrasado'

    def __str__(self):
        return f"SPI: {self.valor} - Estado: {self.estado}"

    
