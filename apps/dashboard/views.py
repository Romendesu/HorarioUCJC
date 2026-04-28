from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import datetime, timedelta, time as dt_time
import locale
from apps.core.models import Grado, Asignatura, CursoAcademico, Horario, SesionHorario
from apps.core.services import generar_horario, validar_horario
from apps.authy.models import Estudiante, Profesor

# Franjas del motor (must match services.py FRANJAS_HORARIAS)
_FRANJAS = [
    (dt_time(8, 30),  dt_time(10, 0)),
    (dt_time(10, 0),  dt_time(11, 30)),
    (dt_time(11, 30), dt_time(13, 0)),
    (dt_time(13, 0),  dt_time(14, 30)),
    (dt_time(14, 30), dt_time(16, 0)),
    (dt_time(16, 0),  dt_time(17, 30)),
    (dt_time(17, 30), dt_time(19, 0)),
    (dt_time(19, 0),  dt_time(20, 30)),
]
_DIAS_ORDER = ['l', 'm', 'x', 'j', 'v']
_DIA_MAP = {0: 'l', 1: 'm', 2: 'x', 3: 'j', 4: 'v'}
_FRANJAS_STR = [
    ('08:30', '10:00'), ('10:00', '11:30'), ('11:30', '13:00'), ('13:00', '14:30'),
    ('14:30', '16:00'), ('16:00', '17:30'), ('17:30', '19:00'), ('19:00', '20:30'),
]


def _build_grid(sesiones):
    """Construye la cuadrícula del horario como lista de filas [{hora_inicio, hora_fin, celdas: [sesion|None]}]."""
    grid = []
    for hi_str, hf_str in _FRANJAS_STR:
        h, m = int(hi_str[:2]), int(hi_str[3:])
        hi = dt_time(h, m)
        fila = {'hora_inicio': hi_str, 'hora_fin': hf_str, 'celdas': []}
        has_any = False
        for dia in _DIAS_ORDER:
            s = next((s for s in sesiones if s.dia == dia and s.hora_inicio == hi), None)
            if s:
                has_any = True
            fila['celdas'].append(s)
        if has_any:
            grid.append(fila)
    return grid


# Funcion auxiliar para obtener el rol del usuario segun su perfil
def obtain_rol(user):
    if hasattr(user, 'perfil_estudiante'):
        return 'Estudiante', user.perfil_estudiante
    elif hasattr(user, 'perfil_profesor'):
        return 'Profesor', user.perfil_profesor
    elif hasattr(user, 'perfil_decano'):
        return 'Decano', user.perfil_decano
    return None, None


def _obtener_sesiones(rol, profile):
    """Returns (horario_or_None, sesiones_queryset) for the active academic year."""
    curso_activo = CursoAcademico.objects.filter(estado='activo').first()
    if not curso_activo or not profile:
        return None, SesionHorario.objects.none()

    if rol == 'Estudiante':
        try:
            grado = Grado.objects.get(nombre=profile.carrera)
        except Grado.DoesNotExist:
            return None, SesionHorario.objects.none()
        horario = Horario.objects.filter(
            curso_academico=curso_activo, grado=grado, estado='aprobado'
        ).first()
        if not horario:
            return None, SesionHorario.objects.none()
        return horario, SesionHorario.objects.filter(
            horario=horario
        ).select_related('asignatura', 'profesor__user')

    if rol == 'Profesor':
        sesiones = SesionHorario.objects.filter(
            profesor=profile,
            horario__curso_academico=curso_activo,
            horario__estado='aprobado',
        ).select_related('asignatura', 'horario__grado', 'horario')
        return None, sesiones

    return None, SesionHorario.objects.none()

