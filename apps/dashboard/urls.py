from django.urls import path
from . import views

urlpatterns = [
    path('inicio/', views.home_redirect, name='dashboard-inicio'), 
    path('horario/', views.home_redirect, name='dashboard-horario'), 
]
