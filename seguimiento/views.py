from django.shortcuts import render
from django.views import generic
from seguimiento.models import Seguimiento

# Create your views here.
# vistas Segimiento
class SeguimientoView(generic.DetailView):
    model = Seguimiento
    template_name = 'seguimiento/seguimiento.html'

class SeguimientoList(generic.ListView):
    queryset = Seguimiento.objects.all().order_by('proyecto')
    template_name = 'seguimiento/index.html'
    context_object_name = 'seguimiento_list'

class HomeView(generic.TemplateView):
    template_name = 'seguimiento/index.html'