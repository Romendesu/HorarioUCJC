from django.db import models
import uuid

class Usuario(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=150)
    email = models.EmailField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=255)
    activo = models.BooleanField(default=True)

class Rol(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=50, unique=True)

class UsuarioRol(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('usuario', 'rol')

class Profesor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    departamento = models.CharField(max_length=100)

class AsignacionDocente(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE)
    asignatura = models.ForeignKey('schedule.Asignatura', on_delete=models.CASCADE)
    es_titular = models.BooleanField(default=True)
    area_conocimiento = models.CharField(max_length=100)

class Estudiante(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    titulacion = models.ForeignKey('schedule.Titulacion', on_delete=models.CASCADE)

class Matricula(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    asignatura = models.ForeignKey('schedule.Asignatura', on_delete=models.CASCADE)
    curso_academico = models.ForeignKey('schedule.CursoAcademico', on_delete=models.CASCADE)