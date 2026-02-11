from django.urls import path
from . import views

app_name = 'risks'

urlpatterns = [
    path('', views.risk_list, name='risk_list'),
    path('create/', views.risk_create, name='risk_create'),
]