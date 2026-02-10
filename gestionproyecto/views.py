from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q

from .models import (
    Interesado, Proyecto, ActaConstitucion, Comunicacion, Riesgo, Alcance,
    Adquisicion, FeedbackInteresado, AlertaRiesgo, PerfilUsuario,
)
from .forms import (
    ProyectoForm, InteresadoForm, ActaConstitucionForm, ComunicacionForm,
    RiesgoForm, AlcanceForm, AdquisicionForm, FeedbackInteresadoForm, PerfilUsuarioForm,
)
from .mixins import RequireAuthMixin, RequireEditarMixin, RequireEliminarMixin, user_puede_editar, get_perfil
from lineabase.models import Actividad, Cronograma


# ---------- Proyecto ----------
class ProyectoList(RequireAuthMixin, generic.ListView):
    model = Proyecto
    template_name = 'gestionproyectos/proyecto_list.html'
    context_object_name = 'proyecto_list'
    ordering = ['nombre']
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['puede_crear'] = user_puede_editar(self.request.user)
        return context


class ProyectoDetalle(RequireAuthMixin, generic.DetailView):
    model = Proyecto
    template_name = 'gestionproyectos/proyecto_detail.html'
    context_object_name = 'proyecto'


class ProyectoCrear(RequireEditarMixin, generic.CreateView):
    model = Proyecto
    form_class = ProyectoForm
    template_name = 'gestionproyectos/proyecto_form.html'
    success_url = reverse_lazy('gestionproyecto:proyecto_list')
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, 'Proyecto creado correctamente.')
        return super().form_valid(form)


class ProyectoEditar(RequireEditarMixin, generic.UpdateView):
    model = Proyecto
    form_class = ProyectoForm
    template_name = 'gestionproyectos/proyecto_form.html'
    context_object_name = 'proyecto'
    slug_url_kwarg = 'slug'
    login_url = reverse_lazy('login')

    def get_success_url(self):
        messages.success(self.request, 'Proyecto actualizado.')
        return reverse_lazy('gestionproyecto:proyecto_detail', kwargs={'slug': self.object.slug})

    def form_valid(self, form):
        return super().form_valid(form)


class ProyectoEliminar(RequireEliminarMixin, generic.DeleteView):
    model = Proyecto
    template_name = 'gestionproyectos/proyecto_confirm_delete.html'
    context_object_name = 'proyecto'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('gestionproyecto:proyecto_list')
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, 'Proyecto eliminado.')
        return super().form_valid(form)


# ---------- Interesado ----------
class InteresadoList(RequireAuthMixin, generic.ListView):
    model = Interesado
    template_name = 'gestionproyectos/interesado_list.html'
    context_object_name = 'interesado_list'
    ordering = ['nombre']
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['puede_crear'] = user_puede_editar(self.request.user)
        return context


class InteresadoDetalle(RequireAuthMixin, generic.DetailView):
    model = Interesado
    template_name = 'gestionproyectos/interesado_detail.html'
    context_object_name = 'interesado'


class InteresadoCrear(RequireEditarMixin, generic.CreateView):
    model = Interesado
    form_class = InteresadoForm
    template_name = 'gestionproyectos/interesado_form.html'
    success_url = reverse_lazy('gestionproyecto:interesado_list')
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, 'Interesado creado.')
        return super().form_valid(form)


class InteresadoEditar(RequireEditarMixin, generic.UpdateView):
    model = Interesado
    form_class = InteresadoForm
    template_name = 'gestionproyectos/interesado_form.html'
    context_object_name = 'interesado'
    slug_url_kwarg = 'slug'
    login_url = reverse_lazy('login')

    def get_success_url(self):
        messages.success(self.request, 'Interesado actualizado.')
        return reverse_lazy('gestionproyecto:interesado_detail', kwargs={'slug': self.object.slug})


class InteresadoEliminar(RequireEliminarMixin, generic.DeleteView):
    model = Interesado
    template_name = 'gestionproyectos/interesado_confirm_delete.html'
    context_object_name = 'interesado'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('gestionproyecto:interesado_list')
    login_url = reverse_lazy('login')


