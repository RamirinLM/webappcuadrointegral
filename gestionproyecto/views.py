from django.shortcuts import render

from gestionproyecto.models import Interesado, Proyecto
from django.views import generic

# Create your views here.
class ProyectoView(generic.DetailView):
    model = Proyecto
    template_name = 'proyecto.html'

class InteresadoView(generic.DetailView):
    model = Interesado
    template_name = 'interesado.html'

class HomeView(generic.TemplateView):
    template_name = 'index.html'

class ProyectoList(generic.ListView):
    queryset = Proyecto.objects.all().order_by('nombre')
    template_name = 'index.html'
    context_object_name = 'proyecto_list'