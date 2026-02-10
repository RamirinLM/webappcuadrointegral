from . import views
from django.urls import path

app_name = 'seguimiento'

urlpatterns = [
    path('index', views.SeguimientoList.as_view(), name='index'),
    path('seguimiento/<slug:slug>/', views.SeguimientoView.as_view(), name='seguimiento_view'),
]