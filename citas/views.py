from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model, login, logout, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Doctor, Paciente, Cita
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import os

User = get_user_model()

# Create your views here.

# Vistas de autenticación
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Registro de nuevos usuarios
    """
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')
    tipo = request.data.get('tipo')  # 'doctor' o 'paciente'
    
    if not all([username, password, email, tipo]):
        return Response(
            {'error': 'Faltan datos requeridos'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'El nombre de usuario ya existe'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = User.objects.create_user(
        username=username,
        password=password,
        email=email
    )
    
    # Crear perfil según el tipo
    if tipo == 'doctor':
        Doctor.objects.create(
            user=user,
            especialidad=request.data.get('especialidad', ''),
            telefono=request.data.get('telefono', '')
        )
    elif tipo == 'paciente':
        Paciente.objects.create(
            user=user,
            telefono=request.data.get('telefono', ''),
            fecha_nacimiento=request.data.get('fecha_nacimiento')
        )
    
    refresh = RefreshToken.for_user(user)
    
    login(request, user)
    messages.success(request, 'Registro exitoso')
    return redirect('home')

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Login de usuarios y generación de tokens
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Por favor proporcione username y password'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {'error': 'Usuario no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if not user.check_password(password):
        return Response(
            {'error': 'Contraseña incorrecta'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    refresh = RefreshToken.for_user(user)
    
    login(request, user)
    messages.success(request, 'Inicio de sesión exitoso')
    return redirect('home')

def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión')
    return redirect('home')

# Vistas de citas
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_citas(request):
    """
    Lista las citas del usuario autenticado
    """
    try:
        doctor = Doctor.objects.get(user=request.user)
        citas = Cita.objects.filter(doctor=doctor)
    except Doctor.DoesNotExist:
        try:
            paciente = Paciente.objects.get(user=request.user)
            citas = Cita.objects.filter(paciente=paciente)
        except Paciente.DoesNotExist:
            return Response(
                {'error': 'Usuario no tiene perfil de doctor ni paciente'},
                status=status.HTTP_403_FORBIDDEN
            )
    
    citas_data = [{
        'id': cita.id,
        'fecha': cita.fecha,
        'hora': cita.hora,
        'estado': cita.estado,
        'notas': cita.notas,
        'paciente': str(cita.paciente),
        'doctor': str(cita.doctor)
    } for cita in citas]
    
    return Response({
        'status': 'success',
        'data': {'citas': citas_data}
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_cita(request):
    """
    Crea una nueva cita
    """
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return Response(
            {'error': 'Solo los doctores pueden crear citas'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    paciente_id = request.data.get('paciente_id')
    fecha = request.data.get('fecha')
    hora = request.data.get('hora')
    
    if not all([paciente_id, fecha, hora]):
        return Response(
            {'error': 'Faltan datos requeridos'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        paciente = Paciente.objects.get(id=paciente_id)
    except Paciente.DoesNotExist:
        return Response(
            {'error': 'Paciente no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    cita = Cita.objects.create(
        doctor=doctor,
        paciente=paciente,
        fecha=fecha,
        hora=hora,
        notas=request.data.get('notas', '')
    )
    
    return Response({
        'status': 'success',
        'message': 'Cita creada exitosamente',
        'data': {
            'id': cita.id,
            'fecha': cita.fecha,
            'hora': cita.hora,
            'estado': cita.estado,
            'notas': cita.notas,
            'paciente': str(cita.paciente),
            'doctor': str(cita.doctor)
        }
    }, status=status.HTTP_201_CREATED)

def register(request):
    """Vista para registro de usuarios"""
    # Inicializar el diccionario de contexto
    context = {
        'data': {},
        'errors': {},
        'especialidades': Doctor.ESPECIALIDADES
    }
    
    if request.method == 'POST':
        print("Datos recibidos en POST:", request.POST)
        print("Archivos recibidos:", request.FILES)
        
        # Obtener y validar los datos básicos
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        tipo = request.POST.get('tipo')
        telefono = request.POST.get('telefono', '').strip()
        
        print(f"Procesando registro para: {first_name} {last_name}")
        
        # Guardar datos en el contexto
        context['data'] = {
            'username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'tipo': tipo,
            'telefono': telefono
        }
        
        # Validaciones
        if not first_name:
            context['errors']['first_name'] = 'El nombre es obligatorio'
        if not last_name:
            context['errors']['last_name'] = 'El apellido es obligatorio'
        if not username:
            context['errors']['username'] = 'El nombre de usuario es obligatorio'
        if not email:
            context['errors']['email'] = 'El correo electrónico es obligatorio'
        if not password:
            context['errors']['password'] = 'La contraseña es obligatoria'
        if not password2:
            context['errors']['password2'] = 'Debe confirmar la contraseña'
        if not tipo:
            context['errors']['tipo'] = 'Debe seleccionar un tipo de usuario'
        if not telefono:
            context['errors']['telefono'] = 'El teléfono es obligatorio'
        
        if password != password2:
            context['errors']['password2'] = 'Las contraseñas no coinciden'
        
        if User.objects.filter(username=username).exists():
            context['errors']['username'] = 'El nombre de usuario ya existe'
        
        if User.objects.filter(email=email).exists():
            context['errors']['email'] = 'El correo electrónico ya está registrado'
        
        print("Errores de validación:", context['errors'])
        
        # Si no hay errores, proceder con el registro
        if not context['errors']:
            try:
                # Crear usuario
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )
                
                print(f"Usuario creado: {user.username} ({user.get_full_name()})")
                
                # Crear perfil según el tipo
                if tipo == 'doctor':
                    especialidad = request.POST.get('especialidad', '').strip()
                    numero_licencia = request.POST.get('numero_licencia', '').strip()
                    documento_licencia = request.FILES.get('documento_licencia')
                    
                    if not especialidad:
                        context['errors']['especialidad'] = 'La especialidad es obligatoria'
                    if not numero_licencia:
                        context['errors']['numero_licencia'] = 'El número de licencia es obligatorio'
                    
                    if context['errors']:
                        print("Errores en datos de doctor:", context['errors'])
                        user.delete()
                        return render(request, 'agendamiento/register.html', context)
                    
                    if Doctor.objects.filter(numero_licencia=numero_licencia).exists():
                        user.delete()
                        context['errors']['numero_licencia'] = 'El número de licencia ya está registrado'
                        return render(request, 'agendamiento/register.html', context)
                    
                    try:
                        doctor = Doctor.objects.create(
                            user=user,
                            especialidad=especialidad,
                            telefono=telefono,
                            numero_licencia=numero_licencia,
                            verificado=False,
                            activo=False
                        )
                        
                        print(f"Doctor creado: {doctor}")
                        
                        # Guardar documento de licencia si se proporcionó
                        if documento_licencia:
                            os.makedirs(os.path.join('media', 'documentos_doctores', str(doctor.id)), exist_ok=True)
                            with open(os.path.join('media', 'documentos_doctores', str(doctor.id), 'licencia.pdf'), 'wb+') as destination:
                                for chunk in documento_licencia.chunks():
                                    destination.write(chunk)
                        
                        # Guardar certificaciones adicionales
                        certificaciones = request.FILES.getlist('certificaciones')
                        for i, cert in enumerate(certificaciones):
                            with open(os.path.join('media', 'documentos_doctores', str(doctor.id), f'certificacion_{i+1}.pdf'), 'wb+') as destination:
                                for chunk in cert.chunks():
                                    destination.write(chunk)
                        
                        messages.success(request, 'Tu cuenta ha sido creada y está pendiente de verificación por el administrador')
                        
                    except Exception as e:
                        print(f"Error al crear doctor: {e}")
                        user.delete()
                        context['errors']['general'] = f'Error al crear el perfil de doctor: {str(e)}'
                        return render(request, 'agendamiento/register.html', context)
                    
                elif tipo == 'paciente':
                    fecha_nacimiento = request.POST.get('fecha_nacimiento')
                    
                    if not fecha_nacimiento:
                        user.delete()
                        context['errors']['fecha_nacimiento'] = 'La fecha de nacimiento es obligatoria'
                        return render(request, 'agendamiento/register.html', context)
                    
                    try:
                        Paciente.objects.create(
                            user=user,
                            telefono=telefono,
                            fecha_nacimiento=fecha_nacimiento
                        )
                        messages.success(request, 'Registro exitoso. ¡Bienvenido!')
                        
                    except Exception as e:
                        print(f"Error al crear paciente: {e}")
                        user.delete()
                        context['errors']['general'] = f'Error al crear el perfil de paciente: {str(e)}'
                        return render(request, 'agendamiento/register.html', context)
                
                login(request, user)
                return redirect('agendamiento:home')
                
            except Exception as e:
                print(f"Error general en el registro: {e}")
                context['errors']['general'] = f'Error en el registro: {str(e)}'
                return render(request, 'agendamiento/register.html', context)
        
        return render(request, 'agendamiento/register.html', context)
    
    return render(request, 'agendamiento/register.html', context)

def login_view(request):
    """
    Vista para login de usuarios (web y API)
    """
    if request.method == 'POST':
        data = request.POST if request.content_type == 'application/x-www-form-urlencoded' else request.data
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            messages.error(request, 'Por favor proporcione username y password')
            return redirect('login') if not request.content_type == 'application/json' else Response(
                {'error': 'Por favor proporcione username y password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=username, password=password)
        if user is None:
            messages.error(request, 'Credenciales inválidas')
            return redirect('login') if not request.content_type == 'application/json' else Response(
                {'error': 'Credenciales inválidas'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        login(request, user)
        messages.success(request, 'Inicio de sesión exitoso')
        return redirect('home')
    
    return render(request, 'agendamiento/login.html')

@login_required
def citas_disponibles(request):
    """
    Vista para ver citas disponibles
    """
    try:
        if hasattr(request.user, 'doctor'):
            citas = Cita.objects.filter(doctor=request.user.doctor)
        else:
            citas = Cita.objects.filter(paciente=request.user.paciente)
    except (Doctor.DoesNotExist, Paciente.DoesNotExist):
        messages.error(request, 'Usuario no tiene perfil de doctor ni paciente')
        return redirect('home')
    
    return render(request, 'agendamiento/citas_disponibles.html', {'citas': citas})

@login_required
def agendar_cita(request):
    """
    Vista para agendar citas
    """
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        
        if not all([doctor_id, fecha, hora]):
            messages.error(request, 'Faltan datos requeridos')
            return redirect('agendar_cita')
        
        try:
            doctor = Doctor.objects.get(id=doctor_id)
            paciente = request.user.paciente
            
            cita = Cita.objects.create(
                doctor=doctor,
                paciente=paciente,
                fecha=fecha,
                hora=hora
            )
            messages.success(request, 'Cita agendada exitosamente')
            return redirect('citas_disponibles')
            
        except (Doctor.DoesNotExist, Paciente.DoesNotExist):
            messages.error(request, 'Error al agendar la cita')
            return redirect('agendar_cita')
    
    doctores = Doctor.objects.all()
    return render(request, 'agendamiento/agendar_cita.html', {'doctores': doctores})
