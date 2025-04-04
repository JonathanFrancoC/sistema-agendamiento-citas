from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Doctor, Paciente, Cita

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        tipo = request.POST.get('tipo')  # 'doctor' o 'paciente'
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe')
            return redirect('register')
        
        user = User.objects.create_user(username=username, password=password, email=email)
        
        if tipo == 'doctor':
            Doctor.objects.create(
                user=user,
                especialidad=request.POST.get('especialidad', ''),
                telefono=request.POST.get('telefono', '')
            )
        else:
            Paciente.objects.create(
                user=user,
                telefono=request.POST.get('telefono', ''),
                fecha_nacimiento=request.POST.get('fecha_nacimiento')
            )
        
        login(request, user)
        messages.success(request, 'Registro exitoso')
        return redirect('home')
    
    return render(request, 'citas/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Inicio de sesión exitoso')
            return redirect('home')
        else:
            messages.error(request, 'Credenciales inválidas')
    
    return render(request, 'citas/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión')
    return redirect('home')

@login_required
def agendar_cita(request):
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        
        try:
            doctor = Doctor.objects.get(id=doctor_id)
            paciente = Paciente.objects.get(user=request.user)
            
            Cita.objects.create(
                doctor=doctor,
                paciente=paciente,
                fecha=fecha,
                hora=hora
            )
            
            messages.success(request, 'Cita agendada exitosamente')
            return redirect('citas_disponibles')
            
        except (Doctor.DoesNotExist, Paciente.DoesNotExist):
            messages.error(request, 'Error al agendar la cita')
    
    doctores = Doctor.objects.all()
    return render(request, 'citas/agendar_cita.html', {'doctores': doctores})

@login_required
def citas_disponibles(request):
    try:
        if hasattr(request.user, 'doctor'):
            # Si es doctor, mostrar sus citas
            citas = Cita.objects.filter(doctor=request.user.doctor)
        else:
            # Si es paciente, mostrar sus citas
            citas = Cita.objects.filter(paciente=request.user.paciente)
            
        return render(request, 'citas/citas_disponibles.html', {'citas': citas})
        
    except (Doctor.DoesNotExist, Paciente.DoesNotExist):
        messages.error(request, 'Error al cargar las citas')
        return redirect('home') 