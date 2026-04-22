from django.db import models
import uuid
class Grado(models.Model):
    '''
    ------------------------- DESCRIPCION -------------------------

    El grado es la titulación universitaria que estudia el alumno.

    -------------------------- ATRIBUTOS --------------------------

    - ID: Identificador del grado
    - NOMBRE: Nombre del grado (p.ej: Informática, Robótica ...)
    - DURACIÓN: Periodo de duración del grado (Por defecto: 4 años)

    ---------------------------------------------------------------
    '''

    id = models.UUIDField(
        default = uuid.uuid4,
        unique = True,
        primary_key = True,
        editable= False
    )

    nombre = models.CharField(
        max_length=100
    )

    duracion = models.IntegerField(
        default=4,
    )

class Asignatura(models.Model):
    '''
    ------------------------- DESCRIPCION -------------------------

    La asignatura es un campo del grado que estudia el alumno

    -------------------------- ATRIBUTOS --------------------------

    - ID: Identificador de la asignatura
    - NOMBRE: Nombre de la asignatura (p.ej: Álgebra lineal)
    - DESCRIPCION: Descripcion de la asignatura
    - CREDITOS: Nº de creditos de la asignatura
    - TIPO: Si es semestral o anual

    ---------------------------------------------------------------
    '''
    DURATION_GRADE = (
        ('s', 'Semestral'),
        ('a', 'Anual')
    )

    id = models.UUIDField(
        default = uuid.uuid4,
        unique = True,
        primary_key = True,
        editable= False
    )
    
    nombre = models.CharField(
        help_text="Nombre de la asignatura",
        max_length=100
    )

    descripcion = models.TextField(
        help_text="Descripcion de la asignatura",
        max_length=1000
    )

    grado = models.ForeignKey(Grado, on_delete=models.CASCADE, related_name='asignaturas', null=True)

    creditos = models.IntegerField(
        help_text="Creditos de la asignatura",
    )

    tipo = models.CharField(
        choices=DURATION_GRADE,
        max_length=1
    )