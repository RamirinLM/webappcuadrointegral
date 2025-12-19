from django.contrib import admin
from .models import Proyecto, Interesado, ActaConstitucion, Comunicacion, Riesgo, Alcance

# Register your models here.
class ProyectoAdmin(admin.ModelAdmin):
    # Usar filter_horizontal para una mejor interfaz
    filter_horizontal = ('interesados', 'comunicaciones', 'riesgos', 'alcances')
    autocomplete_fields = ['interesados', 'comunicaciones', 'riesgos', 'alcances']

class InteresadoAdmin(admin.ModelAdmin):
    search_fields = ['nombre', 'apellido']

class ComunicacionAdmin(admin.ModelAdmin):
    search_fields = ['observaciones']

class RiesgoAdmin(admin.ModelAdmin):
    search_fields = ['descripcion']

class AlcanceAdmin(admin.ModelAdmin):
    search_fields = ['descripcion']

admin.site.register(Proyecto, ProyectoAdmin)
admin.site.register(Interesado, InteresadoAdmin)
admin.site.register(ActaConstitucion)
admin.site.register(Comunicacion, ComunicacionAdmin)
admin.site.register(Riesgo, RiesgoAdmin)
admin.site.register(Alcance, AlcanceAdmin)
