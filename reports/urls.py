from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_list, name='report_list'),
    path('gantt/<int:project_id>/', views.gantt_chart, name='gantt_chart'),
    path('progress/<int:project_id>/', views.progress_report, name='progress_report'),
    path('cost/<int:project_id>/', views.cost_report, name='cost_report'),
    path('status/<int:project_id>/', views.status_report, name='status_report'),
    path('calendar/<int:project_id>/', views.calendar_view, name='calendar_view'),
    path('performance/<int:project_id>/', views.performance_graphs, name='performance_graphs'),
    path('export/<int:project_id>/', views.export_csv, name='export_csv'),
]