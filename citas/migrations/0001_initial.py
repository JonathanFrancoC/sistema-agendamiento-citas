# Generated by Django 5.2 on 2025-04-04 15:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('especialidad', models.CharField(max_length=100)),
                ('telefono', models.CharField(max_length=20)),
                ('activo', models.BooleanField(default=True)),
                ('verificado', models.BooleanField(default=False)),
                ('numero_licencia', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('fecha_verificacion', models.DateTimeField(blank=True, null=True)),
                ('hora_inicio', models.TimeField(default='08:00')),
                ('hora_fin', models.TimeField(default='18:00')),
                ('dias_trabajo', models.CharField(default='0,1,2,3,4', max_length=50)),
                ('duracion_cita', models.IntegerField(default=30, help_text='Duración de la cita en minutos')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('verificado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='doctores_verificados', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Doctor',
                'verbose_name_plural': 'Doctores',
            },
        ),
        migrations.CreateModel(
            name='Paciente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telefono', models.CharField(max_length=20)),
                ('fecha_nacimiento', models.DateField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HorarioDoctor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia_semana', models.IntegerField(choices=[(0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), (3, 'Jueves'), (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo')])),
                ('hora_inicio', models.TimeField()),
                ('hora_fin', models.TimeField()),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='horarios', to='citas.doctor')),
            ],
            options={
                'ordering': ['dia_semana', 'hora_inicio'],
                'unique_together': {('doctor', 'dia_semana')},
            },
        ),
        migrations.CreateModel(
            name='Cita',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('hora', models.TimeField()),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('confirmada', 'Confirmada'), ('cancelada', 'Cancelada'), ('completada', 'Completada')], default='pendiente', max_length=20)),
                ('notas', models.TextField(blank=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('motivo', models.CharField(blank=True, max_length=200)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='citas', to='citas.doctor')),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='citas', to='citas.paciente')),
            ],
            options={
                'ordering': ['fecha', 'hora'],
                'unique_together': {('doctor', 'fecha', 'hora')},
            },
        ),
    ]
