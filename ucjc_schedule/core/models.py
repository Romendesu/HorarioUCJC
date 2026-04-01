from django.db import models
import uuid

# Tabla "Auditoria"
class Auditoria(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey('users.Usuario', on_delete=models.SET_NULL, null=True)
    accion = models.CharField(max_length=100)
    entidad = models.CharField(max_length=100)
    valor_anterior = models.JSONField(null=True)
    valor_nuevo = models.JSONField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

# Tabla "Notificacion"
class Notificacion(models.Model):
    TIPO_CHOICES = [('info', 'Info'), ('warning', 'Warning'), ('error', 'Error')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey('users.Usuario', on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    mensaje = models.TextField()
    leido = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

# Tabla "Exportación"
class Exportacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey('users.Usuario', on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10) 
    parametros = models.JSONField()
    fecha = models.DateTimeField(auto_now_add=True)