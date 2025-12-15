import json
from django.shortcuts import render
from django.views import generic
from django.core.serializers.json import DjangoJSONEncoder

from lineabase.models import Cronograma


# Create your views here.
# vistas cronograma
class CronogramaView(generic.DetailView):
    model = Cronograma
    template_name = 'lineabase/cronograma.html'

class CronogramaList(generic.ListView):
    queryset = Cronograma.objects.all().order_by('proyecto')
    template_name = 'lineabase/index.html'
    context_object_name = 'cronograma_list'

class HomeView(generic.TemplateView):
    template_name = 'lineabase/index.html'

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
