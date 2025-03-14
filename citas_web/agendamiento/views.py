from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import RegistroUsuarioForm
from .models import Cita
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404


def home(request):
    """Página de inicio"""
    print("Renderizando home.html")
    return render(request, "agendamiento/home.html")

def agendar_cita(request):
    """Vista para agendar una cita"""
    return render(request, "agendamiento/agendar_cita.html")

def register(request):
    """Vista para el registro de usuarios"""
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            print("✅ Usuario registrado con éxito:", user.username)  # DEPURACIÓN
            login(request, user)
            messages.success(request, "Registro exitoso. ¡Bienvenido!")
            return redirect("citas_disponibles")

        else:
            print("❌ Errores en el formulario:", form.errors)  # DEPURACIÓN
            messages.error(request, "Por favor, corrija los errores en el formulario.")
    else:
        form = RegistroUsuarioForm()
    return render(request, "agendamiento/register.html", {"form": form})


def login_view(request):
    """Vista para iniciar sesión"""
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Has iniciado sesión correctamente.")
            return redirect("citas_disponibles") 
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = AuthenticationForm()
    return render(request, "agendamiento/login.html", {"form": form})

def logout_view(request):
    """Cerrar sesión y redirigir a home"""
    logout(request)
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect("home")

def citas_disponibles(request):
    citas = Cita.objects.filter(disponible=True) 
    return render(request, "agendamiento/citas_disponibles.html", {"citas": citas})

@login_required
def reservar_cita(request, cita_id):
    """Vista para reservar una cita"""
    cita = get_object_or_404(Cita, id=cita_id)
    
    if cita.disponible:
        cita.usuario = request.user
        cita.disponible = False
        cita.save()
        return redirect("citas_disponibles")

    messages.success(request, "Cita reservada con éxito.")
    return redirect("citas_disponibles")