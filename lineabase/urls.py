from . import views
from django.urls import path


urlpatterns = [
    path('index', views.CronogramaList.as_view(), name='index'),
    path('cronograma/<slug:slug>/', views.CronogramaView.as_view(), name='cronograma_view'),
    path('cronograma/<slug:slug>/gantt/', views.gantt_chart, name='gantt_chart'),   
    path('cronograma/<slug:slug>/bar/', views.bar_chart, name='bar_chart'),
]