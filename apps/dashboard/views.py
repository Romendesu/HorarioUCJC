from django.shortcuts import render
from django.contrib.auth.decorators import login_required

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
    # Obtener el rol del usuario
    rol, profile = obtain_rol(request.user)

    # Obtener la fecha mediante datetime y la traducimos al español
    from datetime import datetime
    import locale
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

    now = datetime.now()
    day_name = now.strftime('%A').capitalize()
    day = now.day
    month = now.strftime("%B")
    year = now.year

    date = f"{day_name}, {day} {month} {year}"

    # Configuramos el contexto segun el rol del usuario
    if not rol:
        return render(request, 'auth/no_perfil.html', {'user': request.user})
    
    # Actualizamos el contexto
    context = {
        'Rol': rol,
        'Perfil': profile,
        'Title': f'Dashboard - {rol}',
        'Date': date
    }
    
    return render(request, 'dashboard/home.html', context)