from django.db import models
from django.contrib.auth.models import User

# Modelo de Estudiante
class Estudiante(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_estudiante')
    anio = models.IntegerField()
    carrera = models.CharField(max_length=100)

# Modelo del Profesor
class Profesor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_profesor')
    disponibilidad = models.CharField(max_length=100)
    asignaturas = models.CharField(max_length=100)

# Modelo del decano
class Decano(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_decano')
    facultad = models.CharField(max_length=100)