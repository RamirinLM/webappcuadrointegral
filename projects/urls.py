from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),
    path('activities/', views.activity_list, name='activity_list'),
    path('activities/create/', views.activity_create, name='activity_create'),
    path('activities/<int:pk>/edit/', views.activity_edit, name='activity_edit'),
    path('milestones/', views.milestone_list, name='milestone_list'),
    path('milestones/create/', views.milestone_create, name='milestone_create'),
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('seguimiento/', views.seguimiento_list, name='seguimiento_list'),
    path('seguimiento/create/', views.seguimiento_create, name='seguimiento_create'),
    path('seguimiento/<int:pk>/edit/', views.seguimiento_edit, name='seguimiento_edit'),
]