# Redireccionamiento al Dashboard
@login_required
def home_redirect(request):
    rol, profile = obtain_rol(request.user)

    if rol == 'Decano':
        return redirect('decano-inicio')

    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    except:
        locale.setlocale(locale.LC_TIME, 'es-ES')

    now = datetime.now()
    actual_monday = now - timedelta(days=now.weekday())
    week_days = [(actual_monday + timedelta(days=i)).day for i in range(7)]

    day = now.day
    month_name = now.strftime("%B")
    year = now.year
    date_str = f"{now.strftime('%A').capitalize()}, {day} {month_name} {year}"

    # ── Datos del horario ────────────────────────────────────────────────
    dia_hoy = _DIA_MAP.get(now.weekday())
    horario_activo, sesiones = _obtener_sesiones(rol, profile)

    sesiones_hoy = sesiones.filter(dia=dia_hoy).order_by('hora_inicio') if dia_hoy else SesionHorario.objects.none()
    sesiones_semana = list(sesiones.order_by('dia', 'hora_inicio'))

    total_asignaturas = sesiones.values('asignatura_id').distinct().count()
    horas_semana = round(sesiones.count() * 1.5)
    clases_hoy_count = sesiones_hoy.count()
    horas_semana_pct = min(100, round((horas_semana / 25) * 100))
    clases_hoy_pct = min(100, round((clases_hoy_count / 8) * 100))

    proxima_sesion = None
    if dia_hoy:
        proxima_sesion = sesiones_hoy.filter(hora_inicio__gte=now.time()).order_by('hora_inicio').first()
    if not proxima_sesion:
        idx = (_DIAS_ORDER.index(dia_hoy) + 1) if dia_hoy in _DIAS_ORDER else 0
        for d in _DIAS_ORDER[idx:]:
            proxima_sesion = sesiones.filter(dia=d).order_by('hora_inicio').first()
            if proxima_sesion:
                break

    context = {
        'Rol': rol,
        'Perfil': profile,
        'Title': f'Dashboard - {rol}',
        'Date': date_str,
        'day': day,
        'month_name': month_name,
        'year': year,
        'semana_dias': week_days,
        'horario_activo': horario_activo,
        'sesiones_hoy': sesiones_hoy,
        'sesiones_semana': sesiones_semana,
        'total_asignaturas': total_asignaturas,
        'horas_semana': horas_semana,
        'clases_hoy_count': clases_hoy_count,
        'horas_semana_pct': horas_semana_pct,
        'clases_hoy_pct': clases_hoy_pct,
        'proxima_sesion': proxima_sesion,
        'tiene_horario': horario_activo is not None or sesiones.exists(),
    }

    return render(request, 'dashboard/home.html', context)


# Redireccionamiento al Horario
@login_required
def schedule_redirect(request):
    rol, profile = obtain_rol(request.user)
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    except:
        locale.setlocale(locale.LC_TIME, 'es-ES')

    now = datetime.now()
    actual_monday = now - timedelta(days=now.weekday())
    week_days = [actual_monday + timedelta(days=i) for i in range(5)]

    day = now.day
    month_name = now.strftime("%B")
    year = now.year
    date_str = f"{now.strftime('%A').capitalize()}, {day} {month_name} {year}"

    # ── Datos del horario ────────────────────────────────────────────────
    dia_hoy = _DIA_MAP.get(now.weekday())
    _, sesiones = _obtener_sesiones(rol, profile)
    sesiones_list = list(sesiones.select_related('asignatura', 'profesor__user'))

    sesiones_hoy = sorted([s for s in sesiones_list if s.dia == dia_hoy], key=lambda s: s.hora_inicio) if dia_hoy else []

    proxima_sesion = None
    if dia_hoy:
        hora_actual = now.time()
        proxima_sesion = next((s for s in sesiones_hoy if s.hora_inicio >= hora_actual), None)

    total_horas_hoy = round(len(sesiones_hoy) * 1.5)

    # Construir grid semanal (solo franjas con al menos una sesión)
    grid = []
    for hi, hf in _FRANJAS:
        fila = {
            'hora_inicio': hi.strftime('%H:%M'),
            'hora_fin': hf.strftime('%H:%M'),
            'celdas': [],
        }
        has_any = False
        for dia in _DIAS_ORDER:
            sesion = next((s for s in sesiones_list if s.dia == dia and s.hora_inicio == hi), None)
            if sesion:
                has_any = True
            fila['celdas'].append(sesion)
        if has_any:
            grid.append(fila)

    context = {
        'Rol': rol,
        'Perfil': profile,
        'Title': f'Dashboard - {rol}',
        'Date': date_str,
        'day': day,
        'month_name': month_name,
        'year': year,
        'semana_dias': week_days,
        'sesiones_hoy': sesiones_hoy,
        'proxima_sesion': proxima_sesion,
        'grid': grid,
        'total_horas_hoy': total_horas_hoy,
        'tiene_sesiones': bool(sesiones_list),
    }

    return render(request, 'dashboard/schedule.html', context)


# ==================== VISTAS DEL DECANO ====================

