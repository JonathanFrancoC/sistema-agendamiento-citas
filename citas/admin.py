from django.contrib import admin
from .models import Doctor, Paciente, Cita, HorarioDoctor

class HorarioDoctorInline(admin.TabularInline):
    model = HorarioDoctor
    extra = 1

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('get_nombre_completo', 'especialidad', 'telefono', 'activo', 'verificado')
    list_filter = ('especialidad', 'activo', 'verificado')
    search_fields = ('user__first_name', 'user__last_name', 'especialidad')
    inlines = [HorarioDoctorInline]

    def get_nombre_completo(self, obj):
        return obj.user.get_full_name()
    get_nombre_completo.short_description = 'Nombre'

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('get_nombre_completo', 'telefono', 'fecha_nacimiento')
    search_fields = ('user__first_name', 'user__last_name', 'telefono')

    def get_nombre_completo(self, obj):
        return obj.user.get_full_name()
    get_nombre_completo.short_description = 'Nombre'

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'paciente', 'fecha', 'estado')
    list_filter = ('estado', 'fecha')
    search_fields = ('doctor__user__first_name', 'doctor__user__last_name', 
                    'paciente__user__first_name', 'paciente__user__last_name')
    date_hierarchy = 'fecha'

@admin.register(HorarioDoctor)
class HorarioDoctorAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'get_dia_semana_display', 'hora_inicio', 'hora_fin')
    list_filter = ('dia_semana', 'doctor__especialidad')
    search_fields = ('doctor__user__first_name', 'doctor__user__last_name')
