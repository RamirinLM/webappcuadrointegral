from django.views import generic

from gestionproyecto.models import Proyecto

class HomeView(generic.ListView):
    queryset = Proyecto.objects.all().order_by('nombre')
    template_name = 'index.html'
    context_object_name = 'proyecto_list'