@login_required
def decano_home(request):
    """Vista principal del decano con métricas y accesos rápidos"""
    rol, profile = obtain_rol(request.user)
    
    # Verificar que el usuario es decano
    if rol != 'Decano':
        return redirect('dashboard-inicio')
    
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    except:
        locale.setlocale(locale.LC_TIME, 'es-ES')

    now = datetime.now()
    day = now.day
    month_name = now.strftime("%B")
    year = now.year
    date_str = f"{now.strftime('%A').capitalize()}, {day} {month_name} {year}"

    # Métricas para el decano
    total_grados = Grado.objects.count()
    total_asignaturas = Asignatura.objects.count()
    cursos_activos = CursoAcademico.objects.filter(estado='activo').count()
    
    # Horarios generados y pendientes
    horarios_aprobados = Horario.objects.filter(estado='aprobado').count()
    horarios_pendientes = Horario.objects.filter(estado__in=['borrador', 'revision']).count()

    context = {
        'Rol': rol,
        'Perfil': profile,
        'Title': f'Dashboard - {rol}',
        'Date': date_str,
        'day': day,
        'month_name': month_name,
        'year': year,
        'total_grados': total_grados,
        'total_asignaturas': total_asignaturas,
        'cursos_activos': cursos_activos,
        'horarios_aprobados': horarios_aprobados,
        'horarios_pendientes': horarios_pendientes,
    }
    
    return render(request, 'dashboard/decano/home.html', context)


@login_required
def decano_gestionar_asignaturas(request):
    """Vista para gestionar asignaturas (crear, editar, eliminar)"""
    rol, profile = obtain_rol(request.user)
    
    if rol != 'Decano':
        return redirect('dashboard-inicio')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'crear':
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion')
            creditos = request.POST.get('creditos')
            tipo = request.POST.get('tipo')
            grado_id = request.POST.get('grado')
            
            if nombre and creditos and tipo and grado_id:
                grado = Grado.objects.get(id=grado_id)
                Asignatura.objects.create(
                    nombre=nombre,
                    descripcion=descripcion,
                    creditos=int(creditos),
                    tipo=tipo,
                    grado=grado
                )
                messages.success(request, 'Asignatura creada correctamente')
        
        elif action == 'editar':
            asignatura_id = request.POST.get('asignatura_id')
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion')
            creditos = request.POST.get('creditos')
            tipo = request.POST.get('tipo')
            grado_id = request.POST.get('grado')
            
            asignatura = Asignatura.objects.get(id=asignatura_id)
            asignatura.nombre = nombre
            asignatura.descripcion = descripcion
            asignatura.creditos = int(creditos)
            asignatura.tipo = tipo
            asignatura.grado = Grado.objects.get(id=grado_id)
            asignatura.save()
            messages.success(request, 'Asignatura actualizada correctamente')
        
        elif action == 'eliminar':
            asignatura_id = request.POST.get('asignatura_id')
            Asignatura.objects.get(id=asignatura_id).delete()
            messages.success(request, 'Asignatura eliminada correctamente')
        
        return redirect('decano-asignaturas')
    
    grados = Grado.objects.all()
    asignaturas = Asignatura.objects.select_related('grado').all()
    
    context = {
        'Rol': rol,
        'Perfil': profile,
        'Title': 'Gestionar Asignaturas',
        'grados': grados,
        'asignaturas': asignaturas,
    }
    
    return render(request, 'dashboard/decano/asignaturas.html', context)


@login_required
def decano_gestionar_grados(request):
    """Vista para gestionar grados (crear, editar, eliminar)"""
    rol, profile = obtain_rol(request.user)
    
    if rol != 'Decano':
        return redirect('dashboard-inicio')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'crear':
            nombre = request.POST.get('nombre')
            duracion = request.POST.get('duracion')
            
            if nombre:
                Grado.objects.create(
                    nombre=nombre,
                    duracion=int(duracion) if duracion else 4
                )
                messages.success(request, 'Grado creado correctamente')
        
        elif action == 'editar':
            grado_id = request.POST.get('grado_id')
            nombre = request.POST.get('nombre')
            duracion = request.POST.get('duracion')
            
            grado = Grado.objects.get(id=grado_id)
            grado.nombre = nombre
            grado.duracion = int(duracion) if duracion else 4
            grado.save()
            messages.success(request, 'Grado actualizado correctamente')
        
        elif action == 'eliminar':
            grado_id = request.POST.get('grado_id')
            Grado.objects.get(id=grado_id).delete()
            messages.success(request, 'Grado eliminado correctamente')
        
        return redirect('decano-grados')
    
    grados = Grado.objects.all()
    
    context = {
        'Rol': rol,
        'Perfil': profile,
        'Title': 'Gestionar Grados',
        'grados': grados,
    }
    
    return render(request, 'dashboard/decano/grados.html', context)