# ---------- Acta ----------
class ActaList(RequireAuthMixin, generic.ListView):
    model = ActaConstitucion
    template_name = 'gestionproyectos/acta_list.html'
    context_object_name = 'acta_list'
    ordering = ['-id']
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['puede_crear'] = user_puede_editar(self.request.user)
        return context


class ActaDetalle(RequireAuthMixin, generic.DetailView):
    model = ActaConstitucion
    template_name = 'gestionproyectos/acta_detail.html'
    context_object_name = 'acta'


class ActaCrear(RequireEditarMixin, generic.CreateView):
    model = ActaConstitucion
    form_class = ActaConstitucionForm
    template_name = 'gestionproyectos/acta_form.html'
    success_url = reverse_lazy('gestionproyecto:acta_list')
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, 'Acta creada.')
        return super().form_valid(form)


class ActaEditar(RequireEditarMixin, generic.UpdateView):
    model = ActaConstitucion
    form_class = ActaConstitucionForm
    template_name = 'gestionproyectos/acta_form.html'
    context_object_name = 'acta'
    slug_url_kwarg = 'slug'
    login_url = reverse_lazy('login')

    def get_success_url(self):
        messages.success(self.request, 'Acta actualizada.')
        return reverse_lazy('gestionproyecto:acta_detail', kwargs={'slug': self.object.slug})


class ActaEliminar(RequireEliminarMixin, generic.DeleteView):
    model = ActaConstitucion
    template_name = 'gestionproyectos/acta_confirm_delete.html'
    context_object_name = 'acta'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('gestionproyecto:acta_list')
    login_url = reverse_lazy('login')


# ---------- Comunicación ----------
class ComunicacionList(RequireAuthMixin, generic.ListView):
    model = Comunicacion
    template_name = 'gestionproyectos/comunicacion_list.html'
    context_object_name = 'comunicacion_list'
    ordering = ['-fecha']
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['puede_crear'] = user_puede_editar(self.request.user)
        return context


class ComunicacionDetalle(RequireAuthMixin, generic.DetailView):
    model = Comunicacion
    template_name = 'gestionproyectos/comunicacion_detail.html'
    context_object_name = 'comunicacion'


class ComunicacionCrear(RequireEditarMixin, generic.CreateView):
    model = Comunicacion
    form_class = ComunicacionForm
    template_name = 'gestionproyectos/comunicacion_form.html'
    success_url = reverse_lazy('gestionproyecto:comunicacion_list')
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, 'Comunicación registrada.')
        return super().form_valid(form)


class ComunicacionEditar(RequireEditarMixin, generic.UpdateView):
    model = Comunicacion
    form_class = ComunicacionForm
    template_name = 'gestionproyectos/comunicacion_form.html'
    context_object_name = 'comunicacion'
    slug_url_kwarg = 'slug'
    login_url = reverse_lazy('login')

    def get_success_url(self):
        messages.success(self.request, 'Comunicación actualizada.')
        return reverse_lazy('gestionproyecto:comunicacion_detail', kwargs={'slug': self.object.slug})


class ComunicacionEliminar(RequireEliminarMixin, generic.DeleteView):
    model = Comunicacion
    template_name = 'gestionproyectos/comunicacion_confirm_delete.html'
    context_object_name = 'comunicacion'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('gestionproyecto:comunicacion_list')
    login_url = reverse_lazy('login')


# ---------- Riesgo ----------
class RiesgoList(RequireAuthMixin, generic.ListView):
    model = Riesgo
    template_name = 'gestionproyectos/riesgo_list.html'
    context_object_name = 'riesgo_list'
    ordering = ['id']
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['puede_crear'] = user_puede_editar(self.request.user)
        return context


class RiesgoDetalle(RequireAuthMixin, generic.DetailView):
    model = Riesgo
    template_name = 'gestionproyectos/riesgo_detail.html'
    context_object_name = 'riesgo'


class RiesgoCrear(RequireEditarMixin, generic.CreateView):
    model = Riesgo
    form_class = RiesgoForm
    template_name = 'gestionproyectos/riesgo_form.html'
    success_url = reverse_lazy('gestionproyecto:riesgo_list')
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, 'Riesgo registrado.')
        return super().form_valid(form)


