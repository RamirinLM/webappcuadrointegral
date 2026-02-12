from django.db import models
from projects.models import Activity

class Resource(models.Model):
    TYPE_CHOICES = [
        ('human', 'Humano'),
        ('material', 'Material'),
        ('equipment', 'Equipo'),
        ('financial', 'Financiero'),
        ('other', 'Otro'),
    ]
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Actividad')
    name = models.CharField(max_length=200, verbose_name='Nombre')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Tipo')
    quantity = models.PositiveIntegerField(verbose_name='Cantidad')
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Costo por Unidad')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, editable=False, verbose_name='Costo Total')
    description = models.TextField(blank=True, verbose_name='Descripción')

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.cost_per_unit
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.activity.name}"

    class Meta:
        verbose_name = 'Recurso'
        verbose_name_plural = 'Recursos'
