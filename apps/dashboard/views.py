from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
import locale

# Funcion auxiliar para obtener el rol del usuario segun su perfil
def obtain_rol(user):
    if hasattr(user, 'perfil_estudiante'):
        return 'Estudiante', user.perfil_estudiante
    elif hasattr(user, 'perfil_profesor'):
        return 'Profesor', user.perfil_profesor
    elif hasattr(user, 'perfil_decano'):
        return 'Decano', user.perfil_decano
    return None, None

# Redireccionamiento al Dashboard
@login_required
def home_redirect(request):
    rol, profile = obtain_rol(request.user)

    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    except:
        locale.setlocale(locale.LC_TIME, 'es-ES')

    now = datetime.now()
    
    # Encontramos el lunes de la semana actual
    actual_monday = now - timedelta(days=now.weekday())

    # Creamos una lista con los números de los 7 días (Lunes a Domingo)
    week_days = [(actual_monday + timedelta(days=i)).day for i in range(7)]

    day = now.day
    month_name = now.strftime("%B")
    year = now.year
    date_str = f"{now.strftime('%A').capitalize()}, {day} {month_name} {year}"

    context = {
        'Rol': rol,
        'Perfil': profile,
        'Title': f'Dashboard - {rol}',
        'Date': date_str,
        'day': day,
        'month_name': month_name,
        'year': year,
        'semana_dias': week_days, 
    }
    
    return render(request, 'dashboard/home.html', context)

# Redireccionamiento al Horario
@login_required
def schedule_redirect(request):
    rol, profile = obtain_rol(request.user)
    try:
        locale.setlocale(locale.LC_TIME, 'es_es.UTF-8')
    except:
        locale.setlocale(locale.LC_TIME, 'es-es')
    
    now = datetime.now()
    actual_monday = now - timedelta(days=now.weekday())
    week_days = [actual_monday + timedelta(days=i) for i in range(5)]

    day = now.day
    month_name = now.strftime("%B")
    year = now.year
    date_str = f"{now.strftime('%A').capitalize()}, {day} {month_name} {year}"

    context = {
        'Rol': rol,
        'Perfil': profile,
        'Title': f'Dashboard - {rol}',
        'Date': date_str,
        'day': day,
        'month_name': month_name,
        'year': year,
        'semana_dias': week_days, # Ahora contiene objetos datetime
    }
   
    return render(request, 'dashboard/schedule.html', context)