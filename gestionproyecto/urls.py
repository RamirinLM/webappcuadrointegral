from . import views
from django.urls import path

urlpatterns = [
    path('index', views.ProyectoList.as_view(), name='index'),
    path('proyecto/<slug:slug>/', views.ProyectoView.as_view(), name='proyecto_view'),

    path('interesado/<slug:slug>/', views.InteresadoView.as_view(), name='interesado_view'),
    path('interesado', views.InteresadoList.as_view(), name='interesado_list'),

    path('acta/<slug:slug>/', views.ActasView.as_view(), name='acta_view'),
    path('acta', views.ActasList.as_view(), name='acta_list'),

    path('comunicacion/<slug:slug>/', views.ComunicacionView.as_view(), name='comunicacion_view'),
    path('comunicacion', views.ComunicacionesList.as_view(), name='comunicacion_list'),

    path('riesgo/<slug:slug>/', views.RiesgosView.as_view(), name='riesgo_view'),
    path('riesgo', views.RiesgosList.as_view(), name='riesgo_list'),

    path('alcance/<slug:slug>/', views.AlcanceView.as_view(), name='alcance_view'),
    path('alcance', views.AlcanceList.as_view(), name='alcance_list'),
]