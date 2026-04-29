from django.contrib import admin
from .models import Grado, Asignatura, CursoAcademico, Horario


@admin.register(Grado)
class GradoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'duracion', 'get_total_asignaturas')
    search_fields = ('nombre',)

    def get_total_asignaturas(self, obj):
        return obj.asignaturas.count()
    get_total_asignaturas.short_description = 'Nº Asignaturas'


@admin.register(Asignatura)
class AsignaturaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'creditos', 'semestre', 'get_descripcion_corta')
    list_filter = ('semestre', 'creditos', 'grados')
    search_fields = ('nombre', 'descripcion')
    filter_horizontal = ('grados',)
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'semestre', 'creditos', 'grados')
        }),
        ('Detalles Académicos', {
            'fields': ('descripcion',),
            'classes': ('collapse',)
        }),
    )

    def get_descripcion_corta(self, obj):
        return obj.descripcion[:50] + "..." if len(obj.descripcion) > 50 else obj.descripcion
    get_descripcion_corta.short_description = 'Descripción'


@admin.register(CursoAcademico)
class CursoAcademicoAdmin(admin.ModelAdmin):
    list_display = ('año', 'estado')
    list_filter = ('estado',)
    search_fields = ('año',)


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'grado', 'curso', 'semestre', 'curso_academico', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'semestre', 'curso_academico', 'grado')
    search_fields = ('grado__nombre',)
    readonly_fields = ('fecha_creacion',)
