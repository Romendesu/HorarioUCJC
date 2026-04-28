from django.urls import path
from . import views

urlpatterns = [
    path('inicio/', views.home_redirect, name='dashboard-inicio'), 
    path('horario/', views.schedule_redirect, name='dashboard-horario'), 
    
    # URLs del Decano
    path('decano/', views.decano_home, name='decano-inicio'),
    path('decano/asignaturas/', views.decano_gestionar_asignaturas, name='decano-asignaturas'),
    path('decano/grados/', views.decano_gestionar_grados, name='decano-grados'),
    path('decano/cursos/', views.decano_gestionar_cursos, name='decano-cursos'),
    path('decano/horarios/', views.decano_horarios, name='decano-horarios'),
    path('decano/horarios/generar/', views.decano_generar_horario, name='decano-generar-horario'),
    path('decano/horarios/validar/<uuid:horario_id>/', views.decano_validar_horario, name='decano-validar-horario'),
    path('decano/usuarios/', views.decano_usuarios, name='decano-usuarios'),
    
    # URLs del Estudiante
    path('estudiante/horario/', views.estudiante_horario, name='estudiante-horario'),
]
