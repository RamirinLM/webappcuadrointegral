from django.contrib import admin
from .models import Cronograma, Actividad, Recurso, Presupuesto
# Register your models here.

class ActividadAdmin(admin.ModelAdmin):
    # Usar filter_horizontal para una mejor interfaz
    filter_horizontal = ('recursos',)
    
    # O usar filter_vertical
    # filter_vertical = ('etiquetas',)
    
    # Para autocompletar en muchos registros
    autocomplete_fields = ['recursos']

class RecursoAdmin(admin.ModelAdmin):
    search_fields = ['nombre']

admin.site.register(Cronograma)
admin.site.register(Actividad, ActividadAdmin)
admin.site.register(Recurso, RecursoAdmin)
admin.site.register(Presupuesto)
