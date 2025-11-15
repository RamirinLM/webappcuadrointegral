from django.contrib import admin
from .models import Proyecto, Interesado, ActaConstitucion, Comunicacion, Riesgo, Alcance

# Register your models here.
admin.site.register(Proyecto)
admin.site.register(Interesado)
admin.site.register(ActaConstitucion)
admin.site.register(Comunicacion)
admin.site.register(Riesgo)
admin.site.register(Alcance)
