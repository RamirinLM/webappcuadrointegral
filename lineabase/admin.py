from django.contrib import admin
from .models import Cronograma, Actividad, Recurso, Presupuesto
# Register your models here.
admin.site.register(Cronograma)
admin.site.register(Actividad)
admin.site.register(Recurso)
admin.site.register(Presupuesto)