class RiesgoEditar(RequireEditarMixin, generic.UpdateView):
    model = Riesgo
    form_class = RiesgoForm
    template_name = 'gestionproyectos/riesgo_form.html'
    context_object_name = 'riesgo'
    slug_url_kwarg = 'slug'
    login_url = reverse_lazy('login')

    def get_success_url(self):
        messages.success(self.request, 'Riesgo actualizado.')
        return reverse_lazy('gestionproyecto:riesgo_detail', kwargs={'slug': self.object.slug})


class RiesgoEliminar(RequireEliminarMixin, generic.DeleteView):
    model = Riesgo
    template_name = 'gestionproyectos/riesgo_confirm_delete.html'
    context_object_name = 'riesgo'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('gestionproyecto:riesgo_list')
    login_url = reverse_lazy('login')


# ---------- Alcance ----------
class AlcanceList(RequireAuthMixin, generic.ListView):
    model = Alcance
    template_name = 'gestionproyectos/alcance_list.html'
    context_object_name = 'alcance_list'
    ordering = ['id']
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['puede_crear'] = user_puede_editar(self.request.user)
        return context


class AlcanceDetalle(RequireAuthMixin, generic.DetailView):
    model = Alcance
    template_name = 'gestionproyectos/alcance_detail.html'
    context_object_name = 'alcance'


class AlcanceCrear(RequireEditarMixin, generic.CreateView):
    model = Alcance
    form_class = AlcanceForm
    template_name = 'gestionproyectos/alcance_form.html'
    success_url = reverse_lazy('gestionproyecto:alcance_list')
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, 'Alcance creado.')
        return super().form_valid(form)


class AlcanceEditar(RequireEditarMixin, generic.UpdateView):
    model = Alcance
    form_class = AlcanceForm
    template_name = 'gestionproyectos/alcance_form.html'
    context_object_name = 'alcance'
    slug_url_kwarg = 'slug'
    login_url = reverse_lazy('login')

    def get_success_url(self):
        messages.success(self.request, 'Alcance actualizado.')
        return reverse_lazy('gestionproyecto:alcance_detail', kwargs={'slug': self.object.slug})


class AlcanceEliminar(RequireEliminarMixin, generic.DeleteView):
    model = Alcance
    template_name = 'gestionproyectos/alcance_confirm_delete.html'
    context_object_name = 'alcance'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('gestionproyecto:alcance_list')
    login_url = reverse_lazy('login')


# ---------- Adquisición ----------
class AdquisicionList(RequireAuthMixin, generic.ListView):
    model = Adquisicion
    template_name = 'gestionproyectos/adquisicion_list.html'
    context_object_name = 'adquisiciones'
    ordering = ['-fecha_limite']
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['puede_crear'] = user_puede_editar(self.request.user)
        return context


class AdquisicionCrear(RequireEditarMixin, generic.CreateView):
    model = Adquisicion
    form_class = AdquisicionForm
    template_name = 'gestionproyectos/adquisicion_form.html'
    success_url = reverse_lazy('gestionproyecto:adquisicion_list')
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, 'Adquisición registrada.')
        return super().form_valid(form)


class AdquisicionEditar(RequireEditarMixin, generic.UpdateView):
    model = Adquisicion
    form_class = AdquisicionForm
    template_name = 'gestionproyectos/adquisicion_form.html'
    context_object_name = 'adquisicion'
    slug_url_kwarg = 'slug'
    login_url = reverse_lazy('login')

    def get_success_url(self):
        messages.success(self.request, 'Adquisición actualizada.')
        return reverse_lazy('gestionproyecto:adquisicion_list')


class AdquisicionEliminar(RequireEliminarMixin, generic.DeleteView):
    model = Adquisicion
    template_name = 'gestionproyectos/adquisicion_confirm_delete.html'
    context_object_name = 'adquisicion'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('gestionproyecto:adquisicion_list')
    login_url = reverse_lazy('login')


# ---------- Feedback ----------
class FeedbackList(RequireAuthMixin, generic.ListView):
    model = FeedbackInteresado
    template_name = 'gestionproyectos/feedback_list.html'
    context_object_name = 'feedbacks'
    ordering = ['-fecha']
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['puede_crear'] = user_puede_editar(self.request.user)
        return context


class FeedbackCrear(RequireEditarMixin, generic.CreateView):
    model = FeedbackInteresado
    form_class = FeedbackInteresadoForm
    template_name = 'gestionproyectos/feedback_form.html'
    success_url = reverse_lazy('gestionproyecto:feedback_list')
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, 'Feedback registrado.')
        return super().form_valid(form)


