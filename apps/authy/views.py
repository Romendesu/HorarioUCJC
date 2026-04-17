from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django import forms

# 1. Definición del Formulario Personalizado
class EmailAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.EmailInput(attrs={
        'class': 'w-full h-12 border-none bg-neutral p-5 input input-primary font-label rounded-sm',
        'placeholder': 'Correo Institucional',
    }))
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full h-12 border-none bg-neutral p-5 input input-primary font-label rounded-sm',
        'placeholder': 'Ingrese su contraseña',
    }))

# 2. Vista de Autenticación
def render_auth_view(request):
    if request.user.is_authenticated:
        return redirect('auth-form')

    if request.method == "GET":
        context = {
            'Title': 'Autentificación',
            'form': EmailAuthenticationForm()
        }
        return render(request, 'auth/auth.html', context)
    
    if request.method == "POST":
        identifier = request.POST.get('username')
        password_input = request.POST.get('password')
        
        User = get_user_model()
        username_to_auth = identifier 

        try:
            # Buscamos el usuario por email
            user_obj = User.objects.get(email=identifier)
            # Pasamos su username real (ej: "Alumno")
            username_to_auth = user_obj.username
        except User.DoesNotExist:
            pass # Si no existe, intentamos con el identificador tal cual

        # Ahora el formulario aceptará "Alumno" porque es un CharField
        form = EmailAuthenticationForm(request, data={
            'username': username_to_auth,
            'password': password_input
        })

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard-inicio')
        else:
            context = {
                'Title': 'Autentificación',
                'form': form,
                'error': "Credenciales incorrectas. Por favor, verifica tu correo y contraseña."
            }
            return render(request, 'auth/auth.html', context)