from django.contrib import admin

from django.contrib import admin
from .models import Grado, Asignatura, CursoAcademico, Horario

# --- INLINE PARA ASIGNATURAS ---
# Esto permite añadir asignaturas directamente desde la ficha del Grado
class AsignaturaInline(admin.TabularInline):
    model = Asignatura
    extra = 1  # Número de filas vacías para añadir rápidamente
    fields = ('nombre', 'creditos', 'tipo')

# --- ADMIN DE GRADO ---
@admin.register(Grado)
class GradoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'duracion', 'get_total_asignaturas')
    search_fields = ('nombre',)
    inlines = [AsignaturaInline]

    def get_total_asignaturas(self, obj):
        return obj.asignatura_set.count()
    
    get_total_asignaturas.short_description = 'Nº Asignaturas'

# --- ADMIN DE ASIGNATURA ---
@admin.register(Asignatura)
class AsignaturaAdmin(admin.ModelAdmin):
    # Columnas visibles en la lista
    list_display = ('nombre', 'creditos', 'tipo', 'get_descripcion_corta')
    
    # Filtros laterales
    list_filter = ('tipo', 'creditos')
    
    # Buscador
    search_fields = ('nombre', 'descripcion')
    
    # Organización del formulario de edición
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'tipo', 'creditos')
        }),
        ('Detalles Académicos', {
            'fields': ('descripcion',),
            'classes': ('collapse',) # Esta sección se puede ocultar/mostrar
        }),
    )

    def get_descripcion_corta(self, obj):
        # Muestra solo los primeros 50 caracteres en la lista
        return obj.descripcion[:50] + "..." if len(obj.descripcion) > 50 else obj.descripcion
    
    get_descripcion_corta.short_description = 'Descripción'


# --- ADMIN DE CURSO ACADÉMICO ---
@admin.register(CursoAcademico)
class CursoAcademicoAdmin(admin.ModelAdmin):
    list_display = ('año', 'estado')
    list_filter = ('estado',)
    search_fields = ('año',)


# --- ADMIN DE HORARIO ---
@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'grado', 'curso', 'curso_academico', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'curso_academico', 'grado')
    search_fields = ('grado__nombre',)
    fieldsets = (
        ('Información del Horario', {
            'fields': ('curso_academico', 'grado', 'curso', 'estado')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_aprobacion'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('fecha_creacion',)