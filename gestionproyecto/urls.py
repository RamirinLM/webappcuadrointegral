from . import views
from django.urls import path

urlpatterns = [
    path('proyecto/<slug:slug>/', views.ProyectoView.as_view(), name='proyecto_view'),
    path('interesado/<slug:slug>/', views.InteresadoView.as_view(), name='interesado_view'),
    path('', views.ProyectoList.as_view(), name='home'),
]