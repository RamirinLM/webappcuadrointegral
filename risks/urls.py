from django.urls import path
from . import views

app_name = 'risks'

urlpatterns = [
    path('', views.risk_list, name='risk_list'),
    path('create/', views.risk_create, name='risk_create'),
    path('<int:pk>/edit/', views.risk_edit, name='risk_edit'),
    path('<int:pk>/delete/', views.risk_delete, name='risk_delete'),
]