@login_required
def decano_gestionar_cursos(request):
    """Vista para gestionar cursos académicos (crear, editar, eliminar)"""
    rol, profile = obtain_rol(request.user)
    
    if rol != 'Decano':
        return redirect('dashboard-inicio')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'crear':
            año = request.POST.get('año')
            
            if año:
                # Desactivar otros cursos si se marca como activo
                if request.POST.get('es_activo'):
                    CursoAcademico.objects.update(estado='inactivo')
                    CursoAcademico.objects.create(año=año, estado='activo')
                else:
                    CursoAcademico.objects.create(año=año, estado='inactivo')
                messages.success(request, 'Curso académico creado correctamente')
        
        elif action == 'editar':
            curso_id = request.POST.get('curso_id')
            año = request.POST.get('año')
            
            curso = CursoAcademico.objects.get(id=curso_id)
            curso.año = año
            
            if request.POST.get('es_activo'):
                CursoAcademico.objects.update(estado='inactivo')
                curso.estado = 'activo'
            
            curso.save()
            messages.success(request, 'Curso académico actualizado correctamente')
        
        elif action == 'eliminar':
            curso_id = request.POST.get('curso_id')
            CursoAcademico.objects.get(id=curso_id).delete()
            messages.success(request, 'Curso académico eliminado correctamente')
        
        return redirect('decano-cursos')
    
    cursos = CursoAcademico.objects.all().order_by('-año')
    
    context = {
        'Rol': rol,
        'Perfil': profile,
        'Title': 'Gestionar Cursos Académicos',
        'cursos': cursos,
    }
    
    return render(request, 'dashboard/decano/cursos.html', context)


@login_required
def decano_horarios(request):
    """Vista para ver horarios generados y pendientes de aprobar"""
    rol, profile = obtain_rol(request.user)
    
    if rol != 'Decano':
        return redirect('dashboard-inicio')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'aprobar':
            horario_id = request.POST.get('horario_id')
            horario = Horario.objects.get(id=horario_id)
            horario.estado = 'aprobado'
            horario.fecha_aprobacion = datetime.now()
            horario.save()
            messages.success(request, 'Horario aprobado correctamente')
        
        elif action == 'rechazar':
            horario_id = request.POST.get('horario_id')
            horario = Horario.objects.get(id=horario_id)
            horario.estado = 'rechazado'
            horario.save()
            messages.success(request, 'Horario rechazado')
        
        return redirect('decano-horarios')
    
    horarios_generados = Horario.objects.filter(
        estado='aprobado'
    ).select_related('curso_academico', 'grado').prefetch_related(
        'sesiones__asignatura', 'sesiones__profesor__user'
    ).order_by('-fecha_creacion')

    horarios_pendientes = Horario.objects.filter(
        estado__in=['borrador', 'revision']
    ).select_related('curso_academico', 'grado').prefetch_related(
        'sesiones__asignatura', 'sesiones__profesor__user'
    ).order_by('-fecha_creacion')

    for h in horarios_generados:
        h.grid = _build_grid(list(h.sesiones.all()))
    for h in horarios_pendientes:
        h.grid = _build_grid(list(h.sesiones.all()))

    todos_horarios = list(horarios_pendientes) + list(horarios_generados)

    grados = Grado.objects.all().order_by('nombre')
    cursos_academicos = CursoAcademico.objects.all().order_by('-año')

    context = {
        'Rol': rol,
        'Perfil': profile,
        'Title': 'Gestión de Horarios',
        'horarios_generados': horarios_generados,
        'horarios_pendientes': horarios_pendientes,
        'todos_horarios': todos_horarios,
        'grados': grados,
        'cursos_academicos': cursos_academicos,
    }
    
    return render(request, 'dashboard/decano/horarios.html', context)


@login_required
def decano_generar_horario(request):
    """Vista para generar un nuevo horario"""
    rol, profile = obtain_rol(request.user)
    
    if rol != 'Decano':
        return redirect('dashboard-inicio')
    
    if request.method == 'POST':
        curso_academico_id = request.POST.get('curso_academico')
        grado_id = request.POST.get('grado')
        curso = request.POST.get('curso')
        
        if curso_academico_id and grado_id and curso:
            resultado = generar_horario(curso_academico_id, grado_id, int(curso))
            
            if resultado['success']:
                messages.success(request, resultado['mensaje'])
                if resultado.get('advertencias'):
                    for adv in resultado['advertencias']:
                        messages.warning(request, adv)
            else:
                for error in resultado.get('errores', []):
                    messages.error(request, error)
        
        return redirect('decano-horarios')
    
    # Si no es POST, redirigir
    return redirect('decano-horarios')


