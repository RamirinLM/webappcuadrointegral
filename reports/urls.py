from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_list, name='report_list'),
    path('gantt/<int:project_id>/', views.gantt_chart, name='gantt_chart'),
]