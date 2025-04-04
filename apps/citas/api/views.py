from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import Doctor, Paciente, Cita

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Registro de nuevos usuarios vía API
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
    
    return Response({
        'status': 'success',
        'message': 'Usuario registrado exitosamente',
        'data': {
            'user': {
                'username': user.username,
                'email': user.email,
                'tipo': tipo
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }
        }
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Login de usuarios vía API
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
    
    return Response({
        'status': 'success',
        'data': {
            'user': {
                'username': user.username,
                'email': user.email
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_citas(request):
    """
    Lista las citas del usuario autenticado vía API
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
    Crea una nueva cita vía API
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