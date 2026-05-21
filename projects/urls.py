from django.urls import path
from . import views
from . import wizard_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/wizard/', wizard_views.project_wizard, name='project_wizard'),
    path('projects/wizard/step/<int:step>/', wizard_views.wizard_step, name='wizard_step'),
    path('projects/wizard/cancel/', wizard_views.wizard_cancel, name='wizard_cancel'),
    path('projects/wizard/add-stakeholder/', wizard_views.wizard_add_stakeholder, name='wizard_add_stakeholder'),
    path('projects/wizard/add-risk/', wizard_views.wizard_add_risk, name='wizard_add_risk'),
    path('projects/wizard/add-activity/', wizard_views.wizard_add_activity, name='wizard_add_activity'),
    path('projects/wizard/add-milestone/', wizard_views.wizard_add_milestone, name='wizard_add_milestone'),
    path('projects/<int:pk>/wizard-edit/', wizard_views.project_edit_wizard, name='project_edit_wizard'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),
    path('projects/<int:pk>/financial/', views.project_financial_summary, name='project_financial_summary'),
    path('projects/<int:pk>/approve/', views.project_approve, name='project_approve'),
    # Actividades — scoped por proyecto
    path('projects/<int:project_id>/activities/', views.activity_list, name='activity_list'),
    path('projects/<int:project_id>/activities/create/', views.activity_create, name='activity_create'),
    path('projects/<int:project_id>/activities/<int:pk>/edit/', views.activity_edit, name='activity_edit'),
    path('projects/<int:project_id>/activities/<int:pk>/assign/', views.activity_assign_user, name='activity_assign_user'),
    # Hitos — scoped por proyecto
    path('projects/<int:project_id>/milestones/', views.milestone_list, name='milestone_list'),
    path('projects/<int:project_id>/milestones/create/', views.milestone_create, name='milestone_create'),
    path('projects/<int:project_id>/milestones/<int:pk>/edit/', views.milestone_edit, name='milestone_edit'),
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('seguimiento/', views.seguimiento_list, name='seguimiento_list'),
    path('seguimiento/create/<int:project_id>/', views.seguimiento_create, name='seguimiento_create'),
    path('seguimiento/<int:pk>/edit/', views.seguimiento_edit, name='seguimiento_edit'),
    # Linea Base — seguimiento masivo por actividad
    path('projects/<int:project_id>/linea-base/', views.linea_base_seguimiento, name='linea_base_seguimiento'),
    # Cortes del proyecto — períodos de revisión
    path('projects/<int:project_id>/cortes/', views.project_cuts, name='project_cuts'),
    # Curvas S — gráfico EVM
    path('projects/<int:project_id>/evm-curvas/', views.evm_curves, name='evm_curves'),
    path('acta/<int:project_id>/create/', views.acta_constitucion_create, name='acta_constitucion_create'),
    path('acta/<int:project_id>/edit/', views.acta_constitucion_edit, name='acta_constitucion_edit'),
    # Solicitudes de cambio
    path('change-requests/', views.change_request_list, name='change_request_list'),
    path('change-requests/create/', views.change_request_create, name='change_request_create'),
    path('change-requests/<int:pk>/approve/', views.change_request_approve, name='change_request_approve'),
    path('change-requests/<int:pk>/reject/', views.change_request_reject, name='change_request_reject'),
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:pk>/', views.notification_detail, name='notification_detail'),
    path('notifications/<int:pk>/read/', views.notification_mark_read, name='notification_mark_read'),
]
