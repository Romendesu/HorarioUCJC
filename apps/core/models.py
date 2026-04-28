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


class CursoAcademico(models.Model):
    '''
    ------------------------- DESCRIPCION -------------------------

    El curso académico representa un año académico específico.

    -------------------------- ATRIBUTOS --------------------------

    - ID: Identificador del curso académico
    - AÑO: Año académico (p.ej: 2024-2025)
    - ESTADO: Estado del curso académico (activo/inactivo)

    ---------------------------------------------------------------
    '''

    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]

    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        primary_key=True,
        editable=False
    )

    año = models.CharField(
        max_length=9,
        help_text="Año académico (ej: 2024-2025)"
    )

    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default='inactivo'
    )

    def __str__(self):
        return self.año


class Horario(models.Model):
    '''
    ------------------------- DESCRIPCION -------------------------

    El horario representa la planificación de clases para un curso académico.

    -------------------------- ATRIBUTOS --------------------------

    - ID: Identificador del horario
    - CURSO_ACADEMICO: Curso académico al que pertenece
    - GRADO: Grado al que pertenece el horario
    - CURSO: Curso del grado (1º, 2º, 3º, 4º)
    - ESTADO: Estado del horario (borrador, revision, aprobado, rechazado)
    - FECHA_CREACION: Fecha de creación del horario
    - FECHA_APROBACION: Fecha de aprobación del horario

    ---------------------------------------------------------------
    '''

    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('revision', 'Revisión'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]

    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        primary_key=True,
        editable=False
    )

    curso_academico = models.ForeignKey(
        CursoAcademico,
        on_delete=models.CASCADE,
        related_name='horarios'
    )

    grado = models.ForeignKey(
        Grado,
        on_delete=models.CASCADE,
        related_name='horarios'
    )

    curso = models.IntegerField(
        help_text="Curso del grado (1, 2, 3, 4)"
    )

    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default='borrador'
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    fecha_aprobacion = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.grado.nombre} - Curso {self.curso} - {self.curso_academico.año}"


class SesionHorario(models.Model):
    '''
    ------------------------- DESCRIPCION -------------------------

    Sesión de horario - representa una clase programada en un horario específico.

    -------------------------- ATRIBUTOS --------------------------

    - ID: Identificador de la sesión
    - HORARIO: Horario al que pertenece
    - ASIGNATURA: Asignatura de la sesión
    - PROFESOR: Profesor que imparte la clase
    - DIA: Día de la semana (l, m, x, j, v)
    - HORA_INICIO: Hora de inicio de la sesión
    - HORA_FIN: Hora de fin de la sesión
    - AULA: Aula donde se imparte la clase

    ---------------------------------------------------------------
    '''

    DIA_CHOICES = [
        ('l', 'Lunes'),
        ('m', 'Martes'),
        ('x', 'Miércoles'),
        ('j', 'Jueves'),
        ('v', 'Viernes'),
    ]

    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        primary_key=True,
        editable=False
    )

    horario = models.ForeignKey(
        Horario,
        on_delete=models.CASCADE,
        related_name='sesiones'
    )

    asignatura = models.ForeignKey(
        Asignatura,
        on_delete=models.CASCADE,
        related_name='sesiones'
    )

    profesor = models.ForeignKey(
        'authy.Profesor',
        on_delete=models.CASCADE,
        related_name='sesiones',
        null=True,
        blank=True
    )

    dia = models.CharField(
        max_length=1,
        choices=DIA_CHOICES
    )

    hora_inicio = models.TimeField(
        help_text="Hora de inicio (formato HH:MM)"
    )

    hora_fin = models.TimeField(
        help_text="Hora de fin (formato HH:MM)"
    )

    aula = models.CharField(
        max_length=50,
        help_text="Aula o sala"
    )

    def __str__(self):
        return f"{self.asignatura.nombre} - {self.get_dia_display()} {self.hora_inicio}-{self.hora_fin}"