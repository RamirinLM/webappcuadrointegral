from django.db import models
from decimal import Decimal
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
        # Defensa contra tipos incorrectos (ej. strings de serialize_form_data)
        # Django no convierte field values automáticamente en __init__ con kwargs
        qty = int(self.quantity) if not isinstance(self.quantity, int) else self.quantity
        cpu = Decimal(str(self.cost_per_unit)) if not isinstance(self.cost_per_unit, Decimal) else self.cost_per_unit
        self.total_cost = qty * cpu
        super().save(*args, **kwargs)
        # Mantener sincronizado el costo de la actividad padre
        if self.activity_id:
            self.activity.update_cost_from_resources()

    def delete(self, *args, **kwargs):
        act = self.activity
        super().delete(*args, **kwargs)
        if act:
            act.update_cost_from_resources()

    def __str__(self):
        activity_name = self.activity.name if self.activity else "Sin actividad"
        return f"{self.name} - {activity_name}"

    class Meta:
        verbose_name = 'Recurso'
        verbose_name_plural = 'Recursos'
