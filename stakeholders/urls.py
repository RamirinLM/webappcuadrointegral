from django.urls import path
from . import views

app_name = 'stakeholders'

urlpatterns = [
    path('', views.stakeholder_list, name='stakeholder_list'),
    path('create/', views.stakeholder_create, name='stakeholder_create'),
    path('<int:pk>/edit/', views.stakeholder_edit, name='stakeholder_edit'),
    path('<int:pk>/delete/', views.stakeholder_delete, name='stakeholder_delete'),
]