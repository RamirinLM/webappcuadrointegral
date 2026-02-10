from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from seguimiento.models import Seguimiento

# Create your views here.
# vistas Seguimiento
class SeguimientoView(LoginRequiredMixin, generic.DetailView):
    model = Seguimiento
    template_name = 'seguimiento/seguimiento.html'
    login_url = reverse_lazy('login')

class SeguimientoList(LoginRequiredMixin, generic.ListView):
    queryset = Seguimiento.objects.all().order_by('proyecto')
    template_name = 'seguimiento/index.html'
    context_object_name = 'seguimiento_list'
    login_url = reverse_lazy('login')

class HomeView(generic.TemplateView):
    template_name = 'seguimiento/index.html'