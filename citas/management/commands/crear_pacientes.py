from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from citas.models import Paciente
from django.utils.crypto import get_random_string
from datetime import date

class Command(BaseCommand):
    help = 'Crea pacientes de ejemplo'

    def handle(self, *args, **kwargs):
        # Lista de pacientes a crear
        pacientes = [
            {
                'nombre': 'Ana',
                'apellido': 'García',
                'fecha_nacimiento': date(1990, 5, 15),
            },
            {
                'nombre': 'Carlos',
                'apellido': 'Martínez',
                'fecha_nacimiento': date(1985, 8, 22),
            },
            {
                'nombre': 'María',
                'apellido': 'López',
                'fecha_nacimiento': date(1995, 3, 10),
            }
        ]

        for paciente_data in pacientes:
            # Crear usuario
            username = f"{paciente_data['nombre'].lower()}.{paciente_data['apellido'].lower()}"
            email = f"{username}@example.com"
            password = get_random_string(10)
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=paciente_data['nombre'],
                last_name=paciente_data['apellido']
            )

            # Crear paciente
            paciente = Paciente.objects.create(
                user=user,
                fecha_nacimiento=paciente_data['fecha_nacimiento'],
                telefono=f"555-{get_random_string(4, '0123456789')}"
            )

            self.stdout.write(self.style.SUCCESS(
                f'Creado paciente: {paciente_data["nombre"]} {paciente_data["apellido"]}\n'
                f'Username: {username}\n'
                f'Password: {password}\n'
                f'----------------------------------'
            )) 