# ---------- Vistas consolidadas (sin CRUD, solo lectura o agregar) ----------
class MatrizInteresadosView(RequireAuthMixin, generic.TemplateView):
    template_name = 'gestionproyectos/matriz_interesados.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        from .models import NIVEL_PODER, NIVEL_INTERES
        context = super().get_context_data(**kwargs)
        interesados = Interesado.objects.all().order_by('nombre')
        matriz = {}
        for i in interesados:
            key = (i.nivel_poder, i.nivel_interes)
            matriz.setdefault(key, []).append(i)
        matriz_celdas = []
        for poder_val, poder_etiq in NIVEL_PODER:
            fila = []
            for interes_val, interes_etiq in NIVEL_INTERES:
                fila.append(matriz.get((poder_val, interes_val), []))
            matriz_celdas.append((poder_etiq, fila))
        context['interesados'] = interesados
        context['matriz_celdas'] = matriz_celdas
        context['niveles_poder'] = NIVEL_PODER
        context['niveles_interes'] = NIVEL_INTERES
        return context


class InformesView(RequireAuthMixin, generic.TemplateView):
    template_name = 'gestionproyectos/informes.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['proyectos'] = Proyecto.objects.all().order_by('nombre')
        context['cronogramas'] = Cronograma.objects.select_related('proyecto').all()
        context['total_riesgos'] = Riesgo.objects.count()
        context['total_interesados'] = Interesado.objects.count()
        return context


class AlertasRiesgosView(RequireAuthMixin, generic.ListView):
    model = AlertaRiesgo
    template_name = 'gestionproyectos/alertas_riesgos.html'
    context_object_name = 'alertas'
    ordering = ['-fecha_generada']
    login_url = reverse_lazy('login')


class HitosListView(RequireAuthMixin, generic.ListView):
    template_name = 'gestionproyectos/hitos.html'
    context_object_name = 'hitos'
    login_url = reverse_lazy('login')

    def get_queryset(self):
        return Actividad.objects.filter(esHito=True).select_related('cronograma', 'cronograma__proyecto').order_by('fechaFin')


class PlanComunicacionView(RequireAuthMixin, generic.TemplateView):
    template_name = 'gestionproyectos/plan_comunicacion.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comunicaciones'] = Comunicacion.objects.all().order_by('-fecha')[:50]
        context['interesados'] = Interesado.objects.all().order_by('nombre')
        return context


# ---------- Perfiles (solo admin puede listar/editar otros) ----------
class PerfilList(RequireAuthMixin, generic.ListView):
    template_name = 'gestionproyectos/perfil_list.html'
    context_object_name = 'usuarios'
    login_url = reverse_lazy('login')

    def get_queryset(self):
        from django.contrib.auth.models import User
        if get_perfil(self.request.user) and get_perfil(self.request.user).es_admin:
            qs = User.objects.all().order_by('username')
            for u in qs:
                PerfilUsuario.objects.get_or_create(user=u, defaults={'rol': 'consultor'})
            return qs
        return User.objects.filter(pk=self.request.user.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['es_admin'] = get_perfil(self.request.user) and get_perfil(self.request.user).es_admin
        return context


def perfil_editar(request, user_id):
    """Editar rol de un usuario. Solo admin puede cambiar roles."""
    from django.contrib.auth.models import User
    from django.contrib.auth.decorators import login_required
    if not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.get_full_path())
    usuario = get_object_or_404(User, pk=user_id)
    perfil, _ = PerfilUsuario.objects.get_or_create(user=usuario, defaults={'rol': 'consultor'})
    mi_perfil = get_perfil(request.user)
    puede_editar_rol = request.user.is_superuser or (mi_perfil and mi_perfil.es_admin)
    if request.method == 'POST' and puede_editar_rol:
        form = PerfilUsuarioForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado.')
            return redirect('gestionproyecto:perfil_list')
    else:
        form = PerfilUsuarioForm(instance=perfil)
    return render(request, 'gestionproyectos/perfil_form.html', {
        'form': form,
        'usuario': usuario,
        'perfil': perfil,
        'puede_editar_rol': puede_editar_rol,
    })
