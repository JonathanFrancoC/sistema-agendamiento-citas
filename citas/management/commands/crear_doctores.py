from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from citas.models import Doctor
from django.utils import timezone

class Command(BaseCommand):
    help = 'Crea doctores de prueba'

    def handle(self, *args, **kwargs):
        # Lista de doctores a crear
        doctores = [
            {
                'username': 'dr.garcia',
                'first_name': 'Juan',
                'last_name': 'García',
                'email': 'dr.garcia@example.com',
                'especialidad': 'Cardiología',
                'telefono': '555-0101',
                'numero_licencia': 'MED001',
                'dias_trabajo': '0,1,2,3,4',  # Lunes a Viernes
                'hora_inicio': '08:00',
                'hora_fin': '17:00'
            },
            {
                'username': 'dra.rodriguez',
                'first_name': 'María',
                'last_name': 'Rodríguez',
                'email': 'dra.rodriguez@example.com',
                'especialidad': 'Pediatría',
                'telefono': '555-0102',
                'numero_licencia': 'MED002',
                'dias_trabajo': '0,1,2,3,4',  # Lunes a Viernes
                'hora_inicio': '09:00',
                'hora_fin': '18:00'
            },
            {
                'username': 'dr.lopez',
                'first_name': 'Carlos',
                'last_name': 'López',
                'email': 'dr.lopez@example.com',
                'especialidad': 'Dermatología',
                'telefono': '555-0103',
                'numero_licencia': 'MED003',
                'dias_trabajo': '1,3,5',  # Martes, Jueves, Sábado
                'hora_inicio': '10:00',
                'hora_fin': '19:00'
            }
        ]

        for doctor_data in doctores:
            try:
                # Crear usuario
                user = User.objects.create_user(
                    username=doctor_data['username'],
                    email=doctor_data['email'],
                    password='doctor123',  # Contraseña temporal
                    first_name=doctor_data['first_name'],
                    last_name=doctor_data['last_name']
                )

                # Crear perfil de doctor
                doctor = Doctor.objects.create(
                    user=user,
                    especialidad=doctor_data['especialidad'],
                    telefono=doctor_data['telefono'],
                    numero_licencia=doctor_data['numero_licencia'],
                    verificado=True,
                    activo=True,
                    fecha_verificacion=timezone.now(),
                    dias_trabajo=doctor_data['dias_trabajo'],
                    hora_inicio=doctor_data['hora_inicio'],
                    hora_fin=doctor_data['hora_fin']
                )

                self.stdout.write(self.style.SUCCESS(
                    f'Doctor creado exitosamente: {doctor.user.get_full_name()}'
                ))

            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'Error al crear doctor {doctor_data["username"]}: {str(e)}'
                )) 