import json
from django.shortcuts import render
from django.views import generic
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

from lineabase.models import Cronograma


# Create your views here.
# vistas cronograma
class CronogramaView(LoginRequiredMixin, generic.DetailView):
    model = Cronograma
    template_name = 'lineabase/cronograma.html'
    login_url = reverse_lazy('login')

class CronogramaList(LoginRequiredMixin, generic.ListView):
    queryset = Cronograma.objects.all().order_by('proyecto')
    template_name = 'lineabase/index.html'
    context_object_name = 'cronograma_list'
    login_url = reverse_lazy('login')

class HomeView(generic.TemplateView):
    template_name = 'lineabase/index.html'

@login_required
def gantt_chart(request, slug):
    cronograma = Cronograma.objects.get(slug=slug)
    actividades = cronograma.listaActividades

    # Convertir a lista de diccionarios
    actividades_list = list(actividades.values(
        'id', 'descripcion', 
        'fechaInicio', 'fechaFin', 'porcentajeCompletado','esHito'
    ))

    context = {
        'cronograma': cronograma,
        'actividades': actividades,
        'actividades_json': json.dumps(actividades_list, cls=DjangoJSONEncoder),
    }
    return render(request, 'lineabase/gantt_chart.html', context)

@login_required
def bar_chart(request, slug):
    cronograma = Cronograma.objects.get(slug=slug)
    actividades = cronograma.listaActividades

    # Convertir a lista de diccionarios
    actividades_list = list(actividades.values(
        'id', 'descripcion', 
        'costoPlanificado', 'costoReal'
    ))

    context = {
        'cronograma': cronograma,
        'actividades': actividades,
        'actividades_json': json.dumps(actividades_list, cls=DjangoJSONEncoder),
    }
    return render(request, 'lineabase/bar_chart.html', context)
