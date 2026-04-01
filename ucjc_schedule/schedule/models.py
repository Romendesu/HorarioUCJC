from django.db import models
import uuid

# Tabla "Titulacion"
class Titulacion(models.Model):
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    nombre = models.CharField(max_length = 30)
    descripcion = models.CharField(max_length = 255)

# Tabla "Curso Académico"
class CursoAcademico(models.Model):
    STATUS = [
        ('ACTIVO', 'Activo'),
        ('CERRADO', 'Cerrado'),
    ]

    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    anio_inicio = models.IntegerField()
    anio_fin = models.IntegerField()
    estado = models.CharField(
        max_length = 20,
        choices = STATUS
    )

# Tabla "Curso"
class Curso(models.Model):
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    numero = models.IntegerField()
    titulacion = models.ForeignKey(
        Titulacion,
        on_delete = models.CASCADE
    )

# Tabla "Asignatura"
class Asignatura(models.Model):
    id = models.UUIDField(
        primary_key = True,
        default = uuid.uuid4,
        editable= False
    )
    codigo = models.CharField(
        max_length=20,
        unique = True,
        null = False
    )
    nombre = models.CharField(
        max_length=150,
        null = False
    )
    horas_totales = models.IntegerField(
        null = False
    )
    titulacion = models.ForeignKey(
        Titulacion,
        on_delete = models.CASCADE
    )
    es_transversal = models.BooleanField(default=False)

# Tabla "Grupo"
class Grupo(models.Model):
    GROUP_TYPE = (('TEORIA','Teoría'),('PRACTICA','Práctica'),('LABORATORIO','Laboratorio'))
    id = models.UUIDField(
        primary_key = True,
        default = uuid.uuid4,
        editable = False
    )
    nombre = models.CharField(
        max_length=20
    )
    tipo = models.CharField(
        max_length=20,
        choices=GROUP_TYPE
    )
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE
    )

class DisponibilidadProfesor(models.Model):
    TIPO_CHOICES = [('preferente', 'Preferente'), ('bloqueado', 'Bloqueado')]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profesor = models.ForeignKey('users.Profesor', on_delete=models.CASCADE)
    dia_semana = models.PositiveSmallIntegerField() # 1-7
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)

class Aula(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=50)
    capacidad = models.IntegerField()
    tipo = models.CharField(max_length=50)

class Horario(models.Model):
    ESTADO_CHOICES = [('borrador', 'Borrador'), ('revision', 'Revisión'), ('aprobado', 'Aprobado'), ('rechazado', 'Rechazado')]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titulacion = models.ForeignKey(Titulacion, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    curso_academico = models.ForeignKey(CursoAcademico, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)

class Sesion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    horario = models.ForeignKey(Horario, on_delete=models.CASCADE)
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    profesor = models.ForeignKey('users.Profesor', on_delete=models.CASCADE)
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE)
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE)
    dia_semana = models.PositiveSmallIntegerField()
    franja_horaria = models.ForeignKey('configs.FranjaHoraria', on_delete=models.CASCADE)