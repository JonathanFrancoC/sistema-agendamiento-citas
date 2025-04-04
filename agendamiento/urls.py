from django.urls import path
from . import views

app_name = 'agendamiento'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('verificar-doctor/<int:doctor_id>/', views.verificar_doctor, name='verificar_doctor'),
    path('rechazar-doctor/<int:doctor_id>/', views.rechazar_doctor, name='rechazar_doctor'),
    path('toggle-estado-doctor/<int:doctor_id>/', views.toggle_estado_doctor, name='toggle_estado_doctor'),
    path('agendar-cita/', views.agendar_cita, name='agendar_cita'),
    path('mis-citas/', views.mis_citas, name='mis_citas'),
    path('confirmar-cita/<int:cita_id>/', views.confirmar_cita, name='confirmar_cita'),
    path('cancelar-cita/<int:cita_id>/', views.cancelar_cita, name='cancelar_cita'),
    path('cambiar-estado-cita/<int:cita_id>/', views.cambiar_estado_cita, name='cambiar_estado_cita'),
    path('get-horarios-disponibles/', views.get_horarios_disponibles, name='get_horarios_disponibles'),
    
    # API endpoints
    path('api/register/', views.register_user, name='api_register'),
    path('api/login/', views.login_user, name='api_login'),
    path('api/logout/', views.logout_user, name='api_logout'),
    path('api/profile/', views.get_user_profile, name='api_profile'),
    path('api/citas/', views.get_user_citas, name='api_citas'),
]