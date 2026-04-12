from django.shortcuts import render

# Create your views here.
def auth(request):
    context = {
        "Title": "Autentificación"
    }

    return render(request, 'core/auth', context)