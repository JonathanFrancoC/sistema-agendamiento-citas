from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta, time
import pytz

def documento_licencia_path(instance, filename):
    # Obtener la extensión del archivo original
    ext = filename.split('.')[-1]
    # Generar el nuevo nombre del archivo
    return f'documentos_doctores/{instance.id}/licencia.{ext}'

def certificacion_path(instance, filename):
    # Obtener el número de certificación del nombre del campo
    field_name = filename.split('/')[-1].split('.')[0]
    num = field_name.split('_')[-1]
    # Obtener la extensión del archivo original
    ext = filename.split('.')[-1]
    # Generar el nuevo nombre del archivo
    return f'documentos_doctores/{instance.id}/certificacion_{num}.{ext}'

class Doctor(models.Model):
    ESPECIALIDADES = [
        ('medicina_general', 'Medicina General'),
        ('pediatria', 'Pediatría'),
        ('cardiologia', 'Cardiología'),
        ('dermatologia', 'Dermatología'),
        ('ginecologia', 'Ginecología'),
        ('oftalmologia', 'Oftalmología'),
        ('psiquiatria', 'Psiquiatría'),
        ('traumatologia', 'Traumatología')
    ]

    DIAS_SEMANA = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    especialidad = models.CharField(max_length=100, choices=ESPECIALIDADES)
    telefono = models.CharField(max_length=20)
    activo = models.BooleanField(default=False)
    verificado = models.BooleanField(default=False)
    numero_licencia = models.CharField(max_length=50, unique=True)
    fecha_verificacion = models.DateTimeField(null=True, blank=True)
    documento_licencia = models.FileField(upload_to=documento_licencia_path, null=True, blank=True)
    certificacion_1 = models.FileField(upload_to=certificacion_path, null=True, blank=True)
    certificacion_2 = models.FileField(upload_to=certificacion_path, null=True, blank=True)
    certificacion_3 = models.FileField(upload_to=certificacion_path, null=True, blank=True)
    hora_inicio = models.TimeField(default=time(8, 0))  # 8:00 AM
    hora_fin = models.TimeField(default=time(17, 0))    # 5:00 PM
    dias_laborables = models.CharField(max_length=13, default='0,1,2,3,4')  # Lunes a Viernes por defecto
    duracion_cita = models.IntegerField(default=30, help_text="Duración de la cita en minutos")

    def clean(self):
        if self.activo and not self.verificado:
            raise ValidationError('Un doctor no verificado no puede estar activo')

    def save(self, *args, **kwargs):
        if not self.verificado:
            self.activo = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_especialidad_display()}"

    def get_dias_laborables(self):
        return [int(dia) for dia in self.dias_laborables.split(',') if dia]

    def trabaja_en_fecha(self, fecha):
        # Convertir el día de la semana de Python (0=Lunes) a nuestro formato
        dia_semana = fecha.weekday()
        dias_laborables = self.get_dias_laborables()
        print(f"Verificando día {dia_semana} (fecha: {fecha}) contra días laborables: {dias_laborables}")
        return dia_semana in dias_laborables

    def get_horarios_disponibles(self, fecha):
        # Si no es un día laborable, retornar lista vacía
        if not isinstance(fecha, datetime):
            try:
                fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                return []

        if not self.trabaja_en_fecha(fecha):
            print(f"El doctor no trabaja en la fecha {fecha}")
            return []

        horarios = []
        ahora = timezone.localtime(timezone.now())
        
        # Generar horarios cada 30 minutos
        hora_actual = datetime.combine(fecha, self.hora_inicio)
        hora_fin = datetime.combine(fecha, self.hora_fin)
        
        # Obtener citas existentes para ese día
        citas_existentes = Cita.objects.filter(
            doctor=self,
            fecha__date=fecha,
            estado='pendiente'
        ).values_list('fecha', flat=True)
        
        # Convertir las horas de las citas a set para búsqueda más eficiente
        horas_ocupadas = {cita.astimezone(ahora.tzinfo).strftime('%H:%M') for cita in citas_existentes}
        
        while hora_actual < hora_fin:
            hora_str = hora_actual.strftime('%H:%M')
            
            # Si es el día actual, verificar si la hora ya pasó
            es_pasado = False
            if fecha == ahora.date():
                hora_actual_aware = timezone.make_aware(hora_actual)
                es_pasado = hora_actual_aware <= ahora
            
            # Solo agregar el horario si no ha pasado y no está ocupado
            if not es_pasado:
                esta_ocupado = hora_str in horas_ocupadas
                horarios.append({
                    'hora': hora_str,
                    'disponible': not esta_ocupado,
                    'ocupado': esta_ocupado
                })
            
            hora_actual += timedelta(minutes=30)
        
        return horarios

    class Meta:
        verbose_name = "Doctor"
        verbose_name_plural = "Doctores"

class HorarioDoctor(models.Model):
    doctor = models.ForeignKey(Doctor, related_name='horarios', on_delete=models.CASCADE)
    dia_semana = models.IntegerField(choices=Doctor.DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    
    class Meta:
        ordering = ['dia_semana', 'hora_inicio']
        unique_together = ['doctor', 'dia_semana']

    def clean(self):
        if self.hora_inicio >= self.hora_fin:
            raise ValidationError(_('La hora de inicio debe ser anterior a la hora de fin'))

    def __str__(self):
        return f"{self.doctor} - {self.get_dia_semana_display()} ({self.hora_inicio} - {self.hora_fin})"

class Paciente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    direccion = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"

class Cita(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
        ('expirada', 'Expirada'),
    )
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    fecha = models.DateTimeField()
    motivo = models.TextField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    notas = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cita con {self.doctor.user.get_full_name()} - {self.fecha}"

    def save(self, *args, **kwargs):
        # Verificar si la cita ya pasó
        if self.fecha < timezone.now():
            if self.estado == 'pendiente':
                self.estado = 'expirada'
        super().save(*args, **kwargs)

    @property
    def ha_pasado(self):
        """Determina si la cita ya pasó"""
        return self.fecha < timezone.now()

    @property
    def estado_display(self):
        """Retorna el estado para mostrar, considerando si la cita ya pasó"""
        if self.ha_pasado and self.estado == 'pendiente':
            return 'Expirada'
        return self.get_estado_display()

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'
