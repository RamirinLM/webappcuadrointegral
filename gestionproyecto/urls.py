from . import views
from django.urls import path

app_name = 'gestionproyecto'

urlpatterns = [
    # Inicio gestión (lista de proyectos)
    path('', views.ProyectoList.as_view(), name='index'),
    path('proyecto/', views.ProyectoList.as_view(), name='proyecto_list'),
    path('proyecto/nuevo/', views.ProyectoCrear.as_view(), name='proyecto_crear'),
    path('proyecto/<slug:slug>/', views.ProyectoDetalle.as_view(), name='proyecto_detail'),
    path('proyecto/<slug:slug>/editar/', views.ProyectoEditar.as_view(), name='proyecto_editar'),
    path('proyecto/<slug:slug>/eliminar/', views.ProyectoEliminar.as_view(), name='proyecto_eliminar'),

    path('interesado/', views.InteresadoList.as_view(), name='interesado_list'),
    path('interesado/nuevo/', views.InteresadoCrear.as_view(), name='interesado_crear'),
    path('interesado/<slug:slug>/', views.InteresadoDetalle.as_view(), name='interesado_detail'),
    path('interesado/<slug:slug>/editar/', views.InteresadoEditar.as_view(), name='interesado_editar'),
    path('interesado/<slug:slug>/eliminar/', views.InteresadoEliminar.as_view(), name='interesado_eliminar'),

    path('acta/', views.ActaList.as_view(), name='acta_list'),
    path('acta/nuevo/', views.ActaCrear.as_view(), name='acta_crear'),
    path('acta/<slug:slug>/', views.ActaDetalle.as_view(), name='acta_detail'),
    path('acta/<slug:slug>/editar/', views.ActaEditar.as_view(), name='acta_editar'),
    path('acta/<slug:slug>/eliminar/', views.ActaEliminar.as_view(), name='acta_eliminar'),

    path('comunicacion/', views.ComunicacionList.as_view(), name='comunicacion_list'),
    path('comunicacion/nuevo/', views.ComunicacionCrear.as_view(), name='comunicacion_crear'),
    path('comunicacion/<slug:slug>/', views.ComunicacionDetalle.as_view(), name='comunicacion_detail'),
    path('comunicacion/<slug:slug>/editar/', views.ComunicacionEditar.as_view(), name='comunicacion_editar'),
    path('comunicacion/<slug:slug>/eliminar/', views.ComunicacionEliminar.as_view(), name='comunicacion_eliminar'),

    path('riesgo/', views.RiesgoList.as_view(), name='riesgo_list'),
    path('riesgo/nuevo/', views.RiesgoCrear.as_view(), name='riesgo_crear'),
    path('riesgo/<slug:slug>/', views.RiesgoDetalle.as_view(), name='riesgo_detail'),
    path('riesgo/<slug:slug>/editar/', views.RiesgoEditar.as_view(), name='riesgo_editar'),
    path('riesgo/<slug:slug>/eliminar/', views.RiesgoEliminar.as_view(), name='riesgo_eliminar'),

    path('alcance/', views.AlcanceList.as_view(), name='alcance_list'),
    path('alcance/nuevo/', views.AlcanceCrear.as_view(), name='alcance_crear'),
    path('alcance/<slug:slug>/', views.AlcanceDetalle.as_view(), name='alcance_detail'),
    path('alcance/<slug:slug>/editar/', views.AlcanceEditar.as_view(), name='alcance_editar'),
    path('alcance/<slug:slug>/eliminar/', views.AlcanceEliminar.as_view(), name='alcance_eliminar'),

    path('adquisicion/', views.AdquisicionList.as_view(), name='adquisicion_list'),
    path('adquisicion/nuevo/', views.AdquisicionCrear.as_view(), name='adquisicion_crear'),
    path('adquisicion/<slug:slug>/editar/', views.AdquisicionEditar.as_view(), name='adquisicion_editar'),
    path('adquisicion/<slug:slug>/eliminar/', views.AdquisicionEliminar.as_view(), name='adquisicion_eliminar'),

    path('feedback/', views.FeedbackList.as_view(), name='feedback_list'),
    path('feedback/nuevo/', views.FeedbackCrear.as_view(), name='feedback_crear'),

    path('matriz-interesados/', views.MatrizInteresadosView.as_view(), name='matriz_interesados'),
    path('informes/', views.InformesView.as_view(), name='informes'),
    path('alertas-riesgos/', views.AlertasRiesgosView.as_view(), name='alertas_riesgos'),
    path('hitos/', views.HitosListView.as_view(), name='hitos'),
    path('plan-comunicacion/', views.PlanComunicacionView.as_view(), name='plan_comunicacion'),

    path('perfiles/', views.PerfilList.as_view(), name='perfil_list'),
    path('perfil/<int:user_id>/editar/', views.perfil_editar, name='perfil_editar'),
]
