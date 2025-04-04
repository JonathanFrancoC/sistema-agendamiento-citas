from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import UserRegisterForm, LoginForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from citas.models import Doctor, Cita, Paciente
from django.utils import timezone
from django.http import JsonResponse
from itertools import groupby
from operator import attrgetter
from datetime import datetime, timedelta, time
import pytz
import json
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.conf import settings
import os
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token

User = get_user_model()

def home(request):
    """Vista de la página principal"""
    if request.user.is_authenticated:
        try:
            if request.user.is_superuser:
                return redirect('agendamiento:admin_dashboard')
            elif hasattr(request.user, 'doctor'):
                doctor = request.user.doctor
                hoy = timezone.now().date()
                
                # Obtener citas de hoy
                citas_hoy = Cita.objects.filter(
                    doctor=doctor,
                    fecha__date=hoy
                ).order_by('fecha')
                
                # Obtener citas pendientes
                citas_pendientes = Cita.objects.filter(
                    doctor=doctor,
                    fecha__date__gte=hoy,
                    estado='pendiente'
                )
                
                # Obtener próximas citas
                proximas_citas = Cita.objects.filter(
                    doctor=doctor,
                    fecha__date__gte=hoy,
                    estado='pendiente'
                ).order_by('fecha')[:5]
                
                # Obtener total de pacientes únicos
                total_pacientes = Cita.objects.filter(
                    doctor=doctor
                ).values('paciente').distinct().count()
                
                # Obtener próxima cita
                proxima_cita = proximas_citas.first()
                proxima_cita_hora = proxima_cita.fecha.strftime('%H:%M') if proxima_cita else None
                
                context = {
                    'citas_hoy': citas_hoy,
                    'citas_hoy_count': citas_hoy.count(),
                    'citas_pendientes_count': citas_pendientes.count(),
                    'proximas_citas': proximas_citas,
                    'total_pacientes': total_pacientes,
                    'proxima_cita_hora': proxima_cita_hora
                }
                
                return render(request, "agendamiento/doctor_dashboard.html", context)
            elif hasattr(request.user, 'paciente'):
                return render(request, "agendamiento/home.html")
            else:
                messages.warning(request, "No tienes un perfil asociado.")
        except (Doctor.DoesNotExist, Paciente.DoesNotExist):
            messages.warning(request, "No tienes un perfil asociado.")
    return render(request, "agendamiento/home.html")

@login_required
def agendar_cita(request):
    """Vista para agendar una cita"""
    try:
        paciente = Paciente.objects.get(user=request.user)
    except Paciente.DoesNotExist:
        messages.error(request, "No tienes un perfil de paciente asociado.")
        return redirect('agendamiento:home')

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        notas = request.POST.get('notas', '')

        print(f"Datos recibidos - doctor_id: {doctor_id}, fecha: {fecha}, hora: {hora}, notas: {notas}")

        if not all([doctor_id, fecha, hora]):
            messages.error(request, "Por favor complete todos los campos requeridos.")
            return redirect('agendamiento:agendar_cita')

        try:
            doctor = Doctor.objects.get(id=doctor_id)
            # Combinar fecha y hora en un datetime y asignar zona horaria
            fecha_hora = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
            tijuana_tz = pytz.timezone('America/Tijuana')
            fecha_hora = tijuana_tz.localize(fecha_hora)
            
            # Verificar si ya existe una cita para este doctor en esta fecha y hora
            cita_existente = Cita.objects.filter(
                doctor=doctor,
                fecha=fecha_hora,
                estado='pendiente'
            ).exists()
            
            if cita_existente:
                messages.error(request, "Ya existe una cita agendada para esta fecha y hora.")
                return redirect('agendamiento:agendar_cita')
            
            # Crear la cita
            Cita.objects.create(
                doctor=doctor,
                paciente=paciente,
                fecha=fecha_hora,
                estado='pendiente',
                notas=notas
            )
            
            messages.success(request, "¡Cita agendada con éxito!")
            return redirect('agendamiento:mis_citas')
            
        except Doctor.DoesNotExist:
            messages.error(request, "El doctor seleccionado no existe.")
        except Exception as e:
            messages.error(request, f"Error al agendar la cita: {str(e)}")
        
        return redirect('agendamiento:agendar_cita')

    # GET request
    doctores = Doctor.objects.all()
    today = timezone.now().date()
    return render(request, 'agendamiento/agendar_cita.html', {
        'doctores': doctores,
        'today': today
    })