@login_required
def decano_validar_horario(request, horario_id):
    """Vista para validar un horario"""
    rol, profile = obtain_rol(request.user)
    
    if rol != 'Decano':
        return redirect('dashboard-inicio')
    
    resultado = validar_horario(horario_id)
    
    if resultado['valido']:
        messages.success(request, 'El horario es válido')
    else:
        for error in resultado['errores']:
            messages.error(request, error)
    
    return redirect('decano-horarios')


@login_required
def decano_usuarios(request):
    """Vista para ver y gestionar estudiantes y profesores."""
    rol, profile = obtain_rol(request.user)

    if rol != 'Decano':
        return redirect('dashboard-inicio')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'editar_estudiante':
            estudiante_id = request.POST.get('estudiante_id')
            carrera = request.POST.get('carrera', '')
            anio = request.POST.get('anio', '1')
            estudiante = Estudiante.objects.get(id=estudiante_id)
            estudiante.carrera = carrera
            estudiante.anio = int(anio) if anio else 1
            estudiante.save()
            messages.success(request, 'Estudiante actualizado correctamente')

        elif action == 'crear_usuario':
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', 'alumnoucjc123').strip() or 'alumnoucjc123'
            rol_nuevo = request.POST.get('rol_usuario', 'estudiante')
            nombre = request.POST.get('nombre', '').strip()
            apellidos = request.POST.get('apellidos', '').strip()

            if not email:
                messages.error(request, 'El correo electrónico es obligatorio.')
            elif User.objects.filter(email=email).exists():
                messages.error(request, f'Ya existe un usuario con el correo {email}.')
            else:
                username = email.split('@')[0]
                base = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f'{base}{counter}'
                    counter += 1

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=nombre,
                    last_name=apellidos,
                )
                if rol_nuevo == 'profesor':
                    Profesor.objects.create(user=user, disponibilidad=['l', 'm', 'x', 'j', 'v'], asignaturas='')
                    messages.success(request, f'Profesor {email} creado correctamente.')
                else:
                    Estudiante.objects.create(user=user, anio=1, carrera='')
                    messages.success(request, f'Estudiante {email} creado correctamente.')

        return redirect('decano-usuarios')

    estudiantes = Estudiante.objects.select_related('user').all().order_by('user__last_name', 'user__first_name')
    profesores = Profesor.objects.select_related('user').all().order_by('user__last_name', 'user__first_name')
    grados = Grado.objects.all().order_by('nombre')

    context = {
        'Rol': rol,
        'Perfil': profile,
        'Title': 'Gestión de Usuarios',
        'estudiantes': estudiantes,
        'profesores': profesores,
        'grados': grados,
    }

    return render(request, 'dashboard/decano/usuarios.html', context)


# ==================== VISTAS PARA ESTUDIANTES ====================

@login_required
def estudiante_horario(request):
    """Vista del horario del estudiante basado en su grado y curso"""
    rol, profile = obtain_rol(request.user)
    
    if rol != 'Estudiante':
        return redirect('dashboard-inicio')
    
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    except:
        locale.setlocale(locale.LC_TIME, 'es-ES')
    
    now = datetime.now()
    day = now.day
    month_name = now.strftime("%B")
    year = now.year
    date_str = f"{now.strftime('%A').capitalize()}, {day} {month_name} {year}"
    
    # Obtener el curso académico activo
    curso_activo = CursoAcademico.objects.filter(estado='activo').first()
    
    # Obtener el horario del estudiante (basado en su carrera/grado)
    horario = None
    sesiones = SesionHorario.objects.none()
    
    if curso_activo and profile:
        # Buscar horario aprobado para el grado del estudiante
        try:
            grado = Grado.objects.get(nombre=profile.carrera)
            horario = Horario.objects.filter(
                curso_academico=curso_activo,
                grado=grado,
                estado='aprobado'
            ).first()
            
            if horario:
                sesiones = SesionHorario.objects.filter(
                    horario=horario
                ).select_related('asignatura', 'profesor')
        except Grado.DoesNotExist:
            pass
    
    # Organizar sesiones por día
    sesiones_por_dia = {}
    for dia in ['l', 'm', 'x', 'j', 'v']:
        sesiones_por_dia[dia] = sesiones.filter(dia=dia).order_by('hora_inicio')
    
    context = {
        'Rol': rol,
        'Perfil': profile,
        'Title': f'Dashboard - {rol}',
        'Date': date_str,
        'day': day,
        'month_name': month_name,
        'year': year,
        'horario': horario,
        'sesiones': sesiones,
        'sesiones_por_dia': sesiones_por_dia,
    }
    
    return render(request, 'dashboard/estudiante/horario.html', context)