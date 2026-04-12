from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

def index_redirect(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/inicio') 
    return redirect('/auth') 

urlpatterns = [
    # Defecto
    path('admin/', admin.site.urls),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Incluir vistas
    path('auth/', include('apps.authy.urls')),
    path('dashboard/', include('apps.dashboard.urls')),

    # Redireccionamiento
    path('', index_redirect, name='index'),

    # Recarga automática a la hora de usar los estilos de TailwindCSS
    path("__reload__/", include("django_browser_reload.urls"))
]