@login_required
def get_horarios_disponibles(request):
    doctor_id = request.GET.get('doctor_id')
    fecha_str = request.GET.get('fecha')

    if not doctor_id or not fecha_str:
        return JsonResponse({'error': 'Faltan parámetros requeridos'}, status=400)

    try:
        doctor = Doctor.objects.get(id=doctor_id)
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        
        # Obtener la hora actual en la zona horaria de Tijuana
        tijuana_tz = pytz.timezone('America/Tijuana')
        ahora = timezone.localtime(timezone.now(), tijuana_tz)
        fecha_actual = ahora.date()
        
        print(f"Fecha solicitada: {fecha}, Fecha actual: {fecha_actual}")
        print(f"Hora actual en Tijuana: {ahora.time()}")
        print(f"Hora inicio doctor: {doctor.hora_inicio}")
        
        # Si es una fecha pasada, no mostrar horarios
        if fecha < fecha_actual:
            return JsonResponse({
                'mensaje': 'No se pueden agendar citas en fechas pasadas',
                'horarios': []
            })
        
        # Verificar si el doctor trabaja en esta fecha
        if not doctor.trabaja_en_fecha(fecha):
            return JsonResponse({
                'mensaje': 'El doctor no atiende este día',
                'horarios': []
            })
        
        # Generar todos los horarios del día
        horarios = []
        
        # Determinar la hora de inicio
        if fecha == fecha_actual:
            # Para el día actual, comenzar desde la siguiente media hora
            minutos_actuales = ahora.hour * 60 + ahora.minute
            minutos_redondeados = ((minutos_actuales + 30) // 30) * 30
            hora_inicio = time(minutos_redondeados // 60, minutos_redondeados % 60)
            print(f"Hora de inicio calculada para hoy: {hora_inicio}")
        else:
            hora_inicio = doctor.hora_inicio
            print(f"Usando hora de inicio normal: {hora_inicio}")

        # Convertir a datetime para poder sumar minutos
        hora_actual = datetime.combine(fecha, hora_inicio)
        hora_fin = datetime.combine(fecha, doctor.hora_fin)
        
        # Hacer aware los datetime con la zona horaria de Tijuana
        hora_actual = tijuana_tz.localize(hora_actual)
        hora_fin = tijuana_tz.localize(hora_fin)
        
        print(f"Hora actual para citas: {hora_actual}")
        print(f"Hora fin para citas: {hora_fin}")
        
        # Obtener citas existentes para ese día
        citas_existentes = Cita.objects.filter(
            doctor=doctor,
            fecha__date=fecha,
            estado='pendiente'
        ).values_list('fecha', flat=True)
        
        # Convertir las horas de las citas a set para búsqueda más eficiente
        horas_ocupadas = {cita.astimezone(tijuana_tz).strftime('%H:%M') for cita in citas_existentes}
        print(f"Horas ocupadas: {horas_ocupadas}")
        
        # Generar horarios cada 30 minutos
        while hora_actual < hora_fin:
            hora_str = hora_actual.strftime('%H:%M')
            
            # Para el día actual, verificar si la hora ya pasó
            es_pasado = False
            if fecha == fecha_actual:
                es_pasado = hora_actual <= ahora
                print(f"Evaluando hora {hora_str}: es_pasado={es_pasado}")
            
            # Solo agregar el horario si no ha pasado y no está ocupado
            if not es_pasado:
                esta_ocupado = hora_str in horas_ocupadas
                horarios.append({
                    'hora': hora_str,
                    'disponible': not esta_ocupado,
                    'ocupado': esta_ocupado
                })
                print(f"Agregando horario {hora_str}: disponible={not esta_ocupado}")
            
            hora_actual += timedelta(minutes=30)

        if not horarios:
            return JsonResponse({
                'mensaje': 'No hay horarios disponibles para esta fecha',
                'horarios': []
            })

        print(f"Total horarios generados: {len(horarios)}")
        return JsonResponse({
            'horarios': horarios,
            'mensaje': 'Horarios cargados exitosamente'
        })

    except Doctor.DoesNotExist:
        return JsonResponse({'error': 'Doctor no encontrado'}, status=404)
    except ValueError as e:
        return JsonResponse({'error': f'Error de formato: {str(e)}'}, status=400)
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return JsonResponse({'error': f'Error inesperado: {str(e)}'}, status=500)

def register(request):
    """Vista para registro de usuarios"""
    # Inicializar el diccionario de contexto
    context = {
        'data': {},
        'errors': {},
        'especialidades': Doctor.ESPECIALIDADES,
        'yesterday': datetime.now().date() - timedelta(days=1),
        'debug': settings.DEBUG
    }
    
    print("Especialidades disponibles:", Doctor.ESPECIALIDADES)  # Debug log
    
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
                    certificaciones = request.FILES.getlist('certificaciones')
                    
                    print("Documento de licencia:", documento_licencia)
                    print("Certificaciones:", certificaciones)
                    
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
                        # Crear doctor
                        doctor = Doctor.objects.create(
                            user=user,
                            especialidad=especialidad,
                            telefono=telefono,
                            numero_licencia=numero_licencia,
                            activo=False,
                            verificado=False
                        )
                        
                        # Guardar documento de licencia
                        if documento_licencia:
                            try:
                                extension = os.path.splitext(documento_licencia.name)[1].lower()
                                nombre_archivo = f'doctor_{doctor.id}_licencia{extension}'
                                doctor.documento_licencia.save(
                                    nombre_archivo,
                                    documento_licencia
                                )
                                print(f"Licencia guardada como: {nombre_archivo}")
                            except Exception as e:
                                print(f"Error al guardar licencia: {e}")
                        
                        # Guardar certificaciones
                        for i, cert in enumerate(certificaciones, 1):
                            try:
                                extension = os.path.splitext(cert.name)[1].lower()
                                nombre_archivo = f'doctor_{doctor.id}_certificacion_{i}{extension}'
                                if i == 1:
                                    doctor.certificacion_1.save(nombre_archivo, cert)
                                elif i == 2:
                                    doctor.certificacion_2.save(nombre_archivo, cert)
                                elif i == 3:
                                    doctor.certificacion_3.save(nombre_archivo, cert)
                                print(f"Certificación {i} guardada como: {nombre_archivo}")
                            except Exception as e:
                                print(f"Error al guardar certificación {i}: {e}")
                        
                        messages.success(request, 'Tu cuenta ha sido creada y está pendiente de verificación por el administrador')
                        return redirect('agendamiento:login')
                        
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

@ensure_csrf_cookie
def login_view(request):
    """Vista para iniciar sesión"""
    if request.user.is_authenticated:
        return redirect('agendamiento:home')
    
    # Asegurar que el token CSRF esté establecido
    get_token(request)
    
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, '¡Bienvenido de vuelta!')
                return redirect('agendamiento:home')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    
    response = render(request, 'agendamiento/login.html', {
        'form': form,
        'debug': settings.DEBUG
    })
    response.set_cookie('csrftoken', get_token(request), samesite='Lax')
    return response

def logout_view(request):
    if request.user.is_authenticated:
        messages.success(request, '¡Hasta pronto!')
        logout(request)
    return redirect('agendamiento:home')

@login_required
def citas_disponibles(request):
    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        doctor_id = request.POST.get('doctor')
        try:
            doctor = Doctor.objects.get(id=doctor_id)
            # Obtener las citas existentes para ese día
            fecha_inicio = datetime.strptime(fecha, "%Y-%m-%d").replace(hour=0, minute=0)
            fecha_fin = fecha_inicio.replace(hour=23, minute=59)
            
            citas_ocupadas = Cita.objects.filter(
                doctor=doctor,
                fecha__range=(fecha_inicio, fecha_fin),
                estado='pendiente'
            ).values_list('fecha', flat=True)
            
            # Convertir a horas
            horas_ocupadas = [cita.strftime('%H:%M') for cita in citas_ocupadas]
            
            # Generar todos los horarios posibles
            horarios_disponibles = []
            hora_actual = datetime.strptime('08:00', '%H:%M')
            hora_fin = datetime.strptime('17:00', '%H:%M')
            
            while hora_actual.time() <= hora_fin.time():
                hora_str = hora_actual.strftime('%H:%M')
                if hora_str not in horas_ocupadas:
                    horarios_disponibles.append(hora_str)
                hora_actual = hora_actual + timedelta(minutes=30)
            
            return JsonResponse({'horarios': horarios_disponibles})
        except Doctor.DoesNotExist:
            return JsonResponse({'error': 'Doctor no encontrado'}, status=404)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def reservar_cita(request, cita_id):
    """Vista para reservar una cita"""
    if request.method == "POST":
        try:
            cita = get_object_or_404(Cita, id=cita_id)
            
            if not cita.disponible:
                messages.error(request, "Esta cita ya no está disponible")
                return redirect("agendamiento:citas_disponibles")
            
            cita.usuario = request.user
            cita.disponible = False
            cita.save()
            
            messages.success(request, "¡Cita reservada con éxito!")
            return redirect("agendamiento:citas_disponibles")
            
        except Exception as e:
            messages.error(request, f"Error al reservar la cita: {str(e)}")
            return redirect("agendamiento:citas_disponibles")
    
    return redirect("agendamiento:citas_disponibles")

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    if not username or not password or not email:
        return Response(
            {'error': 'Por favor proporcione username, password y email'},
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

    refresh = RefreshToken.for_user(user)

    return Response({
        'user': {
            'username': user.username,
            'email': user.email
        },
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Endpoint para autenticación de usuarios y generación de tokens JWT
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {
                'error': 'Credenciales incompletas',
                'message': 'Por favor proporcione username y password'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {
                'error': 'Usuario no encontrado',
                'message': 'El usuario no existe en el sistema'
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if not user.check_password(password):
        return Response(
            {
                'error': 'Credenciales inválidas',
                'message': 'La contraseña proporcionada es incorrecta'
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        return Response(
            {
                'error': 'Usuario inactivo',
                'message': 'La cuenta está desactivada'
            },
            status=status.HTTP_403_FORBIDDEN
        )

    refresh = RefreshToken.for_user(user)

    return Response({
        'status': 'success',
        'message': 'Login exitoso',
        'data': {
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_active': user.is_active,
                'last_login': user.last_login
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'token_type': 'Bearer',
                'expires_in': 3600  # 1 hora en segundos
            }
        }
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Logout exitoso'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    Endpoint protegido que requiere autenticación JWT
    Devuelve el perfil del usuario autenticado
    """
    user = request.user
    
    return Response({
        'status': 'success',
        'data': {
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_active': user.is_active,
                'last_login': user.last_login,
                'date_joined': user.date_joined,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser
            }
        }
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_citas(request):
    """
    Endpoint protegido que requiere autenticación JWT
    Devuelve las citas del usuario autenticado
    """
    citas = Cita.objects.filter(usuario=request.user)
    
    citas_data = [{
        'id': cita.id,
        'fecha': cita.fecha,
        'hora': cita.hora,
        'disponible': cita.disponible,
        'servicio': cita.servicio,
        'estado': 'Reservada' if not cita.disponible else 'Disponible'
    } for cita in citas]
    
    return Response({
        'status': 'success',
        'data': {
            'citas': citas_data
        }
    }, status=status.HTTP_200_OK)

@login_required
def mis_citas(request):
    """Vista para mostrar las citas del usuario (doctor o paciente)"""
    try:
        if hasattr(request.user, 'doctor'):
            # Si es un doctor
            doctor = Doctor.objects.get(user=request.user)
            citas = Cita.objects.filter(doctor=doctor).order_by('fecha')
            return render(request, 'agendamiento/mis_citas.html', {
                'citas': citas,
                'es_doctor': True,
                'doctor': doctor
            })
        elif hasattr(request.user, 'paciente'):
            # Si es un paciente
            paciente = Paciente.objects.get(user=request.user)
            citas = Cita.objects.filter(paciente=paciente).order_by('fecha')
            return render(request, 'agendamiento/mis_citas.html', {
                'citas': citas,
                'es_doctor': False,
                'paciente': paciente
            })
        else:
            messages.error(request, "No tienes un perfil asociado.")
            return redirect('agendamiento:home')
    except (Doctor.DoesNotExist, Paciente.DoesNotExist):
        messages.error(request, "No tienes un perfil asociado.")
        return redirect('agendamiento:home')

@login_required
def confirmar_cita(request, cita_id):
    """Vista para que el doctor confirme una cita"""
    if request.method == 'POST':
        try:
            doctor = Doctor.objects.get(user=request.user)
            cita = get_object_or_404(Cita, id=cita_id, doctor=doctor)
            
            if cita.estado != 'pendiente':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Solo se pueden confirmar citas pendientes.'
                }, status=400)
            
            cita.estado = 'confirmada'
            cita.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Cita confirmada exitosamente.'
            })
            
        except Doctor.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'No tienes permisos para realizar esta acción.'
            }, status=403)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error al confirmar la cita: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Método no permitido'
    }, status=405)

@login_required
def cancelar_cita(request, cita_id):
    """Vista para que el doctor cancele una cita"""
    if request.method == 'POST':
        try:
            doctor = Doctor.objects.get(user=request.user)
            cita = get_object_or_404(Cita, id=cita_id, doctor=doctor)
            
            if cita.estado != 'pendiente':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Solo se pueden cancelar citas pendientes.'
                }, status=400)
            
            cita.estado = 'cancelada'
            cita.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Cita cancelada exitosamente.'
            })
            
        except Doctor.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'No tienes permisos para realizar esta acción.'
            }, status=403)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error al cancelar la cita: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Método no permitido'
    }, status=405)

@login_required
def cambiar_estado_cita(request, cita_id):
    """Vista para cambiar el estado de una cita"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nuevo_estado = data.get('estado')
            
            # Verificar que el usuario es el doctor de la cita
            cita = get_object_or_404(Cita, id=cita_id, doctor__user=request.user)
            
            if nuevo_estado in ['pendiente', 'completada', 'cancelada']:
                cita.estado = nuevo_estado
                cita.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Estado no válido'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
            
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@staff_member_required
def admin_dashboard(request):
    """Vista del panel de administración"""
    # Obtener estadísticas
    total_doctores = Doctor.objects.count()
    print(f"Total de doctores en el sistema: {total_doctores}")
    
    # Obtener doctores no verificados con información detallada
    doctores_no_verificados = Doctor.objects.filter(
        verificado=False
    ).select_related('user').order_by('-user__date_joined')
    
    # Imprimir información de diagnóstico
    print("Doctores no verificados encontrados:")
    for doctor in doctores_no_verificados:
        print(f"- {doctor.user.get_full_name()} (ID: {doctor.id}, Email: {doctor.user.email})")
    
    doctores_pendientes = doctores_no_verificados.count()
    print(f"Total de doctores pendientes: {doctores_pendientes}")
    
    # Obtener doctores verificados con información detallada
    doctores_verificados_lista = Doctor.objects.filter(
        verificado=True
    ).select_related('user').order_by('user__first_name')
    
    doctores_verificados = doctores_verificados_lista.count()
    print(f"Total de doctores verificados: {doctores_verificados}")
    
    # Obtener total de pacientes
    total_pacientes = Paciente.objects.count()
    print(f"Total de pacientes: {total_pacientes}")
    
    context = {
        'total_doctores': total_doctores,
        'doctores_pendientes': doctores_pendientes,
        'doctores_verificados': doctores_verificados,
        'total_pacientes': total_pacientes,
        'doctores_no_verificados': doctores_no_verificados,
        'doctores_verificados_lista': doctores_verificados_lista,
    }
    
    return render(request, 'agendamiento/admin_dashboard.html', context)

@staff_member_required
def verificar_doctor(request, doctor_id):
    """Vista para verificar un doctor"""
    if request.method == 'POST':
        try:
            doctor = Doctor.objects.get(id=doctor_id)
            doctor.verificado = True
            doctor.activo = True
            doctor.save()
            
            # Enviar correo de notificación al doctor
            # TODO: Implementar envío de correo
            
            return JsonResponse({
                'success': True,
                'message': 'Doctor verificado exitosamente'
            })
        except Doctor.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Doctor no encontrado'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al verificar doctor: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    }, status=405)

@staff_member_required
def rechazar_doctor(request, doctor_id):
    """Vista para rechazar la solicitud de un doctor"""
    if request.method == 'POST':
        try:
            doctor = Doctor.objects.get(id=doctor_id)
            # Eliminar documentos
            if doctor.documento_licencia:
                doctor.documento_licencia.delete()
            if doctor.certificacion_1:
                doctor.certificacion_1.delete()
            if doctor.certificacion_2:
                doctor.certificacion_2.delete()
            if doctor.certificacion_3:
                doctor.certificacion_3.delete()
            
            # Eliminar usuario y doctor
            user = doctor.user
            doctor.delete()
            user.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Doctor rechazado exitosamente'
            })
        except Doctor.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Doctor no encontrado'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    }, status=405)

@staff_member_required
def toggle_estado_doctor(request, doctor_id):
    """Vista para activar/desactivar un doctor"""
    if request.method == 'POST':
        try:
            doctor = Doctor.objects.get(id=doctor_id)
            doctor.activo = not doctor.activo
            doctor.save()
            
            estado = "activado" if doctor.activo else "desactivado"
            return JsonResponse({
                'success': True,
                'message': f'Doctor {estado} exitosamente'
            })
        except Doctor.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Doctor no encontrado'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al cambiar estado: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    }, status=405)