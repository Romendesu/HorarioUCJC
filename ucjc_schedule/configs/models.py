from django.db import models
import uuid

# Tabla "Configuracion Académica"
class ConfiguracionAcademica(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    curso_academico = models.ForeignKey('schedule.CursoAcademico', on_delete=models.CASCADE)
    parametros = models.JSONField() # Almacena JSONB

# Tabla "Franja Horaria"
class FranjaHoraria(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

# Tabla "Regla"
class Regla(models.Model):
    TIPO_CHOICES = [('hard', 'Hard Constraint'), ('soft', 'Soft Constraint')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    descripcion = models.TextField()
    activa = models.BooleanField(default=True)

# Tabla "Resultado Validacion"
class ResultadoValidacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    horario = models.ForeignKey('schedule.Horario', on_delete=models.CASCADE)
    es_valido = models.BooleanField()
    reporte = models.JSONField()