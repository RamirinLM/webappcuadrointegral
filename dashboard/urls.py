# dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_principal, name='principal'),
    path('proyectos/', views.dashboard_proyectos, name='proyectos'),
    path('financiero/', views.dashboard_financiero, name='financiero'),
]