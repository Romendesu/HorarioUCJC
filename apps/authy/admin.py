from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Estudiante, Profesor, Decano

# --- CONFIGURACIÓN DE INLINES ---
# Esto permite que los campos extra aparezcan dentro de la edición del Usuario

class EstudianteInline(admin.StackedInline):
    model = Estudiante
    can_delete = False
    verbose_name_plural = 'Información de Estudiante'
    fk_name = 'user'

class ProfesorInline(admin.StackedInline):
    model = Profesor
    can_delete = False
    verbose_name_plural = 'Información de Profesor'
    fk_name = 'user'

class DecanoInline(admin.StackedInline):
    model = Decano
    can_delete = False
    verbose_name_plural = 'Información de Decano'
    fk_name = 'user'

# --- PERSONALIZACIÓN DEL USER ADMIN ---

class UserAdmin(BaseUserAdmin):
    # Añadimos los tres perfiles al formulario de usuario
    inlines = [EstudianteInline, ProfesorInline, DecanoInline]
    
    # Columnas que verás en la lista de usuarios
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_rol')

    def get_rol(self, obj):
        # Función auxiliar para ver el rol rápidamente en la lista
        if hasattr(obj, 'perfil_estudiante'): return "Estudiante"
        if hasattr(obj, 'perfil_profesor'): return "Profesor"
        if hasattr(obj, 'perfil_decano'): return "Decano"
        return "Sin Perfil"
    
    get_rol.short_description = 'Rol Asignado'

# --- REGISTRO FINAL ---

# Primero quitamos el registro por defecto del modelo User
admin.site.unregister(User)
# Lo registramos de nuevo con nuestra configuración personalizada
admin.site.register(User, UserAdmin)

# También los registramos por separado por si quieres editarlos individualmente
@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ('user', 'carrera', 'anio')
    search_fields = ('user__username', 'carrera')

@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    list_display = ('user', 'asignaturas', 'disponibilidad')
    search_fields = ('user__username', 'asignaturas')

@admin.register(Decano)
class DecanoAdmin(admin.ModelAdmin):
    list_display = ('user', 'facultad')
    search_fields = ('user__username', 'facultad')