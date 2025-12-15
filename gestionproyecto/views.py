from django.shortcuts import render

from gestionproyecto.models import Interesado, Proyecto, ActaConstitucion, Comunicacion, Riesgo, Alcance
from django.views import generic

# Create your views here.

# vistas proyecto
class ProyectoView(generic.DetailView):
    model = Proyecto
    template_name = 'gestionproyectos/proyecto.html'


class ProyectoList(generic.ListView):
    queryset = Proyecto.objects.all().order_by('nombre')
    template_name = 'gestionproyectos/index.html'
    context_object_name = 'proyecto_list'

#vistas interesado
class InteresadoView(generic.DetailView):
    model = Interesado
    template_name = 'gestionproyectos/interesado.html'

class InteresadoList(generic.ListView):
    queryset = Interesado.objects.all().order_by('nombre')
    template_name = 'gestionproyectos/interesadolist.html'
    context_object_name = 'interesado_list'

#vistas acta
class ActasView(generic.DetailView):
    model = ActaConstitucion
    template_name = 'gestionproyectos/acta.html'

class ActasList(generic.ListView):
    queryset = ActaConstitucion.objects.all().order_by('proyecto')
    template_name = 'gestionproyectos/actalist.html'
    context_object_name = 'acta_list'

#vistas comunicaciones
class ComunicacionView(generic.DetailView):
    model = Comunicacion
    template_name = 'gestionproyectos/comunicacion.html'

class ComunicacionesList(generic.ListView):
    queryset = Comunicacion.objects.all().order_by('fecha')
    template_name = 'gestionproyectos/comunicacionlist.html'
    context_object_name = 'comunicacion_list'

#vistas riesgo
class RiesgosView(generic.DetailView):
    model = Riesgo
    template_name = 'gestionproyectos/riesgo.html'

class RiesgosList(generic.ListView):
    queryset = Riesgo.objects.all().order_by('proyecto')
    template_name = 'gestionproyectos/riesgolist.html'
    context_object_name = 'riesgo_list'

#vistas alcance
class AlcanceView(generic.DetailView):
    model = Alcance
    template_name = 'gestionproyectos/alcance.html'

class AlcanceList(generic.ListView):
    queryset = Alcance.objects.all().order_by('proyecto')
    template_name = 'gestionproyectos/alcancelist.html'
    context_object_name = 'alcance_list'

class HomeView(generic.TemplateView):
    queryset = Proyecto.objects.all().order_by('nombre')
    template_name = 'index.html'
    context_object_name = 'proyecto_list'


