from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField

# Modelo de Estudiante
class Estudiante(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_estudiante')
    anio = models.IntegerField()
    carrera = models.CharField(max_length=100)

# Modelo del Profesor
class Profesor(models.Model):
    '''
    Modelo que representa al rol de profesor.
    Atributos:
    - Disponibilidad (RF - 08.1 / De lunes a viernes ): El profesor puede marcar su disponibilidad horaria. 
      Por defecto, la disponibilidad del profesor será todos los días
    - 
    '''
    AVAIABLE_DAYS = [
        ('l', 'Lunes'),
        ('m', 'Martes'),
        ('x', 'Miercoles'),
        ('j', 'Jueves'),
        ('v', 'Viernes'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_profesor')
    disponibilidad = ArrayField(
        models.CharField(max_length=1, choices=AVAIABLE_DAYS),
        blank=True,
        default=list,
        help_text="Seleccione los dias de disponibilidad del profesor"
    )

    asignaturas = models.ManyToManyField(
        'core.Asignatura',
        blank=True,
        related_name='profesores',
        help_text="Asignaturas que puede impartir este profesor",
    )

# Modelo del decano
class Decano(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_decano')
    facultad = models.CharField(max_length=100)