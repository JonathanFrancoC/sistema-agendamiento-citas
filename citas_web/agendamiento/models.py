from django.db import models
from django.contrib.auth.models import User

class Doctor(models.Model):
    nombre = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre} - {self.especialidad}"

class Appointment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient_name = models.CharField(max_length=100)
    date = models.DateTimeField()
    reason = models.TextField()

    def __str__(self):
        return f"{self.patient_name} - {self.date}"

class Cita(models.Model):
    doctor = models.CharField(max_length=100)  # Nombre del doctor
    especialidad = models.CharField(max_length=100)  # Especialidad médica
    fecha = models.DateTimeField()  # Fecha y hora de la cita
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    disponible = models.BooleanField(default=True)  # Disponibilidad de la cita

    def __str__(self):
        return f"{self.doctor} - {self.especialidad} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"


    def __str__(self):
        estado = "Disponible" if self.disponible else f"Ocupada por {self.usuario}"
        return f"{self.doctor} - {self.fecha_hora} - {estado}"