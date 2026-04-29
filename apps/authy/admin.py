from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Estudiante, Profesor, Decano

# --- FORMULARIO PERSONALIZADO PARA PROFESOR ---

class ProfesorForm(forms.ModelForm):
    # Definimos el campo disponibilidad con un widget de Checkboxes
    disponibilidad = forms.MultipleChoiceField(
        choices=Profesor.AVAIABLE_DAYS, # Asegúrate de que se llame AVAILABLE_DAYS en tu modelo
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Seleccione los días de disponibilidad"
    )

    class Meta:
        model = Profesor
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Esto asegura que si ya hay datos, se marquen los checkboxes correctamente
        if self.instance and self.instance.disponibilidad:
            self.initial['disponibilidad'] = self.instance.disponibilidad

    def save(self, commit=True):
        # Guardamos la lista de Python directamente en el ArrayField
        instance = super().save(commit=False)
        instance.disponibilidad = self.cleaned_data['disponibilidad']
        if commit:
            instance.save()
        return instance

# --- CONFIGURACIÓN DE INLINES ---

class EstudianteInline(admin.StackedInline):
    model = Estudiante
    can_delete = False
    verbose_name_plural = 'Información de Estudiante'
    fk_name = 'user'

class ProfesorInline(admin.StackedInline):
    model = Profesor
    form = ProfesorForm  # <--- APLICAMOS EL FORMULARIO AQUÍ
    can_delete = False
    verbose_name_plural = 'Información de Profesor'
    fk_name = 'user'
    extra = 1

class DecanoInline(admin.StackedInline):
    model = Decano
    can_delete = False
    verbose_name_plural = 'Información de Decano'
    fk_name = 'user'

# --- PERSONALIZACIÓN DEL USER ADMIN ---

class UserAdmin(BaseUserAdmin):
    inlines = [EstudianteInline, ProfesorInline, DecanoInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_rol')

    def get_rol(self, obj):
        if hasattr(obj, 'estudiante'): return "Estudiante" # Verifica los related_name de tus OneToOneField
        if hasattr(obj, 'profesor'): return "Profesor"
        if hasattr(obj, 'decano'): return "Decano"
        return "Sin Perfil"
    
    get_rol.short_description = 'Rol Asignado'

# --- REGISTRO FINAL ---

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ('user', 'carrera', 'anio')

@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    form = ProfesorForm
    list_display = ('user', 'get_asignaturas', 'disponibilidad')
    filter_horizontal = ('asignaturas',)

    def get_asignaturas(self, obj):
        return ", ".join(obj.asignaturas.values_list('nombre', flat=True)) or "—"
    get_asignaturas.short_description = 'Asignaturas'

@admin.register(Decano)
class DecanoAdmin(admin.ModelAdmin):
    list_display = ('user', 'facultad')